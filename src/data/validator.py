"""Dataset validation.

The validator only *detects* problems; it never modifies data (Decision 003).
Fixing problems is the responsibility of the cleaner.

Findings are split into two severities:

* **errors**   - the dataset cannot be trusted by downstream stages.
* **warnings** - suspicious but legitimate-looking data that the cleaner or
  a later stage may want to handle (e.g. duplicate fixtures, unsorted rows).
"""

import pandas as pd

REQUIRED_COLUMNS = [
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "tournament",
    "country",
    "neutral",
]

TEAM_COLUMNS = ["home_team", "away_team"]
SCORE_COLUMNS = ["home_score", "away_score"]

# Scores at or above this are legal in the data (e.g. 31-0) but extreme
# enough to deserve a look because they distort goal-based ratings.
EXTREME_SCORE_THRESHOLD = 15


def validate_dataset(df: pd.DataFrame) -> list[str]:
    """
    Validate a football results dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to validate. It is never modified.

    Returns
    -------
    list[str]
        A list of validation errors.
        An empty list means the dataset passed all checks.
        Use :func:`find_warnings` for non-fatal findings.
    """

    if df.empty:
        return ["Dataset is empty."]

    errors = _check_required_columns(df)
    if errors:
        # Later checks assume these columns exist, so fail fast here.
        return errors

    errors.extend(_check_missing_values(df))
    errors.extend(_check_dates(df))
    errors.extend(_check_scores(df))
    errors.extend(_check_teams(df))
    errors.extend(_check_neutral(df))
    return errors


def find_warnings(df: pd.DataFrame) -> list[str]:
    """
    Report non-fatal data-quality findings.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to inspect. It is never modified.

    Returns
    -------
    list[str]
        Human-readable warnings. Empty if nothing suspicious was found.
        Returns an empty list if the required columns are missing, because
        :func:`validate_dataset` already reports that as an error.
    """

    if _check_required_columns(df):
        return []

    warnings: list[str] = []

    duplicates = int(
        df.duplicated(["date", "home_team", "away_team"]).sum()
    )
    if duplicates:
        warnings.append(
            f"{duplicates} rows repeat the same date/home_team/away_team."
        )

    dates = pd.to_datetime(df["date"], format="ISO8601", errors="coerce")
    if dates.notna().all() and not dates.is_monotonic_increasing:
        warnings.append(
            "Rows are not sorted by date; rating stages need "
            "chronological order."
        )

    scores = df[SCORE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    extreme = int((scores >= EXTREME_SCORE_THRESHOLD).any(axis=1).sum())
    if extreme:
        warnings.append(
            f"{extreme} matches have a score of "
            f"{EXTREME_SCORE_THRESHOLD} or more goals."
        )

    return warnings


def _check_required_columns(df: pd.DataFrame) -> list[str]:
    """Return an error if any required column is absent."""

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]
    if missing_columns:
        return [f"Missing required columns: {missing_columns}"]
    return []


def _check_missing_values(df: pd.DataFrame) -> list[str]:
    """Return one error per required column containing nulls."""

    missing_values = df[REQUIRED_COLUMNS].isnull().sum()
    return [
        f"{column} contains {count} missing values."
        for column, count in missing_values.items()
        if count > 0
    ]


def _check_dates(df: pd.DataFrame) -> list[str]:
    """Return an error if non-null dates cannot be parsed."""

    present = df["date"].dropna()
    parsed = pd.to_datetime(present, format="ISO8601", errors="coerce")
    unparseable = int(parsed.isna().sum())
    if unparseable:
        return [f"date contains {unparseable} unparseable values."]
    return []


def _check_scores(df: pd.DataFrame) -> list[str]:
    """Return errors for non-numeric, fractional, or negative scores."""

    errors: list[str] = []
    for column in SCORE_COLUMNS:
        present = df[column].dropna()
        numeric = pd.to_numeric(present, errors="coerce")

        non_numeric = int(numeric.isna().sum())
        if non_numeric:
            errors.append(f"{column} contains {non_numeric} non-numeric values.")
            continue

        fractional = int((numeric % 1 != 0).sum())
        if fractional:
            errors.append(f"{column} contains {fractional} non-integer values.")

        negative = int((numeric < 0).sum())
        if negative:
            errors.append(f"{column} contains {negative} negative values.")
    return errors


def _check_teams(df: pd.DataFrame) -> list[str]:
    """Return errors for blank names or a team playing itself."""

    errors: list[str] = []
    for column in TEAM_COLUMNS:
        names = df[column].dropna().astype(str)
        stripped = names.str.strip()
        blank = int((stripped == "").sum())
        if blank:
            errors.append(f"{column} contains {blank} blank team names.")
        padded = int(((names != stripped) & (stripped != "")).sum())
        if padded:
            errors.append(
                f"{column} contains {padded} names with leading/trailing "
                "whitespace."
            )

    self_matches = int((df["home_team"] == df["away_team"]).sum())
    if self_matches:
        errors.append(
            f"{self_matches} matches have the same home and away team."
        )
    return errors


def _check_neutral(df: pd.DataFrame) -> list[str]:
    """Return an error if ``neutral`` is not strictly boolean."""

    present = df["neutral"].dropna()
    is_boolean = pd.api.types.is_bool_dtype(present) or bool(
        present.map(type).eq(bool).all()
    )
    if not is_boolean:
        return ["neutral must contain only True/False values."]
    return []
