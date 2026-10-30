# Engineering Decisions

---

## Decision 001

Title:
Datasets are external repositories

Status:
Accepted

Reason:
Keeps repository lightweight.
Allows updating datasets independently.
Avoids copying another repository.

Alternatives:
Commit CSV files directly.
Use Git submodules.

Chosen:
External repository.

---

## Decision 002

Title:
Use pathlib instead of os.path

Status:
Accepted

Reason:
Cross-platform.
Cleaner syntax.
Modern Python.

---

## Decision 003

Title:
Validator only detects issues

Status:
Accepted

Reason:
Single Responsibility Principle.

Cleaner performs fixes.

---

## Decision 004

Title:
Generic football engine instead of World Cup-only project

Reason:
Reusable for every competition.

---

## Decision 005

Title:
Use Football Strength Index instead of pure Elo

Reason:
Allows us to extend the model with:
- Tournament weighting
- Home advantage
- Goal difference
- Time decay

---

## Decision 006

Title:
Validator separates errors from warnings

Status:
Accepted

Reason:
Some oddities are legitimate data, not corruption. The real results.csv
contains one repeated date/home/away key (two different scores on the
same day) and 61 matches with 15+ goals (e.g. 31-0). Treating these as
errors would block the pipeline; ignoring them hides risk.

Chosen:
`validate_dataset(df) -> list[str]` returns errors only (fatal).
`find_warnings(df) -> list[str]` returns non-fatal findings.
Neither modifies data; the cleaner decides what to fix.

---

## Decision 007

Title:
Tests run with pytest and `pythonpath = .`

Status:
Accepted

Reason:
Removes the `sys.path.append` hack from scripts. Tests that need the
external dataset skip automatically when it is not cloned (Decision 001).


---

## Decision 008

Title:
Integration test checks validator consistency, not a clean dataset

Status:
Accepted

Reason:
The external dataset (Decision 001) changes independently of this repo, and
a given snapshot may contain historical matches whose scores are not yet
recorded. Asserting `validate_dataset(df) == []` made the suite fail
whenever such a snapshot was cloned, which tests the dataset rather than
the validator.

Chosen:
`test_validator_agrees_with_real_dataset` asserts that the validator's
errors exactly equal the missing-score counts computed independently with
pandas. Any other error category (columns, dates, negative scores, team
names, `neutral` type) still fails the test. The validator is unchanged:
missing scores remain errors (never warnings), and a unit test pins that
behaviour. Deciding what to do with unscored rows belongs to the cleaner.


---

## Decision 009

Title:
Cleaner policy: fix only what is safe, report everything, fail on the rest

Status:
Accepted

Reason:
Cleaning silently changes training data, so every change must be explicit
and countable, and anything ambiguous must stay truthful.

Chosen:
`clean_dataset(df) -> (cleaned_df, CleaningReport)`.
- Keep all teams and tournaments. Filtering (e.g. FIFA members only) is a
  per-competition feature-engineering concern, not a cleaning one.
- Keep extreme scores (e.g. 31-0). Margin capping belongs in the rating
  model so the stored data stays truthful.
- Drop rows with missing scores (no outcome to learn from) and count them.
- Drop exact duplicate rows only. Same date/teams with different scores
  (e.g. Tahiti v New Caledonia, 1974) are kept as possibly separate matches.
- Sort by date with a stable sort so same-day order is preserved.
- No team renaming until a dataset needs it (`former_names.csv` is already
  reflected in `results.csv`).
- Raise `ValueError` for what cannot be repaired safely: missing columns,
  unparseable dates, negative or fractional scores.

Alternatives:
Filter to FIFA members during cleaning; cap scores at the cleaner; impute
missing scores. All rejected: they hide information or invent data.
