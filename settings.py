RULES = ["semantic", "syntactic", "phonological"]

#set to false for set order (sesmantic, syntactic, phonological)
SHUFFLE_RULES = True

#WCST style stsreak to switch rule, dont tell the participant! 
TRIALS_PER_RULE = 3 #beta testing fix to 5 later
TOTAL_TRIALS = TRIALS_PER_RULE * len(RULES)