# Running Tests

This guide explains how to run the test suite for the backend.

## Prerequisites

Make sure you have all dependencies installed:

```bash
cd backend
pip install -r requirements.txt
```

## Running Tests

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test File

```bash
# Run only scoring tests
pytest tests/test_scoring.py

# Run only auth tests
pytest tests/test_auth_login.py
```

### Run Specific Test Class or Function

```bash
# Run a specific test class
pytest tests/test_scoring.py::TestCalculatePredictionPoints

# Run a specific test function
pytest tests/test_scoring.py::TestCalculatePredictionPoints::test_exact_score_match
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
# First install pytest-cov if not already installed
pip install pytest-cov

# Then run with coverage
pytest --cov=app --cov-report=html
```

## Environment Variables

Tests use an in-memory SQLite database by default, so you don't need to set up a real database. However, you may need to set some environment variables:

```bash
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export SECRET_KEY="test-secret-key-for-testing"
```

Or set them inline:

```bash
DATABASE_URL="sqlite+aiosqlite:///:memory:" SECRET_KEY="test-secret-key" pytest
```

## Test Structure

- `tests/conftest.py` - Pytest configuration and fixtures
- `tests/test_*.py` - Individual test files
- Tests use an in-memory SQLite database (no setup required)
- Tests are async and use `pytest-asyncio`

## Common Issues

### Import Errors

If you get import errors, make sure you're running from the `backend` directory:

```bash
cd backend
pytest
```

### Database Configuration Errors

If you see errors about `pool_size` or `max_overflow`, make sure you're using the latest version of `database.py` which handles SQLite properly.

### Missing Dependencies

If tests fail with missing imports, install all requirements:

```bash
pip install -r requirements.txt
```

## Example Test Run

```bash
$ cd backend
$ pytest tests/test_scoring.py -v

============================= test session starts ==============================
platform darwin -- Python 3.12.0, pytest-7.4.3, pytest-asyncio-0.21.1
collected 15 items

tests/test_scoring.py::TestCalculatePredictionPoints::test_exact_score_match PASSED
tests/test_scoring.py::TestCalculatePredictionPoints::test_correct_outcome_and_home_goals PASSED
...
============================= 15 passed in 2.34s ==============================
```


