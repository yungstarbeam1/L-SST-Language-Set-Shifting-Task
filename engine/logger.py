"""
logger.py — LS-ST Trial Logger & Measures Exporter

Records every trial and computes all WCST-aligned measures on export.

Perseverative error definition used here:
  An incorrect response where the chosen card would have been CORRECT
  under the immediately preceding rule. This is the standard WCST
  operationalisation of perseveration — the participant is still
  responding as if the old rule is in effect.
"""

import csv
import os
from datetime import datetime


class TrialLogger:
    def __init__(self, participant_id="participant"):
        self.participant_id = participant_id
        self.trials         = []          # list of trial dicts
        self.task_start_time = None       # set when task begins (ms, pygame ticks)

    def start_task(self, start_ms):
        self.task_start_time = start_ms

    # ── LOG A SINGLE TRIAL ────────────────────────────────────────────────────
    def log(
        self,
        trial_number,
        current_rule,
        previous_rule,
        target_card,
        chosen_card,
        correct,
        rt_ms,
        is_post_shift,          # True if this is the first trial under a new rule
        consecutive_correct,    # streak value AFTER this trial is resolved
    ):
        # Perseverative error check:
        # Wrong answer that would have been right under the previous rule
        perseverative = False
        if not correct and previous_rule is not None:
            perseverative = chosen_card.matches_rule(target_card, previous_rule)

        self.trials.append({
            "trial_number":         trial_number,
            "rule":                 current_rule,
            "previous_rule":        previous_rule if previous_rule else "none",
            "is_post_shift":        is_post_shift,
            "target_word":          target_card.text,
            "target_semantic":      target_card.semantic,
            "target_length":        target_card.length,
            "target_syllables":     target_card.syllables,
            "chosen_word":          chosen_card.text,
            "chosen_semantic":      chosen_card.semantic,
            "chosen_length":        chosen_card.length,
            "chosen_syllables":     chosen_card.syllables,
            "correct":              correct,
            "perseverative_error":  perseverative,
            "rt_ms":                rt_ms,
            "streak_after":         consecutive_correct,
        })

    # ── COMPUTE ALL MEASURES ──────────────────────────────────────────────────
    def compute_measures(self):
        T = self.trials
        if not T:
            return {}

        total_trials   = len(T)
        correct_trials = [t for t in T if t["correct"]]
        error_trials   = [t for t in T if not t["correct"]]
        total_correct  = len(correct_trials)
        total_errors   = len(error_trials)

        # ── PERSEVERATION ─────────────────────────────────────────────────────
        persev_errors     = [t for t in error_trials if t["perseverative_error"]]
        non_persev_errors = [t for t in error_trials if not t["perseverative_error"]]
        persev_count      = len(persev_errors)
        persev_rate       = round(persev_count / total_errors, 3) if total_errors else 0.0

        # ── CATEGORIES ────────────────────────────────────────────────────────
        # Count distinct rules that were ever successfully completed
        # A rule is completed when a shift away from it occurs (rule_index advanced)
        # We detect this by finding trials where is_post_shift is True
        # and recording the previous_rule
        completed_rules = set()
        for t in T:
            if t["is_post_shift"] and t["previous_rule"] != "none":
                completed_rules.add(t["previous_rule"])
        # Also check if the final rule was completed (game ended naturally)
        final_streaks = {}
        for t in T:
            final_streaks[t["rule"]] = t["streak_after"]
        from settings import TRIALS_PER_RULE
        for rule, streak in final_streaks.items():
            if streak >= TRIALS_PER_RULE:
                completed_rules.add(rule)

        categories_completed = len(completed_rules)

        # ── SET SHIFT MEASURES ────────────────────────────────────────────────
        # Group trials by rule epoch (consecutive trials under same rule)
        epochs = []
        current_epoch = []
        for t in T:
            if current_epoch and t["rule"] != current_epoch[-1]["rule"]:
                epochs.append(current_epoch)
                current_epoch = []
            current_epoch.append(t)
        if current_epoch:
            epochs.append(current_epoch)

        trials_to_first_correct_per_shift = []
        rt_first_correct_per_shift        = []
        errors_per_rule                   = {}

        for epoch in epochs:
            rule = epoch[0]["rule"]
            errors_per_rule[rule] = errors_per_rule.get(rule, 0) + sum(1 for t in epoch if not t["correct"])

            # Only measure shift acquisition for epochs after the first
            # (the first epoch has no shift to recover from)
            if epoch[0]["is_post_shift"]:
                count = 0
                for t in epoch:
                    count += 1
                    if t["correct"]:
                        trials_to_first_correct_per_shift.append(count)
                        rt_first_correct_per_shift.append(t["rt_ms"])
                        break

        mean_trials_to_acquire = (
            round(sum(trials_to_first_correct_per_shift) / len(trials_to_first_correct_per_shift), 2)
            if trials_to_first_correct_per_shift else None
        )

        # ── RESPONSE TIMES ────────────────────────────────────────────────────
        def mean_ms(lst):
            return round(sum(lst) / len(lst), 1) if lst else None

        mean_rt_correct   = mean_ms([t["rt_ms"] for t in correct_trials])
        mean_rt_incorrect = mean_ms([t["rt_ms"] for t in error_trials])
        mean_rt_overall   = mean_ms([t["rt_ms"] for t in T])

        # RT per rule
        mean_rt_per_rule = {}
        for rule in set(t["rule"] for t in T):
            rts = [t["rt_ms"] for t in T if t["rule"] == rule]
            mean_rt_per_rule[rule] = mean_ms(rts)

        # Post-error slowing: RT on trial immediately following an error
        post_error_rts = []
        for i in range(1, len(T)):
            if not T[i - 1]["correct"]:
                post_error_rts.append(T[i]["rt_ms"])
        mean_rt_post_error = mean_ms(post_error_rts)

        # ── ASSEMBLE ──────────────────────────────────────────────────────────
        measures = {
            # Core counts
            "participant_id":               self.participant_id,
            "total_trials":                 total_trials,
            "total_correct":                total_correct,
            "total_errors":                 total_errors,
            "percent_correct":              round(total_correct / total_trials * 100, 1),
            "categories_completed":         categories_completed,

            # Perseveration
            "perseverative_errors":         persev_count,
            "non_perseverative_errors":     len(non_persev_errors),
            "perseverative_error_rate":     persev_rate,

            # Set shift acquisition
            "mean_trials_to_acquire_rule":  mean_trials_to_acquire,
            "trials_to_first_correct_per_shift": trials_to_first_correct_per_shift,
            "rt_first_correct_per_shift_ms": rt_first_correct_per_shift,

            # Response times
            "mean_rt_correct_ms":           mean_rt_correct,
            "mean_rt_incorrect_ms":         mean_rt_incorrect,
            "mean_rt_overall_ms":           mean_rt_overall,
            "mean_rt_per_rule_ms":          mean_rt_per_rule,
            "mean_rt_post_error_ms":        mean_rt_post_error,

            # Per-rule errors
            "errors_per_rule":              errors_per_rule,
        }

        return measures

    # ── EXPORT TRIAL LOG CSV ──────────────────────────────────────────────────
    def export_trial_csv(self, output_dir="data"):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = os.path.join(output_dir, f"{self.participant_id}_{timestamp}_trials.csv")

        if not self.trials:
            return filename

        fieldnames = list(self.trials[0].keys())
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.trials)

        return filename

    # ── EXPORT SUMMARY MEASURES CSV ───────────────────────────────────────────
    def export_summary_csv(self, output_dir="data"):
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = os.path.join(output_dir, f"{self.participant_id}_{timestamp}_summary.csv")

        m = self.compute_measures()
        if not m:
            return filename

        # Flatten any nested dicts/lists into separate columns
        flat = {}
        for k, v in m.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    flat[f"{k}__{sub_k}"] = sub_v
            elif isinstance(v, list):
                flat[k] = ";".join(str(x) for x in v)
            else:
                flat[k] = v

        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(flat.keys()))
            writer.writeheader()
            writer.writerow(flat)

        return filename

    def export_all(self, output_dir="data"):
        trial_file   = self.export_trial_csv(output_dir)
        summary_file = self.export_summary_csv(output_dir)
        print(f"[LS-ST] Trial log  → {trial_file}")
        print(f"[LS-ST] Summary    → {summary_file}")
        return trial_file, summary_file