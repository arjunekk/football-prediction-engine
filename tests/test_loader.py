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
def test_real_dataset_passes_validation():
    """Integration check against the real (externally cloned) dataset."""

    from src.data.validator import validate_dataset

    df = load_dataset("international_results", "results")
    assert isinstance(df, pd.DataFrame)
    assert validate_dataset(df) == []
