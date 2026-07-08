# AI Instructions

## Purpose

You are contributing to a professional software engineering and machine learning project called **Football Prediction Engine**.

Your objective is to help build a reusable football analytics engine—not just a FIFA World Cup predictor.

Before making ANY changes, you MUST read:

1. docs/PROJECT_CONTEXT.md
2. docs/ROADMAP.md
3. docs/ARCHITECTURE.md
4. docs/DECISIONS.md (if architectural changes are involved)

Never ignore these files.

---

# Project Goal

Build a production-quality football analytics engine capable of:

- Rating football teams
- Predicting football matches
- Simulating tournaments
- Supporting multiple football competitions

The engine should work for:

- FIFA World Cup
- UEFA Euros
- Copa America
- Premier League
- Champions League
- Any future football competition

The project must remain generic.

---

# Development Philosophy

Always think like a Senior Machine Learning Engineer and Software Engineer.

Before writing code:

1. Understand the architecture.
2. Explain important design decisions.
3. Implement cleanly.
4. Test.
5. Keep the project modular.

Do not rush into coding.

---

# Coding Standards

Every public function must include:

- Type hints
- Docstrings

Use:

- pathlib
- pandas
- clear variable names

Avoid:

- os.path unless absolutely necessary
- giant functions
- duplicated code
- notebook-style programming

Functions should have a single responsibility.

---

# Software Engineering Principles

Always follow:

- Single Responsibility Principle
- Fail Fast
- Loose Coupling
- High Cohesion
- DRY (Don't Repeat Yourself)
- KISS (Keep It Simple)
- Readability over cleverness

---

# Project Structure

Respect the existing folder structure.

Do not create random folders.

Only create new modules if they clearly belong in the architecture.

---

# Data Pipeline

Always preserve this flow:

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

Poisson Goal Model

↓

Prediction Engine

↓

Tournament Simulator

Never bypass stages.

---

# Validation Philosophy

Validator detects problems.

Cleaner fixes problems.

Do not mix these responsibilities.

---

# Dataset Policy

Datasets are external Git repositories.

Never assume datasets are committed.

Never hardcode dataset paths.

Always use the project's dataset loader.

---

# Error Handling

Raise meaningful exceptions.

Fail early when required information is missing.

Do not silently ignore errors.

Error messages should clearly explain what went wrong.

---

# Testing

Every new feature should include an appropriate test.

Do not consider a feature complete without testing.

---

# Git Workflow

For every feature:

Implement

↓

Test

↓

Commit

↓

Push

Use meaningful commit messages.

Avoid "update", "fix", or "changes".

---

# Documentation

Whenever architecture changes:

Update:

- PROJECT_CONTEXT.md
- ROADMAP.md
- ARCHITECTURE.md
- DECISIONS.md (if a major decision was made)
- CHANGELOG.md (when a milestone is completed)

Keep documentation synchronized with the code.

---

# Machine Learning Philosophy

Prioritize:

- Explainability
- Reproducibility
- Statistical correctness
- Modular pipelines

Avoid black-box code whenever possible.

---

# Football Analytics Philosophy

Do not simply copy existing football models.

Whenever possible, improve upon them.

Examples:

- Football Strength Index instead of plain Elo
- Dynamic tournament weighting
- Home advantage estimation
- Goal difference scaling
- Time decay
- Recent form weighting

The objective is to create an original, extensible rating system.

---

# Communication Style

Assume the user understands intermediate Python.

Do not over-explain basic syntax.

Focus explanations on:

- Architecture
- Algorithms
- Statistics
- Machine Learning
- Software Engineering
- Design trade-offs

When multiple approaches exist:

1. Present the options.
2. Explain the pros and cons.
3. Recommend one.
4. Explain why.

---

# Long-Term Vision

The final repository should resemble a professional open-source analytics project.

It should include:

- Clean architecture
- Modular design
- Comprehensive documentation
- Tests
- Professional commit history
- High-quality README
- Extensible ML pipeline
- Reusable football analytics engine

Every contribution should move the project toward this vision.