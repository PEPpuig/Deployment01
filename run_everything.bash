#!/bin/bash

# Activamos el entorno virtual
source ~/venv/bin/activate

MODELO=$1

# Cogemos las listas de argumentos de la CLI y las formateamos
IFS=',' read -r -a MAX_LENS <<< "$2"
IFS=',' read -r -a MAX_SEQS <<< "$3"
IFS=',' read -r -a NUM_PROMPTS <<< "$4"

# Usamos el separador '|' (pipe) para las configuraciones especulativas
IFS='|' read -r -a SPEC_CONFIGS <<< "$5"

# Creamos bucles para iterar a través de todas las configuraciones posibles
for MLEN in "${MAX_LENS[@]}"; do
  for MSEQ in "${MAX_SEQS[@]}"; do
    for NPROMPT in "${NUM_PROMPTS[@]}"; do
      # Iteramos obteniendo el índice para poder generar nombres de carpeta seguros
      for S_IDX in "${!SPEC_CONFIGS[@]}"; do
        S_CONFIG="${SPEC_CONFIGS[$S_IDX]}"

        # Evitamos usar el JSON crudo en el nombre del directorio porque contiene
        # caracteres inválidos para rutas (/, {, }, ", espacios).
        if [ "$S_CONFIG" == "None" ]; then
          SAFE_CONFIG_NAME="None"
        else
          SAFE_CONFIG_NAME="Spec_${S_IDX}"
        fi

        DIR_NAME="run_${MLEN}_${MSEQ}_${NPROMPT}_${SAFE_CONFIG_NAME}" 
        
        # Creamos el directorio de la ejecución y entramos en él
        mkdir "$DIR_NAME" 
        cd "$DIR_NAME" 
        
        # Guardamos el JSON exacto en un archivo dentro de la carpeta para saber 
        # qué configuración se usó realmente en esta prueba
        echo "$S_CONFIG" > spec_config_utilizado.txt

        # Inicializamos el servidor vLLM en segundo plano
        echo "Iniciando servidor vLLM en segundo plano..."
        if [ "$S_CONFIG" == "None" ]; then
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
        else
          # Se pasa la variable envolviéndola en comillas dobles para respetar el JSON
          vllm serve "$MODELO" \
            --gpu-memory-utilization 0.75 \
            --max-model-len "$MLEN" \
            --max-num-seqs "$MSEQ" \
            --optimization-level 3 \
            --max-logprobs -1 \
            --stream-interval 10 \
            --enable-mfu-metrics \
            --host 0.0.0.0 \
            --speculative_config "$S_CONFIG" \
            --port 8000 &
        fi
        
        # Guardamos el PID del proceso de vLLM
        VLLM_PID=$!

        # Esperamos a que el modelo esté inicializado
        while ! curl -s http://localhost:8000/health > /dev/null; do
          sleep 5
        done
        
        # Iniciamos los recolectores de métricas
        # Pasamos SAFE_CONFIG_NAME en lugar del JSON para que los archivos de Python
        # también puedan generar archivos CSV/PNG con nombres de archivo válidos
        python3 ../vllm_max_metrics.py "$NPROMPT" "$MLEN" "$MSEQ" "$SAFE_CONFIG_NAME" &
        MAX_METRICS_PID=$!
        
        python3 ../collect_latency_metrics.py "$NPROMPT" "$MLEN" "$MSEQ" "$SAFE_CONFIG_NAME" &
        LATENCY_PID=$!
        
        python3 ../vllm_collect_metrics_csv.py "$NPROMPT" "$MLEN" "$MSEQ" "$SAFE_CONFIG_NAME" &
        METRICS_PID=$!

        # Cargamos los prompts
        bash ../my_Script1.bash "$NPROMPT"

        # Matamos los recolectores de métricas
        kill $LATENCY_PID $METRICS_PID $MAX_METRICS_PID

        # Generamos los gráficos y recogemos los parámetros
        python3 ../graph_gen_from_csv.py "$NPROMPT" "$MLEN" "$MSEQ" "$SAFE_CONFIG_NAME"
        python3 ../latency_graph_gen_from_csv.py "$NPROMPT" "$MLEN" "$MSEQ" "$SAFE_CONFIG_NAME"
        python3 ../model_params_dump.py "$NPROMPT" "$MLEN" "$MSEQ" "$SAFE_CONFIG_NAME"

        # Matamos el modelo antes de la siguiente iteración
        echo "Finalizando servidor vLLM..."
        kill $VLLM_PID
        
        # Salimos del directorio actual
        cd ..
        
        # Esperamos a que el puerto se libere completamente
        sleep 10
        
      done
    done
  done
done

echo "Toda la ejecución en lote ha finalizado."
