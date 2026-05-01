import random

RULE_MAP = {
    "semantic": "semantic",
    "syntactic": "syntactic",
    "phonological": "syllables"
}

def generate_trial(stimuli, current_rule):
    target = random.choice(stimuli)
    
    # Identify the other two rules that are NOT the current one
    other_rules = [r for r in RULE_MAP.keys() if r != current_rule]
    active_key = RULE_MAP[current_rule]
    
    # 1. Find a 'Pure' Correct Match
    # Must match target on the active rule, but NOT on the other two rules
    correct_pool = [
        s for s in stimuli 
        if s[active_key] == target[active_key] 
        and s["text"] != target["text"]
        and all(s[RULE_MAP[r]] != target[RULE_MAP[r]] for r in other_rules)
    ]

    # 2. Find 'Pure' Incorrect Choices
    # Must NOT match target on the active rule
    incorrect_pool = [
        s for s in stimuli 
        if s[active_key] != target[active_key]
        and s["text"] != target["text"]
    ]

    # Fallback: If stimuli pool is too small for pure matches, 
    # loosen constraints or alert dev.
    if not correct_pool or len(incorrect_pool) < 2:
        return generate_trial(stimuli, current_rule)

    correct = random.choice(correct_pool)
    incorrects = random.sample(incorrect_pool, 2)

    choices = [correct] + incorrects
    random.shuffle(choices)

    return target, choices