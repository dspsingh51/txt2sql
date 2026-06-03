.PHONY: install seed api ui test compile docker

install:
	pip install -r requirements.txt

seed:
	python -m sql_engine.seed

api:
	uvicorn app.main:app --reload

ui:
	streamlit run frontend/streamlit_app.py

test:
	pytest -q

compile:
	python -m compileall app agents api configs frontend memory sql_engine workflows tests

docker:
	docker compose up --build
