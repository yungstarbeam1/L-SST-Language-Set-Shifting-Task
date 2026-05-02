RULES = ["semantic", "length", "phonological"]

# Set to False for fixed order (semantic → length → phonological)
SHUFFLE_RULES = True

# WCST-style streak to shift rule — don't tell the participant!
TRIALS_PER_RULE = 1  # default
TOTAL_TRIALS = TRIALS_PER_RULE * len(RULES)