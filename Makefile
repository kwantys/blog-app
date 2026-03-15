# ──────────────────────────────────────────────
#  Blog App — Makefile
#  Використання:  make <target>
#  Приклад:       make install
# ──────────────────────────────────────────────

VENV      = .venv
PYTHON    = $(VENV)/bin/python
PIP       = $(VENV)/bin/pip
FLASK_APP = run.py

# Windows-сумісність: якщо команда не знайдена — використати системний python
ifeq ($(OS), Windows_NT)
	PYTHON = $(VENV)/Scripts/python
	PIP    = $(VENV)/Scripts/pip
endif

.PHONY: all install run test lint clean help

## help : вивести цей список команд
help:
	@echo ""
	@echo "  Доступні команди:"
	@grep -E '^## ' Makefile | sed 's/## /    make /'
	@echo ""

## all : встановити залежності та запустити тести
all: install test

## install : створити venv та встановити всі залежності
install:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "  Залежності встановлено."
	@echo "  Скопіюйте .env.example → .env і встановіть SECRET_KEY"
	@echo ""

## run : запустити додаток у режимі розробки
run:
	$(PYTHON) $(FLASK_APP)

## test : запустити всі тести
test:
	$(VENV)/bin/pytest tests/ -v

## lint : перевірити якість коду (flake8)
lint:
	$(VENV)/bin/flake8 app/ config.py run.py \
		--max-line-length=100 \
		--exclude=__pycache__,.venv

## clean : видалити згенеровані файли та кеш
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.db"  -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
	@echo "  Clean done."
