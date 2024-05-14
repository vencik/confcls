.PHONY: setup init update test lint build mypy check build publish doc examples clean


setup:
	pyenv install --verbose --skip-existing
	pyenv local
	poetry config virtualenvs.in-project true

init:
	poetry install -E all

update:
	poetry update --lock
	poetry install -E all

test:
	poetry run pytest --verbose --color=yes tests

lint:
	poetry run pylint --rcfile=.pylintrc --exit-zero confcls -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"

mypy:
	poetry run mypy confcls --no-strict-optional --ignore-missing-imports --check-untyped-defs

check: test mypy lint

build:
	poetry build

publish:
	poetry publish

clean:
	rm -rf .mypy_cache .pytest_cache tests/*.xml .coverage dist .venv
