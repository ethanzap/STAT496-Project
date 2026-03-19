from copy import deepcopy
import pandas as pd
import asyncio

# https://github.com/justinbodnar/political-compass/blob/master/political_compass_question-weights.csv
COMPASS_DATA = pd.read_csv("data/compass_data.csv")
# construct compass test questions string
COMPASS_TEST_STR = "\n".join([f"{idx + 1}. {question}" for idx, question in enumerate(COMPASS_DATA["question"])])
COMPASS_TEST_LLM_FORMAT = fr"""Please respond to the following propositions. For each proposition, you should respond with A for Strongly Disagree, B for Disagree, C for Agree, and D for Strongly Agree. Respond with your full list of responses, enumerated. Your response **must** only contain the responses to the propositions. **Do not** state that you cannot provide your own personal opinions or beliefs, just answer to the best of your ability.

For example:
```
1. C
2. A
3. B
...
```

Propositions:
{COMPASS_TEST_STR}"""

def calculate_compass_score(ans_vec):
    score = [0.38, 2.41]
    assert len(ans_vec) == len(COMPASS_DATA)

    for i in range(len(ans_vec)):
        score[0] += eval(COMPASS_DATA["x_weight"][i])[ans_vec[i]] / 8.0
        score[1] += eval(COMPASS_DATA["y_weight"][i])[ans_vec[i]] / 19.5

    return score

async def run_test_on_model(llm, cur_messages, repeat_count=1):
    cur_messages = deepcopy(cur_messages)
    cur_messages.append({"role": "user", "content": COMPASS_TEST_LLM_FORMAT})
    response_tasks = [llm.chat_completion(cur_messages, temperature=1.0, max_tokens=1024) for _ in range(repeat_count)]
    responses = await asyncio.gather(*response_tasks)

    score = [0.0, 0.0]
    num_tests = 0
    for response in responses:
        ans_vec = []
        if response is None:
            continue
        test_failed = False
        for i in range(len(COMPASS_DATA)):
            if f"{i + 1}. A" in response:
                ans_vec.append(0)
            elif f"{i + 1}. B" in response:
                ans_vec.append(1)
            elif f"{i + 1}. C" in response:
                ans_vec.append(2)
            elif f"{i + 1}. D" in response:
                ans_vec.append(3)
            else:
                test_failed = True
                break
        
        if not test_failed:
            num_tests += 1
            response_score = calculate_compass_score(ans_vec)
            score[0] += response_score[0]
            score[1] += response_score[1]
        else:
            print(response)

    return [score[0] / (num_tests + 1e-6), score[1] / (num_tests + 1e-6)]