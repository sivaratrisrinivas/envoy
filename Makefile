PYTHON := ./.venv/bin/python
PYTEST := PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(PYTHON) -m pytest

.PHONY: bootstrap dev test seed send-hero send-backup replay reset-preview deploy-preview

bootstrap:
	$(PYTHON) scripts/bootstrap.py

dev:
	$(PYTHON) -m uvicorn app.main:app --reload

test:
	$(PYTEST)

seed:
	$(PYTHON) scripts/seed_demo.py

send-hero:
	$(PYTHON) scripts/send_event.py --scenario hero_job_change

send-backup:
	$(PYTHON) scripts/send_event.py --scenario backup_job_change

replay:
	$(PYTHON) scripts/replay_event.py $(EVENT_ID)

reset-preview:
	$(PYTHON) scripts/reset_preview.py --confirm $(CONFIRM)

deploy-preview:
	$(PYTHON) scripts/deploy_preview.py
