CUDA_VISIBLE_DEVICES=0 python -m vllm.entrypoints.openai.api_server --port 8000 --model Meta-Llama-3.1-8B-Instruct --max-model-len 16384 --served-model-name llama &
CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server --port 8001 --model gemma-3-12b-it --max-model-len 16384 --language-model-only --served-model-name gemma &
