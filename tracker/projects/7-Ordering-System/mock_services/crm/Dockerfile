FROM python:3.13-slim

WORKDIR /app

# Recreate the mock_services.crm package path inside the image so the
# relative imports in main.py (from .db import ...) resolve exactly the
# way they do in local dev/tests (04-BUILD-PLAN.md's repo structure) --
# deliberately not switching to plain imports just for Docker, which would
# make the container behave differently from local uvicorn runs.
RUN mkdir -p mock_services/crm && touch mock_services/__init__.py

COPY requirements.txt mock_services/crm/
RUN pip install --no-cache-dir -r mock_services/crm/requirements.txt

COPY . mock_services/crm/

EXPOSE 8001
CMD ["uvicorn", "mock_services.crm.main:app", "--host", "0.0.0.0", "--port", "8001"]
