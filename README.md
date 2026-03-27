# Deployment01
**Orden de ejecución:**
bash run_everything.bash modelo max_model_lengths max_num_seqs num_prompts speculative-config

**Ejemplo de ejecución:**
bash run_everything.bash jinaai/reader-lm-0.5b "512,1024" "8,16" "64" 'None|{"model": "Qwen/Qwen3-0.6B", "num_speculative_tokens": 5, "method": "draft_model"}'
