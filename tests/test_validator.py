"""Tests for src.data.validator."""

import pandas as pd
import pytest

from src.data.validator import find_warnings, validate_dataset


@pytest.fixture
def valid_df() -> pd.DataFrame:
    """A tiny, fully valid results table."""

    return pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-05"],
            "home_team": ["Brazil", "France"],
            "away_team": ["Chile", "Spain"],
            "home_score": [2, 1],
            "away_score": [0, 1],
            "tournament": ["Friendly", "Friendly"],
            "country": ["Brazil", "France"],
            "neutral": [False, True],
        }
    )


def test_valid_dataset_has_no_errors_or_warnings(valid_df):
    assert validate_dataset(valid_df) == []
    assert find_warnings(valid_df) == []


def test_validator_does_not_modify_input(valid_df):
    snapshot = valid_df.copy(deep=True)
    validate_dataset(valid_df)
    find_warnings(valid_df)
    pd.testing.assert_frame_equal(valid_df, snapshot)


def test_empty_dataset_is_an_error(valid_df):
    assert validate_dataset(valid_df.iloc[0:0]) == ["Dataset is empty."]


def test_missing_columns_fail_fast(valid_df):
    errors = validate_dataset(valid_df.drop(columns=["tournament", "neutral"]))
    assert len(errors) == 1
    assert "tournament" in errors[0] and "neutral" in errors[0]


def test_missing_values_reported_per_column(valid_df):
    valid_df.loc[0, "home_team"] = None
    errors = validate_dataset(valid_df)
    assert any("home_team contains 1 missing" in e for e in errors)


def test_missing_scores_are_errors_not_warnings(valid_df):
    """Incomplete historical results must never be silently tolerated."""

    valid_df["home_score"] = valid_df["home_score"].astype("float")
    valid_df["away_score"] = valid_df["away_score"].astype("float")
    valid_df.loc[0, ["home_score", "away_score"]] = None

    errors = validate_dataset(valid_df)
    assert "home_score contains 1 missing values." in errors
    assert "away_score contains 1 missing values." in errors
    assert not any("missing" in w for w in find_warnings(valid_df))


def test_unparseable_dates(valid_df):
    valid_df.loc[0, "date"] = "not-a-date"
    errors = validate_dataset(valid_df)
    assert any("date contains 1 unparseable" in e for e in errors)


def test_negative_scores(valid_df):
    valid_df.loc[1, "away_score"] = -1
    errors = validate_dataset(valid_df)
    assert any("away_score contains 1 negative" in e for e in errors)


def test_fractional_scores(valid_df):
    valid_df["home_score"] = [2.5, 1.0]
    errors = validate_dataset(valid_df)
    assert any("home_score contains 1 non-integer" in e for e in errors)


def test_non_numeric_scores(valid_df):
    valid_df["home_score"] = ["two", "1"]
    errors = validate_dataset(valid_df)
    assert any("home_score contains 1 non-numeric" in e for e in errors)


def test_team_playing_itself(valid_df):
    valid_df.loc[0, "away_team"] = "Brazil"
    errors = validate_dataset(valid_df)
    assert any("same home and away team" in e for e in errors)


def test_blank_and_padded_team_names(valid_df):
    valid_df.loc[0, "home_team"] = "  "
    valid_df.loc[1, "away_team"] = " Spain"
    errors = validate_dataset(valid_df)
    assert any("home_team contains 1 blank" in e for e in errors)
    assert any("away_team contains 1 names with leading" in e for e in errors)


def test_neutral_must_be_boolean(valid_df):
    valid_df["neutral"] = ["yes", "no"]
    errors = validate_dataset(valid_df)
    assert any("neutral must contain only" in e for e in errors)


def test_duplicate_fixture_is_a_warning_not_an_error(valid_df):
    duplicated = pd.concat([valid_df, valid_df.iloc[[0]]], ignore_index=True)
    assert validate_dataset(duplicated) == []
    assert any("repeat the same" in w for w in find_warnings(duplicated))


def test_unsorted_dates_warn(valid_df):
    reversed_df = valid_df.iloc[::-1].reset_index(drop=True)
    assert validate_dataset(reversed_df) == []
    assert any("not sorted" in w for w in find_warnings(reversed_df))


def test_extreme_scores_warn(valid_df):
    valid_df.loc[0, "home_score"] = 31
    assert any("15 or more goals" in w for w in find_warnings(valid_df))


def test_warnings_skip_when_columns_missing(valid_df):
    assert find_warnings(valid_df.drop(columns=["date"])) == []
