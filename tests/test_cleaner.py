"""Tests for src.data.cleaner."""

import pandas as pd
import pytest

from src.data import loader
from src.data.cleaner import CleaningReport, clean_dataset
from src.data.validator import validate_dataset


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """A small messy table covering every cleaning rule."""

    return pd.DataFrame(
        {
            "date": ["2020-03-01", "2020-01-01", "2020-01-01", "2020-02-01"],
            "home_team": ["Brazil ", "France", "Italy", "Spain"],
            "away_team": ["Chile", "Spain", "Peru", "Chile"],
            "home_score": [2.0, 1.0, None, 3.0],
            "away_score": [0.0, 1.0, None, 3.0],
            "tournament": ["Friendly"] * 4,
            "city": ["Rio", "Paris", "Rome", "Madrid"],
            "country": ["Brazil", "France", "Italy", "Spain"],
            "neutral": [False, True, False, False],
        }
    )


def test_clean_returns_frame_and_report(raw_df):
    cleaned, report = clean_dataset(raw_df)
    assert isinstance(cleaned, pd.DataFrame)
    assert isinstance(report, CleaningReport)


def test_input_is_not_modified(raw_df):
    snapshot = raw_df.copy(deep=True)
    clean_dataset(raw_df)
    pd.testing.assert_frame_equal(raw_df, snapshot)


def test_missing_scores_dropped_and_counted(raw_df):
    cleaned, report = clean_dataset(raw_df)
    assert report.dropped_missing_scores == 1
    assert "Italy" not in set(cleaned["home_team"])
    assert report.rows_in == 4 and report.rows_out == 3


def test_scores_become_integers(raw_df):
    cleaned, _ = clean_dataset(raw_df)
    assert cleaned["home_score"].dtype == "int64"
    assert cleaned["away_score"].dtype == "int64"


def test_dates_parsed_and_sorted_chronologically(raw_df):
    cleaned, _ = clean_dataset(raw_df)
    assert pd.api.types.is_datetime64_any_dtype(cleaned["date"])
    assert cleaned["date"].is_monotonic_increasing
    assert list(cleaned.index) == [0, 1, 2]


def test_whitespace_stripped_and_counted(raw_df):
    cleaned, report = clean_dataset(raw_df)
    assert "Brazil" in set(cleaned["home_team"])
    assert report.whitespace_fixed == 1


def test_exact_duplicates_dropped(raw_df):
    doubled = pd.concat([raw_df, raw_df.iloc[[1]]], ignore_index=True)
    _, report = clean_dataset(doubled)
    assert report.dropped_exact_duplicates == 1


def test_same_fixture_with_different_scores_is_kept(raw_df):
    rival = raw_df.iloc[[1]].copy()
    rival["home_score"] = 0.0
    both = pd.concat([raw_df, rival], ignore_index=True)
    _, report = clean_dataset(both)
    assert report.dropped_exact_duplicates == 0


def test_sort_is_stable_for_same_day_matches():
    df = pd.DataFrame(
        {
            "date": ["2020-01-01"] * 3,
            "home_team": ["A", "B", "C"],
            "away_team": ["X", "Y", "Z"],
            "home_score": [1, 1, 1],
            "away_score": [0, 0, 0],
            "tournament": ["Friendly"] * 3,
            "country": ["A", "B", "C"],
            "neutral": [False] * 3,
        }
    )
    cleaned, _ = clean_dataset(df)
    assert list(cleaned["home_team"]) == ["A", "B", "C"]


def test_cleaned_output_passes_validation(raw_df):
    cleaned, _ = clean_dataset(raw_df)
    assert validate_dataset(cleaned) == []


def test_missing_columns_raise(raw_df):
    with pytest.raises(ValueError, match="missing columns"):
        clean_dataset(raw_df.drop(columns=["neutral"]))


def test_bad_dates_raise(raw_df):
    raw_df.loc[0, "date"] = "not-a-date"
    with pytest.raises(ValueError, match="bad dates"):
        clean_dataset(raw_df)


def test_negative_scores_raise(raw_df):
    raw_df.loc[0, "home_score"] = -1.0
    with pytest.raises(ValueError, match="negative"):
        clean_dataset(raw_df)


def test_fractional_scores_raise(raw_df):
    raw_df.loc[0, "home_score"] = 1.5
    with pytest.raises(ValueError, match="fractions"):
        clean_dataset(raw_df)


_REAL_RESULTS = (
    loader.PROJECT_ROOT / "datasets" / "international_results" / "results.csv"
)


@pytest.mark.skipif(
    not _REAL_RESULTS.exists(),
    reason="external international_results dataset is not cloned",
)
def test_real_dataset_cleans_to_a_valid_table():
    """Loader -> cleaner -> validator on the real data, for any snapshot."""

    raw = loader.load_dataset("international_results", "results")
    cleaned, report = clean_dataset(raw)

    assert validate_dataset(cleaned) == []
    assert report.rows_in == len(raw)
    assert report.rows_out == (
        report.rows_in
        - report.dropped_missing_scores
        - report.dropped_exact_duplicates
    )
    assert cleaned["date"].is_monotonic_increasing
