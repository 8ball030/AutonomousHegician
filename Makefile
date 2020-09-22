.PHONY: clean
clean: clean-build clean-pyc clean-test clean-docs

.PHONY: clean-build
clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr pip-wheel-metadata
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +
	rm -fr Pipfile.lock

.PHONY: clean-docs
clean-docs:
	rm -fr site/

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.vscode' -exec rm -fr {} +
	find . -name '*.ipynb_checkpoints' -exec rm -fr {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.DS_Store' -exec rm -fr {} +

.PHONY: clean-test
clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr .coverage*
	rm -fr coverage.xml
	rm -fr htmlcov/
	rm -fr .hypothesis
	rm -fr .pytest_cache
	rm -fr .mypy_cache/
	rm -fr fetch/AutonomousHegician/input_file
	rm -fr fetch/AutonomousHegician/output_file
	find . -name 'log.txt' -exec rm -fr {} +
	find . -name 'log.*.txt' -exec rm -fr {} +
