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
    CSV_FILENAME = f"vllm_latency_metrics_{n_prompts}_{m_len}_{m_seq}.csv"
else:
    CSV_FILENAME = "vllm_latency_metrics.csv"


#Intervalos de muestreo, definidos para que los resultados se puedan apreciar correctamente
INTERVAL = 0.1
THROUGHPUT_INTERVAL = 0.15

start_time = time.time()

# Crear el archivo y la cabecera si no existe
if not os.path.exists(CSV_FILENAME):
    with open(CSV_FILENAME, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['t_rel', 'num_reqs_running', 'Inter_Token_Latency', 'kv_cache_perc', 'e2e_latency'])

#Obtenemos los valores que nos interesan usando re.search
def get_value(lines, metric_substr):
    for line in lines:
        if metric_substr in line:
            match = re.search(r'\{[^}]+\}\s+([\d.e+-]+)', line)
            if match:
                return float(match.group(1))
    return 0.0


#Inicializacion de variables para el calculo de latency
iteration = 1.0
e2e_latency = 0.0

while True:
    try:
        resp = requests.get(METRICS_URL, timeout=2)
        lines = resp.text.splitlines()
#obtenemos las metricas que queremos
        running = get_value(lines, 'vllm:num_requests_running')
        Inter_Token_Latency = get_value(lines, 'vllm:inter_token_latency_seconds_sum')/iteration
        kv_perc = get_value(lines, 'vllm:kv_cache_usage_perc')
        e2e_latency_sum = get_value(lines, 'vllm:e2e_request_latency_seconds_sum')
        current_time = time.time()
        e2e_latency = (e2e_latency_sum) / iteration
        t_rel = round(time.time() - start_time, 2)
        iteration = iteration + 1

#Guardamos los valores de las metricas con una precision de  decimales
        with open(CSV_FILENAME, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                t_rel,
                round(running, 5),
                round(Inter_Token_Latency, 5),
                round(kv_perc, 5),
                round(e2e_latency_sum, 5)
            ])

    except Exception as e:
        # Silenciado opcionalmente para que no ensucie los logs si vLLM se apaga
        pass
#Dormimos el proceso durante el Intervalo de tiempo definido y se vuelve a ejecutar
    time.sleep(INTERVAL)