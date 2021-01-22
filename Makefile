.PHONY: clean clean-test clean-pyc clean-build docs help
.PHONY: docker-build docker-run-no-build docker-run
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

app_name:=line-item-manager
ifndef image_repo
image_repo:=${app_name}
endif
docker_org:=prebid

docker-build: ## build docker image for local development
	docker build ${extra_build_opts} --tag ${docker_org}/${image_repo}:${IMAGE_TAG_PREFIX}latest .
docker-run-no-build: ## docker run without building docker image
	docker run -it --rm ${extra_run_opts} ${docker_org}/${image_repo} ${command} ${extra_args}
docker-run: docker-build docker-run-no-build  ## docker build and run with env vars 'extra_run_opts', 'command', and 'extra_args'

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint: ## check style with flake8
	flake8 line_item_manager tests

test: ## run tests quickly with the default Python
	pytest \
	--cov=line_item_manager \
	--cov-report term-missing

coverage: ## check code coverage quickly with the default Python
	coverage run --source line_item_manager -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

docs: ## generate Sphinx HTML documentation, including API docs
	rm -f docs/line_item_manager.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ line_item_manager
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/_build/html/index.html

servedocs: docs ## compile the docs watching for changes
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

pre_release:
	sed -i "s/^dev_version =.*/dev_version = ''/" line_item_manager/__init__.py

release_test: dist ## package and upload a release
	twine check dist/*
	twine upload -r testpypi dist/*

release: dist ## package and upload a release
	twine check dist/*
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install
