
check-style:
	pylint **/*.py

ingest-data:
	python3 tool/ingest.py

chat:
	python3 main.py
