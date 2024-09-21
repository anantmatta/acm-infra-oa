.PHONY: install local test reset_db

install:
	python3 -m pip install -r requirements.txt

local:
	python3 server.py

test:
	cp data.db data-testing.db && DB_PATH=data-testing.db PYTHONPATH=./ pytest -W ignore::DeprecationWarning && rm data-testing.db

reset_db:
	rm data.db && wget https://github.com/acm-uiuc/infra-interviews-assets/raw/main/fa24/data.db