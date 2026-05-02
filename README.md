[L-SST_showcase.md](https://github.com/user-attachments/files/27306615/L-SST_showcase.md)
# L-SST — Language Set-Shifting Task

![L-SST Start Screen](1777745023973_2026-05-02_14_01_24-L-SST.png)

> *Can your brain switch gears fast enough?*

---

## What is L-SST?

**L-SST** is a cognitive flexibility task built for researchers studying how the brain manages and struggles with **rule-based thinking under uncertainty**.

It's an English-language reimagining of the classic **Wisconsin Card Sorting Test (WCST)**, rebuilt around words instead of cards. Participants sort words by a hidden rule that silently shifts once they've figured it out. The catch? They're never told the rule changed.

That moment of confusion when someone keeps using the old rule even after it's stopped working is exactly what we're measuring.

---

## Why words?

The WCST uses colours, shapes, and numbers. L-SST uses **language**.

That's not a small difference. Language processing pulls on a different set of cognitive resources: semantic memory, phonological awareness, lexical access. By grounding the task in words, L-SST targets **linguistic cognitive control** specifically, making it useful for:

-  Research on language & executive function
-  Studies of bilingualism and cognitive flexibility
-  Clinical screening for perseverative thinking
-  Cognitive psychology coursework and demos

---

## How it works

A **target word** appears at the top of the screen. Three choice words appear below. The participant picks the one that matches the target — but the rule is never shown.

```
        [ FOREST ]          ← target

  [ Sun ]  [ Doctor ]  [ Laptop ]   ← choices
```

The active rule could be any of three dimensions:

| Rule | What to match | Example |
|------|--------------|---------|
| **Semantic** | Same category | *Forest* → *Ocean* (both nature) |
| **Length** | Same word-length tier | *Forest* → *Doctor* (both medium) |
| **Phonological** | Same syllable count | *Forest* → *Driver* (both 2 syllables) |

Get **5 in a row correct** → the rule shifts. No warning. No fanfare. The task just quietly moves the goalposts.

---

## What it measures

L-SST captures a rich set of WCST-aligned cognitive measures automatically:

###  Accuracy
- Total correct responses & error rate
- Categories completed (out of 3)

###  Perseveration
> *The hallmark of inflexible thinking.*

A **perseverative error** is when a participant chooses the card that would have been correct under the **previous** rule — they're still playing by the old rules. This is the core measure of cognitive rigidity, directly comparable to WCST perseveration scores.

###  Set-Shift Acquisition
- How many trials it takes to get the first correct response after each rule shift
- Captures *how quickly* someone detects and adapts to change

### Reaction Time
- Mean RT for correct vs. incorrect responses
- RT per rule dimension
- **Post-error slowing**  the hesitation that follows a mistake

---

## Built for research

-  **No setup friction** — double-click and go, no Python required for participants
-  **Automatic CSV export** — trial-level log + summary measures, timestamped per participant
-  **Configurable** — tweak rules, streak threshold, and rule order in `settings.py`
-  **Debug mode** — press `B` to reveal current rule and streak (researcher use only)
-  **Dark & light modes** — press `D` to toggle
-  **Pure-match trial generation** — correct choice always matches on exactly one dimension, eliminating ambiguous trials

---

## Controls

| Key | Action |
|-----|--------|
| `SPACE` | Start |
| `1` `2` `3` or click | Select a card |
| `D` | Toggle dark / light mode |
| `B` | Debug HUD *(researcher only)* |
| `V` | Reveal results summary |
| `S` | Save data to `data/` |
| `ESC` | Exit |

---

## Quick start

```
LSST_release/
├── LSST.exe       ← double-click to run
├── settings.py    ← configure the task here
├── Manual.md      ← full documentation
└── data/          ← exported CSVs appear here
```

No installation. No Python. No dependencies. Just run it.

---

## Configuration

Open `settings.py` in any text editor:

```python
RULES = ["semantic", "length", "phonological"]  # which rules to include
SHUFFLE_RULES = True                             # randomise rule order?
TRIALS_PER_RULE = 5                              # streak needed to shift
```

Before each session, update the participant ID in `main.py`:
```python
logger = TrialLogger(participant_id="P001")
```

---

## The science behind it

Cognitive set-shifting, the ability to disengage from a current mental strategy and switch to a new one, is a core component of **executive function**.
The WCST has been a gold-standard measure of this since the 1940s. L-SST brings it into the domain of language, opening up new research questions about how **verbal cognition and cognitive control interact**.

---

*Built with Python & pygame.*
