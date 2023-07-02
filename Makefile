
check-style:
	pylint **/*.py

ingest-data:
	python3 tool/ingest.py
