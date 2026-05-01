import random

RULE_MAP = {
    "semantic": "semantic",
    "length": "length",
    "phonological": "syllables"
}

MAX_ATTEMPTS = 100


def generate_trial(stimuli, current_rule):
    active_key = RULE_MAP[current_rule]
    other_rules = [r for r in RULE_MAP if r != current_rule]

    for _ in range(MAX_ATTEMPTS):

        target = random.choice(stimuli)

        # ---------------------------
        # PURE CORRECT POOL
        # matches ONLY active rule
        # ---------------------------
        correct_pool = [
            s for s in stimuli
            if s["text"] != target["text"]
            and s[active_key] == target[active_key]
            and all(s[RULE_MAP[r]] != target[RULE_MAP[r]] for r in other_rules)
        ]

        if not correct_pool:
            continue

        correct = random.choice(correct_pool)

        # ---------------------------
        # PURE INCORRECT POOL
        # matches NONE of the rules
        # ---------------------------
        incorrect_pool = [
            s for s in stimuli
            if s["text"] != target["text"]
            and s[active_key] != target[active_key]
            and all(s[RULE_MAP[r]] != target[RULE_MAP[r]] for r in other_rules)
        ]

        if len(incorrect_pool) < 2:
            continue

        incorrects = random.sample(incorrect_pool, 2)

        choices = [correct] + incorrects
        random.shuffle(choices)

        return target, choices

    # ---------------------------
    # FAILSAFE (if constraints too tight)
    # ---------------------------
    raise ValueError(
        "Could not generate a valid trial. "
        "Your stimulus set may be too constrained or unbalanced."
    )