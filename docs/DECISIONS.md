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
