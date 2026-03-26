#!/usr/bin/env python3
import requests
import time
import re
import os
import csv
import sys

METRICS_URL = "http://localhost:8000/metrics"

# Leer argumentos pasados desde bash para ir modificando el nombre del arxivo donde guardar los resultados de manera dinamica
if len(sys.argv) >= 4:
    n_prompts = sys.argv[1]
    m_len = sys.argv[2]
    m_seq = sys.argv[3]
    CSV_FILENAME = f"vllm_metrics_{n_prompts}_{m_len}_{m_seq}.csv" 
else:
    CSV_FILENAME = "vllm_metrics.csv"
    
#Intervalos de muestreo, definidos para que los resultados se puedan apreciar correctamente
INTERVAL = 0.1
THROUGHPUT_INTERVAL = 0.15

start_time = time.time()

# Crear el archivo y la cabecera si no existe
if not os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['t_rel', 'num_reqs_running', 'num_reqs_waiting', 'kv_cache_perc', 'throughput'])

#Obtenemos los valores que nos interesan usando re.search
def get_value(lines, metric_substr):
    for line in lines:
        if metric_substr in line:
            match = re.search(r'\{[^}]+\}\s+([\d.e+-]+)', line)
            if match:
                return float(match.group(1))
    return 0.0

#Inicializacion de variables para el calculo de throughput
prev_tokens = 0
prev_time = time.time()
throughput = 0.0
prev_throughput = 0.0
iteration = 1.0

while True:
    try:
        resp = requests.get(METRICS_URL, timeout=2)
        lines = resp.text.splitlines()
#obtenemos las metricas que queremos
        running = get_value(lines, 'vllm:num_requests_running')
        waiting = get_value(lines, 'vllm:num_requests_waiting')
        kv_perc = get_value(lines, 'vllm:kv_cache_usage_perc')

        current_time = time.time()
        elapsed = current_time - prev_time

        if elapsed >= THROUGHPUT_INTERVAL:
            tokens_total = get_value(lines, 'vllm:generation_tokens_total')
            if prev_tokens > 0:
                throughput_total = (tokens_total - prev_tokens) / elapsed + prev_throughput
                throughput = (throughput_total)/iteration
                prev_tokens = tokens_total
            prev_time = current_time
            prev_throughput = throughput_total
            iteration = iteration +1

        t_rel = round(time.time() - start_time, 2)

#Guardamos los valores de las metricas con una precision de  decimales
        with open(CSV_FILENAME, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                t_rel,
                round(running, 5),
                round(waiting, 5),
                round(kv_perc, 5),
                round(throughput, 2)
            ])

    except Exception as e:
        # Silenciado opcionalmente para que no ensucie los logs si vLLM se apaga
        pass
#Dormimos el proceso durante el Intervalo de tiempo definido y se vuelve a ejecutar
    time.sleep(INTERVAL)