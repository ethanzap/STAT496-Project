python -m src.main --user_model gpt-5-mini --llm_model gpt-5-mini --output_file output_5_5.json
python utils/plot_alignment_trajectory.py --input_file output_5_5.json --output_dir plots_5_5

python -m src.main --user_model gpt-5-mini --llm_model gemma --output_file output_5_g.json
python utils/plot_alignment_trajectory.py --input_file output_5_g.json --output_dir plots_5_g

python -m src.main --user_model gpt-5-mini --llm_model llama --output_file output_5_l.json
python utils/plot_alignment_trajectory.py --input_file output_5_l.json --output_dir plots_5_l

python -m src.main --user_model gemma --llm_model gpt-5-mini --output_file output_g_5.json
python utils/plot_alignment_trajectory.py --input_file output_g_5.json --output_dir plots_g_5

python -m src.main --user_model gemma --llm_model gemma --output_file output_g_g.json
python utils/plot_alignment_trajectory.py --input_file output_g_g.json --output_dir plots_g_g

python -m src.main --user_model gemma --llm_model llama --output_file output_g_l.json
python utils/plot_alignment_trajectory.py --input_file output_g_l.json --output_dir plots_g_l

python -m src.main --user_model llama --llm_model gpt-5-mini --output_file output_l_5.json
python utils/plot_alignment_trajectory.py --input_file output_l_5.json --output_dir plots_l_5

python -m src.main --user_model llama --llm_model gemma --output_file output_l_g.json
python utils/plot_alignment_trajectory.py --input_file output_l_g.json --output_dir plots_l_g

python -m src.main --user_model llama --llm_model llama --output_file output_l_l.json
python utils/plot_alignment_trajectory.py --input_file output_l_l.json --output_dir plots_l_l