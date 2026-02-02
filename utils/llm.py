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
    "gpt-4.1"
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-4o",
    "gpt-4o-mini"
]
MODEL_COSTS = {
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60)
}

def get_model(model):
    load_dotenv()
    
    # return AsyncOpenAI(
    #     api_key=os.environ["OPENAI_API_KEY"],
    #     timeout=None
    # )
    client = AsyncAzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_4_1_API_KEY"],
        api_version=os.environ["AZURE_OPENAI_4_1_API_VERSION"],
        azure_endpoint=os.environ["AZURE_OPENAI_4_1_ENDPOINT"],
        timeout=None
    )
    return LLM(client, model)

class LLM:
    def __init__(self, client, model):
        self.client = client
        self.model = model
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def chat_completion(self, messages, *args, **kwargs):
        await self.semaphore.acquire()

        try:
            for _ in range(MAX_RETRY):
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        *args,
                        **kwargs
                    )
                except RateLimitError:
                    await asyncio.sleep(TIMEOUT)
                    continue
                except Exception as e:
                    warnings.warn(repr(e))
                    return None
                if len(response.choices) == 0 or response.choices[0].message.content is None:
                    warnings.warn("Invalid output from chat_completion")
                    return None
                else:
                    self.prompt_tokens += response.usage.prompt_tokens
                    self.completion_tokens += response.usage.completion_tokens
                    return response.choices[0].message.content
        except Exception as e:
            warnings.warn(repr(e))
            return None
        finally:
            self.semaphore.release()
    
    def cost(self):
        return self.prompt_tokens / 1e6 * MODEL_COSTS[self.model][0] + self.completion_tokens / 1e6 * MODEL_COSTS[self.model][1]