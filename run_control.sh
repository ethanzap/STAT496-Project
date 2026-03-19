python -m src.main --texts_dir data/control_articles --user_model gpt-5-mini --llm_model gpt-5-mini --output_file output_5_5_c.json
python utils/plot_alignment_trajectory.py --input_file output_5_5_c.json --output_dir plots_5_5_c

python -m src.main --texts_dir data/control_articles --user_model gpt-5-mini --llm_model gemma --output_file output_5_g_c.json
python utils/plot_alignment_trajectory.py --input_file output_5_g_c.json --output_dir plots_5_g_c

python -m src.main --texts_dir data/control_articles --user_model gpt-5-mini --llm_model llama --output_file output_5_l_c.json
python utils/plot_alignment_trajectory.py --input_file output_5_l_c.json --output_dir plots_5_l_c

python -m src.main --texts_dir data/control_articles --user_model gemma --llm_model gpt-5-mini --output_file output_g_5_c.json
python utils/plot_alignment_trajectory.py --input_file output_g_5_c.json --output_dir plots_g_5_c

python -m src.main --texts_dir data/control_articles --user_model gemma --llm_model gemma --output_file output_g_g_c.json
python utils/plot_alignment_trajectory.py --input_file output_g_g_c.json --output_dir plots_g_g_c

python -m src.main --texts_dir data/control_articles --user_model gemma --llm_model llama --output_file output_g_l_c.json
python utils/plot_alignment_trajectory.py --input_file output_g_l_c.json --output_dir plots_g_l_c

python -m src.main --texts_dir data/control_articles --user_model llama --llm_model gpt-5-mini --output_file output_l_5_c.json
python utils/plot_alignment_trajectory.py --input_file output_l_5_c.json --output_dir plots_l_5_c

python -m src.main --texts_dir data/control_articles --user_model llama --llm_model gemma --output_file output_l_g_c.json
python utils/plot_alignment_trajectory.py --input_file output_l_g_c.json --output_dir plots_l_g_c

python -m src.main --texts_dir data/control_articles --user_model llama --llm_model llama --output_file output_l_l_c.json
python utils/plot_alignment_trajectory.py --input_file output_l_l_c.json --output_dir plots_l_l_c