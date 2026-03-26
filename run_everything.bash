#!/bin/bash


#Activamos el virtual environment
source ~/venv/bin/activate


MODELO=$1

# Cogemos las listas de argumentos que pasamos desde CLI y las fromateamos de manera en que podemos iterar a traves de ellas
IFS=',' read -r -a MAX_LENS <<< "$2"
IFS=',' read -r -a MAX_SEQS <<< "$3"
IFS=',' read -r -a NUM_PROMPTS <<< "$4"

# Creamos bucles para iterar a traves de todas las configuraciones possibles entre los argumentos definidos
for MLEN in "${MAX_LENS[@]}"; do
  for MSEQ in "${MAX_SEQS[@]}"; do
    for NPROMPT in "${NUM_PROMPTS[@]}"; do
      DIR_NAME="run_${MLEN}_${MSEQ}_${NPROMPT}" 
    
      mkdir "$DIR_NAME" 
      cd "$DIR_NAME" 
      

      # Inicializamos el modelo
      echo "Iniciando servidor vLLM en segundo plano..."
      vllm serve "$MODELO" \
        --gpu-memory-utilization 0.75 \
        --max-model-len "$MLEN" \
        --max-num-seqs "$MSEQ" \
        --optimization-level 3 \
        --max-logprobs -1 \
        --stream-interval 10 \
        --enable-mfu-metrics \
        --host 0.0.0.0 \
        --port 8000 &
      
      VLLM_PID=$!

      # Esperamos a que el modelo este inicializado
      while ! curl -s http://localhost:8000/health > /dev/null; do
        sleep 5
      done
      

      # Iniciar recolectores de métricas, les pasamos tambien los parametros con los que se estan ejecutando para poder modificar el nombre de los arxivos
      # A los que se guardan los datos, de esta manera evitamos que se sobreescriban datos constantemente
      python3 ../vllm_max_metrics.py "$NPROMPT" "$MLEN" "$MSEQ" &
      MAX_METRICS_PID=$!
      
      python3 ../collect_latency_metrics.py "$NPROMPT" "$MLEN" "$MSEQ" &
      LATENCY_PID=$!
      
      python3 ../vllm_collect_metrics_csv.py "$NPROMPT" "$MLEN" "$MSEQ" &
      METRICS_PID=$!

      # Cargar los prompts
      bash ../my_Script1.bash "$NPROMPT"

      # Matar recolectores
      kill $LATENCY_PID $METRICS_PID $MAX_METRICS_PID

      # Generar gráficos y recoger parametros de la ejecucion para poder replicarla en condiciones identicas
      python3 ../graph_gen_from_csv.py "$NPROMPT" "$MLEN" "$MSEQ" 
      python3 ../latency_graph_gen_from_csv.py "$NPROMPT" "$MLEN" "$MSEQ" 
      python3 ../model_params_dump.py "$NPROMPT" "$MLEN" "$MSEQ" 

      # Matar el modelo antes de la siguiente iteración
      echo "Finalizando servidor vLLM..."
      kill $VLLM_PID
      cd ..
      
      # Esperar a que el puerto se libere completamente
      sleep 10
      
    done
  done
done
#Escribir un mensaje en la CLI cuando toda la ejecucion este finalizada, dado que puede ser confuso
echo "Toda la ejecución en lote ha finalizado."