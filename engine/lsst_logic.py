class LSSTEngine:
    def __init__(self):
        pass  

    #^ CAlled from main.py rule

    def check(self, target, choice, rule):
        """
        Check whether the choice card matches the target under the given rule.
        Rule must be passed in explicitly — the engine does NOT hold its own rule.
        """
        return choice.matches_rule(target, rule)