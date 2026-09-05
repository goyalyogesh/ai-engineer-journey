FROM python:3.13-slim

WORKDIR /app

# Build context is the repo root (docker-compose.yml), not this directory
# -- widened for consistency with the other 3 mock services' Dockerfiles
# (Phase 9), even though this service doesn't need events/ or any sibling
# mock_services/* package today.

COPY mock_services/inventory/requirements.txt mock_services/inventory/requirements.txt
RUN pip install --no-cache-dir -r mock_services/inventory/requirements.txt

COPY mock_services/inventory mock_services/inventory
COPY mock_services/__init__.py mock_services/__init__.py

EXPOSE 8004
CMD ["uvicorn", "mock_services.inventory.main:app", "--host", "0.0.0.0", "--port", "8004"]
