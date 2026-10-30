# Architecture

## Project Architecture

[Pipeline Diagram]

## Folder Structure

Explain each folder.

## Module Responsibilities

loader.py - reads CSVs from datasets/<source>/<table>.csv; never hardcodes paths.

validator.py - detects problems, never modifies data. `validate_dataset`
returns fatal errors; `find_warnings` returns non-fatal findings.

cleaner.py - fixes what is safe (whitespace, unscored rows, exact duplicates,
dtypes, chronological order) and returns a `CleaningReport`. Raises
`ValueError` for anything it cannot repair. See Decision 009.

feature_engineering.py

football_strength_index.py

poisson_model.py

predictor.py

simulator.py

## Data Flow

Raw CSV

↓

Loader

↓

Validator

↓

Cleaner

↓

Feature Engineering

↓

Football Strength Index

↓

Poisson Model

↓

Prediction

↓

Tournament Simulation

## Future Architecture

Dashboard

REST API

Database

Live Match Prediction

Cloud Deployment