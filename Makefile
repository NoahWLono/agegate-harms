.PHONY: setup validate test run ui clean

setup:
	uv sync --extra dev --extra ui

validate:
	uv run agegate-evidence --config data/scenarios/quebec_bill9_v02.yaml --evidence data/evidence.csv --output results/evidence_coverage.csv

test:
	uv run pytest -v

run:
	uv run agegate-run --config data/scenarios/quebec_bill9_v02.yaml --evidence data/evidence.csv --simulations 50000 --seed 20260722

ui:
	uv run streamlit run app.py

clean:
	rm -f results/*.csv results/*.png results/*.html results/*.json results/REPORT.md
