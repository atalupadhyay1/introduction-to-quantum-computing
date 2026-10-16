# QC101 — Quantum Computing & Introduction to Quantum Machine Learning
#
#   make            list every target
#   make selftest   run the shared-library test suite          (~2 s)
#   make labs       run all 17 labs                             (~100 s)
#   make site       build the interactive study site
#   make site-check verify the site is complete and self-consistent
#   make serve      serve the study site on http://localhost:8000
#   make check      everything that must pass (selftest + labs + site)
#
# PYTHON can be overridden:  make labs PYTHON=python3.12

PYTHON ?= python3
PORT   ?= 8000

.DEFAULT_GOAL := help
.PHONY: help selftest labs lab site site-check serve quiz quiz-list progress \
        notebooks quizbank check clean all distclean

help: ## Show this help
	@echo ""
	@echo "  QC101 study companion"
	@echo "  --------------------"
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
selftest: ## Run the shared qc101 library test suite (167 checks)
	$(PYTHON) labs/common/qc101/selftest.py

labs: ## Run all 17 labs (summary)
	$(PYTHON) tools/labcheck.py

lab: ## Run one lab, e.g. make lab LAB=L07
	@test -n "$(LAB)" || (echo "usage: make lab LAB=L07" && exit 1)
	$(PYTHON) labs/$(LAB)_*/lab.py

check: selftest labs site-check ## Run the full test suite (library + labs + site)

# ---------------------------------------------------------------------------
# Study site
# ---------------------------------------------------------------------------
site: ## Build the study site into site/content
	$(PYTHON) tools/build_site.py

site-check: ## Verify the study site is complete and self-consistent
	$(PYTHON) tools/site_check.py

serve: ## Serve the study site on http://localhost:$(PORT)
	@echo "  study site -> http://localhost:$(PORT)   (Ctrl-C to stop)"
	$(PYTHON) -m http.server $(PORT) --bind 0.0.0.0 --directory site

# ---------------------------------------------------------------------------
# Quizzes and progress
# ---------------------------------------------------------------------------
quiz: ## Interactive quiz (mixes sections)
	$(PYTHON) tools/quiz.py

quiz-list: ## List every question in the bank
	$(PYTHON) tools/quiz.py --list

progress: ## Show your progress dashboard
	$(PYTHON) tools/progress.py

# ---------------------------------------------------------------------------
# Generators (the checked-in artefacts are already up to date)
# ---------------------------------------------------------------------------
quizbank: ## Regenerate quizzes/questions/*.json
	$(PYTHON) tools/make_quiz_bank.py

notebooks: ## Regenerate notebooks/*.ipynb
	$(PYTHON) tools/make_notebooks.py

# ---------------------------------------------------------------------------
# Housekeeping
# ---------------------------------------------------------------------------
all: selftest labs site site-check ## Everything: tests + site build + site check

clean: ## Remove caches and build artefacts
	find . -path ./.venv -prune -o -name '__pycache__' -type d -print0 | xargs -0 rm -rf 2>/dev/null || true
	find . -path ./.venv -prune -o -name '*.pyc' -type f -delete 2>/dev/null || true
	rm -rf site/content

distclean: clean ## Also remove the recorded progress
	rm -f progress/lab_results.json progress/quiz_results.json
