ç#!/bin/bash
source ~/venv/bin/activate

# Capturamos el T0
T0=$(date +%s.%N)

#Cargamos el numero de prompts especificados en bash en paralelo
for ((i=1; i<=$1; i++))
do
python3 ../model_init_random.py $i $T0 &
done

# Esperamos a que todos los procesos de fondo terminen
wait
#Imprimimos que se ha acabado el proceso
echo "Todas las llamadas finalizadas."
