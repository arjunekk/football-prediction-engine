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


def validate_dataset(df: pd.DataFrame) -> list[str]:
    """
    Validate a football results dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to validate.

    Returns
    -------
    list[str]
        A list of validation errors.
        An empty list means the dataset passed all checks.
    """

    errors = []

    # Check required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"Missing required columns: {missing_columns}"
        )
        return errors

    # Check for missing values
    missing_values = df[REQUIRED_COLUMNS].isnull().sum()

    for column, count in missing_values.items():
        if count > 0:
            errors.append(
                f"{column} contains {count} missing values."
            )

    return errors