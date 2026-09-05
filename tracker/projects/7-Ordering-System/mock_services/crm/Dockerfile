FROM python:3.13-slim

WORKDIR /app

# Build context is the repo root (docker-compose.yml), not this directory
# -- Phase 9 added a shared events/ package (events/producer.py) that
# every mock service's image now needs, so the whole repo is copied in
# rather than just this service's own subtree.

COPY mock_services/crm/requirements.txt mock_services/crm/requirements.txt
RUN pip install --no-cache-dir -r mock_services/crm/requirements.txt

COPY mock_services mock_services
COPY events events

EXPOSE 8001
CMD ["uvicorn", "mock_services.crm.main:app", "--host", "0.0.0.0", "--port", "8001"]
