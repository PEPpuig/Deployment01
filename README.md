# Deployment01
**Orden de ejecución:**
bash run_everything.bash modelo max_model_lengths max_num_seqs num_prompts speculative-config

**Ejemplo de ejecución:**
bash run_everything.bash Qwen/Qwen3-2B "512,1024" "8,16" "64" 'None|{"model": "Qwen/Qwen3-0.6B", "num_speculative_tokens": 5, "method": "draft_model"}'
