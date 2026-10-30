"""Dataset cleaning.

The cleaner *fixes* what can be fixed safely and reports exactly what it did.
Detection is the validator's job (Decision 003); the two never share logic.

Cleaning policy (Decision 009):

* Keep every team and every tournament. Filtering (e.g. FIFA members only)
  belongs to feature engineering, where it can be configured per competition.
* Keep extreme scores as recorded. Margin capping belongs inside the rating
  model, so the data stays truthful.
* Drop matches with no recorded score: they carry no outcome to learn from.
* Drop exact duplicate rows only. Two rows with the same date and teams but
  different scores are kept; they may be genuinely separate matches.
* Do not rename teams. The current dataset already uses current names; a
  name-normalisation stage is added only when a dataset needs it.

Anything the cleaner cannot repair safely (missing columns, unparseable
dates, negative or fractional scores) raises ``ValueError`` instead of being
silently altered.
"""

from dataclasses import dataclass

import pandas as pd

from src.data.validator import REQUIRED_COLUMNS, SCORE_COLUMNS

TEXT_COLUMNS = ["home_team", "away_team", "tournament", "city", "country"]


@dataclass(frozen=True)
class CleaningReport:
    """Summary of what :func:`clean_dataset` changed.

    Attributes
    ----------
    rows_in : int
        Rows in the input.
    rows_out : int
        Rows in the cleaned output.
    dropped_missing_scores : int
        Rows removed because a score was missing.
    dropped_exact_duplicates : int
        Rows removed because they duplicated another row in every column.
    whitespace_fixed : int
        Text cells whose leading/trailing whitespace was stripped.
    """

    rows_in: int
    rows_out: int
    dropped_missing_scores: int
    dropped_exact_duplicates: int
    whitespace_fixed: int


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """
    Clean a football results dataset.

    Steps, in order: strip whitespace in text columns, drop rows with missing
    scores, parse dates, convert scores to integers, drop exact duplicates,
    and sort chronologically (stable, so same-day order is preserved).

    Parameters
    ----------
    df : pandas.DataFrame
        Raw results table. It is never modified.

    Returns
    -------
    tuple[pandas.DataFrame, CleaningReport]
        The cleaned table (fresh 0..n-1 index, ``date`` as datetime64,
        scores as int64) and a report of what changed.

    Raises
    ------
    ValueError
        If required columns are missing, dates cannot be parsed, or scores
        are negative or not whole numbers.
    """

    _require_columns(df)
    rows_in = len(df)

    cleaned = df.copy()
    whitespace_fixed = _strip_text(cleaned)

    has_scores = cleaned[SCORE_COLUMNS].notna().all(axis=1)
    dropped_missing_scores = int((~has_scores).sum())
    cleaned = cleaned[has_scores].copy()

    cleaned["date"] = _parse_dates(cleaned["date"])
    _convert_scores(cleaned)

    before = len(cleaned)
    cleaned = cleaned.drop_duplicates()
    dropped_exact_duplicates = before - len(cleaned)

    cleaned = cleaned.sort_values("date", kind="stable").reset_index(drop=True)

    report = CleaningReport(
        rows_in=rows_in,
        rows_out=len(cleaned),
        dropped_missing_scores=dropped_missing_scores,
        dropped_exact_duplicates=dropped_exact_duplicates,
        whitespace_fixed=whitespace_fixed,
    )
    return cleaned, report


def _require_columns(df: pd.DataFrame) -> None:
    """Raise if any required column is absent."""

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Cannot clean dataset; missing columns: {missing}")


def _strip_text(df: pd.DataFrame) -> int:
    """Strip whitespace in text columns in place; return cells changed."""

    changed = 0
    for column in TEXT_COLUMNS:
        if column not in df.columns:
            continue
        original = df[column]
        stripped = original.str.strip()
        changed += int((original.notna() & (original != stripped)).sum())
        df[column] = stripped
    return changed


def _parse_dates(dates: pd.Series) -> pd.Series:
    """Parse ISO 8601 dates, raising on any that cannot be parsed."""

    try:
        return pd.to_datetime(dates, format="ISO8601", errors="raise")
    except (ValueError, TypeError) as error:
        raise ValueError(f"Cannot clean dataset; bad dates: {error}") from error


def _convert_scores(df: pd.DataFrame) -> None:
    """Convert score columns to int64 in place, rejecting invalid values."""

    for column in SCORE_COLUMNS:
        numeric = pd.to_numeric(df[column], errors="coerce")
        if numeric.isna().any():
            raise ValueError(f"Cannot clean dataset; {column} is non-numeric.")
        if (numeric % 1 != 0).any():
            raise ValueError(f"Cannot clean dataset; {column} has fractions.")
        if (numeric < 0).any():
            raise ValueError(f"Cannot clean dataset; {column} is negative.")
        df[column] = numeric.astype("int64")
