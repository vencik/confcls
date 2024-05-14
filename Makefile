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
	rm -rf dist
	asciidoctor -b docbook -a leveloffset=+1 -o - README.adoc | pandoc  --atx-headers --wrap=preserve -t markdown_strict -f docbook - > README.md
	poetry build

publish:
	poetry run twine upload dist/*

clean:
	rm -rf .mypy_cache .pytest_cache tests/*.xml .coverage dist .venv
