install:
	poetry install
	poetry run pre-commit install

run:
	poetry run python -m party_purse

flow:
	poetry run python flows/main_flow.py run

dashboard:
	poetry run streamlit run dashboard/app.py

experiment:
	poetry run python -m party_purse.experiment

test:
	poetry run pytest

format:
	poetry run black .
	poetry run ruff check . --fix