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
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '.DS_Store' -exec rm -fr {} +

.PHONY: clean-test
clean-test:
	rm -fr .tox/
	rm -f .coverage
	find . -name ".coverage*" -not -name ".coveragerc" -exec rm -fr "{}" \;
	rm -fr coverage.xml
	rm -fr htmlcov/
	rm -fr .hypothesis
	rm -fr .pytest_cache
	rm -fr .mypy_cache/
	rm -fr input_file
	rm -fr output_file
	find . -name 'log.txt' -exec rm -fr {} +
	find . -name 'log.*.txt' -exec rm -fr {} +

.PHONY: lint
lint:
	black autonomous_hegician/contracts autonomous_hegician/skills hegic_deployer/contracts hegic_deployer/skills
	isort autonomous_hegician/contracts autonomous_hegician/skills hegic_deployer/contracts hegic_deployer/skills
	flake8 autonomous_hegician/contracts autonomous_hegician/skills hegic_deployer/contracts hegic_deployer/skills

.PHONY: security
security:
	bandit -x B104 -r autonomous_hegician/contracts autonomous_hegician/skills hegic_deployer/contracts hegic_deployer/skills 
	safety check -i 37524 -i 38038 -i 37776 -i 38039

.PHONY: vulture
vulture:
	if [ "0" == "$(shell ((vulture  autonomous_hegician/skills/option_management  whitelist.py )  | wc -l))" ];\
	then\
      echo "ah code is all used."; \
  else \
      echo "Not used!"; \
  fi
	if [ "0" == "$(shell ((vulture hegic_deployer/skills/hegic_deployer whitelist.py )  | wc -l))" ];\
	then\
      echo "deployer code is all used."; \
  else \
      echo "Not used!"; \
  fi

.PHONY: static
static:
	mypy autonomous_hegician/contracts autonomous_hegician/skills
	mypy hegic_deployer/contracts hegic_deployer/skills

.PHONY: new_env
new_env: clean
	if [ "$v" == "" ];\
	then\
		pipenv --rm;\
		pipenv --python 3.7;\
		echo "Enter clean virtual environment now: 'pipenv shell'.";\
	else\
		echo "In a virtual environment! Exit first: 'exit'.";\
	fi


.PHONY: install_env
install_env:
	pipenv install --dev --skip-lock
