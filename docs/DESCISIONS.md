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