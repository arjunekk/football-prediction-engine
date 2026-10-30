"""Tests for src.data.loader."""

from pathlib import Path

import pandas as pd
import pytest

from src.data import loader
from src.data.loader import load_dataset


@pytest.fixture
def fake_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the loader at a temporary project root with one tiny dataset."""

    source_dir = tmp_path / "datasets" / "demo_source"
    source_dir.mkdir(parents=True)
    (source_dir / "results.csv").write_text("a,b\n1,2\n3,4\n")
    monkeypatch.setattr(loader, "PROJECT_ROOT", tmp_path)
    return tmp_path


def test_load_dataset_reads_csv(fake_project):
    df = load_dataset("demo_source", "results")
    assert df.shape == (2, 2)
    assert list(df.columns) == ["a", "b"]


def test_load_dataset_missing_file_raises_with_path(fake_project):
    with pytest.raises(FileNotFoundError, match="nope.csv"):
        load_dataset("demo_source", "nope")


def test_load_dataset_missing_source_raises(fake_project):
    with pytest.raises(FileNotFoundError):
        load_dataset("missing_source", "results")


_REAL_RESULTS = (
    loader.PROJECT_ROOT / "datasets" / "international_results" / "results.csv"
)


@pytest.mark.skipif(
    not _REAL_RESULTS.exists(),
    reason="external international_results dataset is not cloned",
)
def test_validator_agrees_with_real_dataset():
    """Integration check against the real (externally cloned) dataset.

    The dataset is maintained externally (Decision 001), so a given snapshot
    may legitimately contain incomplete rows, e.g. matches whose scores were
    not yet recorded. The test therefore does not assert "zero errors".
    Instead it checks that the validator's report is *consistent with the
    data*:

    * structural problems (missing columns, bad dates, negative scores,
      bad team names, non-boolean ``neutral``) never occur, and
    * the only error allowed is missing score values, whose reported count
      must equal an independent pandas null count.
    """

    from src.data.validator import validate_dataset

    df = load_dataset("international_results", "results")
    assert isinstance(df, pd.DataFrame)

    expected = {
        f"{column} contains {count} missing values."
        for column in ("home_score", "away_score")
        if (count := int(df[column].isnull().sum())) > 0
    }

    assert set(validate_dataset(df)) == expected
