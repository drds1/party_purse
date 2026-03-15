# Party Purse

Author: David Starkey

---

## Overview

Tracking the money behind UK politics. Automated donation data → structured by LLMs → visualized in Streamlit. Open source, quarterly updates, full transparency.

This project was generated from the ML Project Template.  
It includes:

- Python environment managed with Poetry
- Optional Metaflow pipeline scaffold
- Optional MLflow experiment tracking
- Optional Streamlit dashboard scaffold
- Pre-commit hooks for code formatting and linting
- GitHub Actions CI workflow

---

## Setup

1. Install dependencies and set up environment:

    poetry install
    poetry run pre-commit install

2. Create a `.env` file from `.env.example` and fill in your environment variables:

    cp .env.example .env
    # Then edit .env with your secrets

---

## Running the Project

- Run main Python module:

    make run

- Run Metaflow pipeline:

    make flow

- Run Streamlit dashboard:

    make dashboard

- Run MLflow experiment scaffold:

    make experiment

---

## Testing

- Run tests:

    make test

- Format and lint code:

    make format

---

## Project Structure

- `src/party_purse/` → main Python package  
- `flows/` → Metaflow pipelines  
- `dashboard/` → Streamlit app  
- `.pre-commit-config.yaml` → pre-commit hooks  
- `.github/workflows/` → CI with GitHub Actions  
- `Makefile` → unified commands for development workflow  

---

## Notes

- This project is ready to run immediately after generation  
- Replace placeholder code in `flows/main_flow.py`, `dashboard/app.py`, and `src/party_purse/experiment.py` with your own logic  
- All commands can be run via `make` for simplicity

---

## License

MIT