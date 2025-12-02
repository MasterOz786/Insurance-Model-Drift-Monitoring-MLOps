python = bin/python
pip = bin/pip

setup:
	python3 -m venv venv
	$(python) -m pip install --upgrade pip setuptools wheel
	$(pip) install --prefer-binary -r requirements.txt

run:
	$(python) main.py

mlflow:
	bin/mlflow ui

test:
	$(python) -m pytest
		
clean:
	rm -rf steps/__pycache__
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf tests/__pycache__

remove:
	rm -rf mlruns
