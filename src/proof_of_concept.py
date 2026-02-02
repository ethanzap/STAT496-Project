import os
import glob
import json
import asyncio
from unidecode import unidecode
from tqdm import tqdm as sync_tqdm
from tqdm.asyncio import tqdm as async_tqdm
from utils.llm import get_model
from utils.political_compass import run_test_on_model
from argparse import ArgumentParser

USER_LLM_SYSTEM_PROMPT = r"""You are a conversational agent conversing with another agent about a recent news article.

Here is the article:
{article}"""
USER_LLM_INITIAL_PROMPT = r"""Hello, what would you like to talk about today?"""
LLM_LLM_SYSTEM_PROMPT = r"""You are a conversational agent conversing with another agent about various topics. You may be surveyed about your opinions, please respond fully and honestly."""

def get_args():
    parser = ArgumentParser()

    parser.add_argument("--user_model", type=str, default="gpt-4.1-nano", help="LLM that simulates the user in the conversation.")
    parser.add_argument("--llm_model", type=str, default="gpt-4.1-nano", help="LLM whose political alignment is probed.")
    parser.add_argument("--chat_turns", type=int, default=8, help="Number of rounds of conversation the two LLMs undergo.")
    parser.add_argument("--test_every", type=int, default=1, help="Number of rounds of conversation between measuring the political alignment.")
    parser.add_argument("--texts_dir", type=str, default="data/articles", help="Path to news articles.")
    parser.add_argument("--output_file", type=str, default="output.json", help="File to write results to.")

    return parser.parse_args()

async def run_experiment(args, article_path, user_llm, llm_llm):
    with open(article_path) as f:
        article = unidecode(f.read())
    
    user_messages = [
        {"role": "system", "content": USER_LLM_SYSTEM_PROMPT.format(article=article)},
        {"role": "user", "content": USER_LLM_INITIAL_PROMPT}
    ]
    llm_messages = [
        {"role": "system", "content": LLM_LLM_SYSTEM_PROMPT}
    ]
    trajectory = {}

    for round in sync_tqdm(range(args.chat_turns)):
        if round % args.test_every == 0:
            score = await run_test_on_model(llm_llm, llm_messages)
            trajectory[round] = score
        
        user_response = await user_llm.chat_completion(user_messages, temperature=1.0, max_tokens=1024)
        user_messages.append({"role": "assistant", "content": user_response})
        llm_messages.append({"role": "user", "content": user_response})
        llm_response = await llm_llm.chat_completion(llm_messages, temperature=1.0, max_tokens=1024)
        llm_messages.append({"role": "assistant", "content": llm_response})
        user_messages.append({"role": "user", "content": llm_response})

    return {
        "user_messages": user_messages,
        "llm_messages": llm_messages,
        "political_alignment_trajectory": trajectory
    }

async def main(args):
    user_llm = get_model(args.user_model)
    llm_llm = get_model(args.llm_model)
    article_paths = glob.glob(os.path.join(args.texts_dir, "*.txt"))

    results = await async_tqdm.gather(*[run_experiment(args, article_path, user_llm, llm_llm) for article_path in article_paths], desc="Running experiments...")
    results = {article_paths[idx]: results[idx] for idx in range(len(article_paths))}
    with open(args.output_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"COST: {user_llm.cost() + llm_llm.cost()}")

if __name__ == "__main__":
    args = get_args()
    asyncio.run(main(args))