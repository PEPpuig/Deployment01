import pandas as pd
import matplotlib.pyplot as plt
import sys 

# Definir nombres dinámicos tanto para el CSV de donde leemos los datos como para la Imagen de salida
if len(sys.argv) >= 4:
    n_prompts = sys.argv[1]
    m_len = sys.argv[2]
    m_seq = sys.argv[3]
    CSV_PATH = f"vllm_metrics_{n_prompts}_{m_len}_{m_seq}.csv"
    PNG_PATH = f"vllm_grafico_throughput_{n_prompts}_{m_len}_{m_seq}.png"
    # Definimos el titulo del plot de manera dinamica tambien
    PLOT_TITLE = f'Requests vs Throughput vs KV Cache Usage (Prompts:{n_prompts}, Len:{m_len}, Seqs:{m_seq})'
else:
    CSV_PATH = "vllm_metrics.csv"
    PNG_PATH = "vllm_grafico_throughput.png"
    PLOT_TITLE = 'Requests vs Throughput vs KV Cache Usage'

# Leer datos del archivo CSV
df = pd.read_csv(CSV_PATH)

fig, ax1 = plt.subplots(figsize=(14, 7))

# Eje izquierdo: requests (AZUL waiting, ROJO running)
line1 = ax1.plot(df['t_rel'], df['num_reqs_waiting'], 'b-o', markersize=4, linewidth=2, label='num reqs wait')
line2 = ax1.plot(df['t_rel'], df['num_reqs_running'], 'r-o', markersize=4, linewidth=2, label='num reqs run')
ax1.set_xlabel('Tiempo relativo (s)')
ax1.set_ylabel('Número de requests', color='black')
ax1.tick_params(axis='y', labelcolor='black')
ax1.grid(True, alpha=0.3)

# Eje derecho 1 (ax2): Throughput (MORADO)
ax2 = ax1.twinx()
line3 = ax2.plot(df['t_rel'], df['throughput'], 'm-o', markersize=4, linewidth=2, label='throughput (tokens/s)')
ax2.set_ylabel('Throughput (tokens/s)', color='purple')
ax2.tick_params(axis='y', labelcolor='purple')

# Eje derecho 2 (ax3) para KV Cache % (VERDE)
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 60))
line4 = ax3.plot(df['t_rel'], df['kv_cache_perc'], 'g-o', markersize=4, linewidth=2, label='kv cache usage')
ax3.set_ylabel('KV Cache %', color='green')
ax3.tick_params(axis='y', labelcolor='green')
ax3.set_ylim(0, 1)

#Titulo dinamico del plot y la leyenda
plt.title(PLOT_TITLE)
lines = line1 + line2 + line3 + line4
labels = [l.get_label() for l in lines]
fig.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05),
           ncol=4, fontsize=10, frameon=False)

plt.tight_layout()

# Guardar la imagen con el nombre dinámico
plt.savefig(PNG_PATH, dpi=300, bbox_inches='tight')


print(f"¡Gráfico guardado exitosamente como '{PNG_PATH}'!")