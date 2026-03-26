import pandas as pd
import matplotlib.pyplot as plt
import sys

# Definir nombres dinámicos tanto para el CSV de donde leemos los datos como para la Imagen de salida
if len(sys.argv) >= 4:
    n_prompts = sys.argv[1]
    m_len = sys.argv[2]
    m_seq = sys.argv[3]
    CSV_PATH = f"vllm_latency_metrics_{n_prompts}_{m_len}_{m_seq}.csv"
    PNG_PATH = f"vllm_grafico_latency_{n_prompts}_{m_len}_{m_seq}.png"
    # Definimos el titulo del plot de manera dinamica tambien
    PLOT_TITLE = f'vLLM: Requests vs Latencies vs KV Cache (Prompts:{n_prompts}, Len:{m_len}, Seqs:{m_seq})'
else:
    CSV_PATH = "vllm_latency_metrics.csv"
    PNG_PATH = "vllm_grafico_latency.png"
    PLOT_TITLE = 'vLLM: Requests vs Latencies vs KV Cache Usage'

# Leer datos del archivo CSV
df = pd.read_csv(CSV_PATH)
print(f"Datos cargados: {len(df)} filas desde {CSV_PATH}")

# Crear figura un poco más ancha para que quepan todos los ejes
fig, ax1 = plt.subplots(figsize=(15, 7))

# Ajustar el margen derecho para que los ejes adicionales no se recorten en la vista previa
fig.subplots_adjust(right=0.75)

# Eje izquierdo: requests (ROJO running)
line1 = ax1.plot(df['t_rel'], df['num_reqs_running'], 'r-o', markersize=4, linewidth=2, label='num reqs run')
ax1.set_xlabel('Tiempo relativo (s)')
ax1.set_ylabel('Número de requests', color='red')
ax1.tick_params(axis='y', labelcolor='red')
ax1.grid(True, alpha=0.3)

# Eje derecho 1 (ax2): e2e_latency (NEGRO)
ax2 = ax1.twinx()
line2 = ax2.plot(df['t_rel'], df['e2e_latency'], 'k-o', markersize=4, linewidth=2, label='e2e_latency (s)')
ax2.set_ylabel('e2e_latency (s)', color='black')
ax2.tick_params(axis='y', labelcolor='black')

# Eje derecho 2 (ax3) para KV Cache % (VERDE)
ax3 = ax1.twinx()
# Mover el tercer eje 60 puntos hacia la derecha
ax3.spines['right'].set_position(('outward', 60))
line3 = ax3.plot(df['t_rel'], df['kv_cache_perc'], 'g-o', markersize=4, linewidth=2, label='kv cache usage')
ax3.set_ylabel('KV Cache %', color='green')
ax3.tick_params(axis='y', labelcolor='green')
ax3.set_ylim(0, 1)

# Eje derecho 3 (ax4) para Inter Token Latency (NARANJA)
ax4 = ax1.twinx()
# Mover el cuarto eje 120 puntos hacia la derecha para no superponerse con el ax3
ax4.spines['right'].set_position(('outward', 120))
line4 = ax4.plot(df['t_rel'], df['Inter_Token_Latency'], color='darkorange', marker='s', linestyle='-', markersize=4, linewidth=2, label='inter_token_lat')
ax4.set_ylabel('Inter Token Latency', color='darkorange')
ax4.tick_params(axis='y', labelcolor='darkorange')

#Titulo dinamico del plot y la leyenda
plt.title(PLOT_TITLE)
lines = line1 + line2 + line3 + line4
labels = [l.get_label() for l in lines]
fig.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05),
           ncol=4, fontsize=10, frameon=False)


# Guardar la imagen con el nombre dinámico
plt.savefig(PNG_PATH, dpi=300, bbox_inches='tight')

print(f"¡Gráfico de latencia guardado exitosamente como '{PNG_PATH}'!")
