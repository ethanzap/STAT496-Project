import os
import asyncio
import warnings
from openai import (
    AsyncOpenAI,
    AsyncAzureOpenAI,
    RateLimitError,
)
from dotenv import load_dotenv

warnings.simplefilter("always")

MAX_CONCURRENT = 32
MAX_RETRY = 8
TIMEOUT = 5.0

MODELS = [
    "gpt-5-mini",
    "gemma",
    "llama"
]
MODEL_COSTS = {
    "gpt-5-mini": (0.25, 2.00),
    "llama": (0.0, 0.0),
    "gemma": (0.0, 0.0)
}

def get_model(model, gpu_id):
    load_dotenv()
    
    if model == "llama":
        client = AsyncOpenAI(base_url="http://localhost:"+str(os.environ["LLAMA_PORT"])+"/v1", api_key="", timeout=None)
    elif model == "gemma":
        client= AsyncOpenAI(base_url="http://localhost:"+str(os.environ["GEMMA_PORT"])+"/v1", api_key="", timeout=None)
    elif model == "gpt-5-mini":
        client = AsyncOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            timeout=None,
        )
    else:
        raise Exception()

    return LLM(client, model)

class LLM:
    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def chat_completion(self, messages, temperature=0.0, max_tokens=1024):
        await self.semaphore.acquire()

        try:
            for _ in range(MAX_RETRY):
                try:
                    if self.model == "gpt-5-mini":
                        response = await self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            max_completion_tokens=max_tokens,
                            reasoning_effort="minimal"
                        )
                    elif self.model == "llama" or self.model == "gemma":
                        response = await self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature
                        )
                    else:
                        raise Exception()
                except RateLimitError:
                    await asyncio.sleep(TIMEOUT)
                    continue
                except Exception as e:
                    warnings.warn(repr(e))
                    return ""
                if len(response.choices) == 0 or response.choices[0].message.content is None:
                    warnings.warn("Invalid output from chat_completion")
                    return ""
                else:
                    self.prompt_tokens += response.usage.prompt_tokens
                    self.completion_tokens += response.usage.completion_tokens
                    return response.choices[0].message.content
        except Exception as e:
            warnings.warn(repr(e))
            return ""
        finally:
            self.semaphore.release()
    
    def cost(self):
        return self.prompt_tokens / 1e6 * MODEL_COSTS[self.model][0] + self.completion_tokens / 1e6 * MODEL_COSTS[self.model][1]