import random

RULE_MAP = {
    "semantic":    "semantic",
    "length":      "length",
    "phonological": "syllables"
}

def generate_trial(stimuli, current_rule):
    target = random.choice(stimuli)

    # The other two rules this trial must NOT accidentally match on
    other_rules = [r for r in RULE_MAP.keys() if r != current_rule]
    active_key  = RULE_MAP[current_rule]

    # Pure correct: matches on active rule, differs on both other rules
    correct_pool = [
        s for s in stimuli
        if s[active_key] == target[active_key]
        and s["text"] != target["text"]
        and all(s[RULE_MAP[r]] != target[RULE_MAP[r]] for r in other_rules)
    ]

    # Pure incorrect: does NOT match on active rule
    incorrect_pool = [
        s for s in stimuli
        if s[active_key] != target[active_key]
        and s["text"] != target["text"]
    ]

    # Recurse if pool is too small (rare with 54 words)
    if not correct_pool or len(incorrect_pool) < 2:
        return generate_trial(stimuli, current_rule)

    correct    = random.choice(correct_pool)
    incorrects = random.sample(incorrect_pool, 2)

    choices = [correct] + incorrects
    random.shuffle(choices)

    return target, choices