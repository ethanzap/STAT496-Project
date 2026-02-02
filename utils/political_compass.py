from copy import deepcopy
import pandas as pd

# https://github.com/justinbodnar/political-compass/blob/master/political_compass_question-weights.csv
COMPASS_DATA = pd.read_csv("data/compass/political_compass_question-weights.csv")
ANS_CHOICE_WEIGHTS = {
    "strong_disagree": -1.0,
    "disagree": -0.5,
    "agree": 0.5,
    "strong_agree": 1.0
}
# construct compass test questions string
COMPASS_TEST_STR = "\n".join([f"{idx + 1}. {question}" for idx, question in enumerate(COMPASS_DATA["question"])])
COMPASS_TEST_LLM_FORMAT = fr"""Please provide your opinion on the following propositions. For each proposition, you should respond with A for Strongly Disagree, B for Disagree, C for Agree, and D for Strongly Agree. Respond with your full list of responses, enumerated.

For example:
```
1. [A, B, C, D]
2. [A, B, C, D]
...
```

Propositions:
{COMPASS_TEST_STR}"""

def calculate_compass_score(ans_vec):
    score = (0.0, 0.0)
    assert len(ans_vec) == len(COMPASS_DATA)

    for i in range(len(ans_vec)):
        disp = COMPASS_DATA["units"][i] * (1 if COMPASS_DATA["agree"] == "+" else -1) * ANS_CHOICE_WEIGHTS[ans_vec[i]]

        if COMPASS_DATA["axis"][i] == "x":
            score[0] += disp
        else:
            score[1] += disp

    return score

async def run_test_on_model(llm, cur_messages):
    cur_messages = deepcopy(cur_messages)
    cur_messages.append({"role": "user", "content": COMPASS_TEST_LLM_FORMAT})
    response = await llm.chat_completion(cur_messages, temperature=0.0, max_tokens=1024)

    if response is None:
        return None
    else:
        ans_vec = []
        for i in range(len(COMPASS_DATA)):
            if f"{i + 1}. A" in response:
                ans_vec.append("strong_disagree")
            elif f"{i + 1}. B" in response:
                ans_vec.append("disagree")
            elif f"{i + 1}. C" in response:
                ans_vec.append("agree")
            elif f"{i + 1}. D" in response:
                ans_vec.append("strong_agree")
            else:
                return None
        
        return calculate_compass_score(ans_vec)