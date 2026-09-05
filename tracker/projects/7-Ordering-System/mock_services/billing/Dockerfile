FROM python:3.13-slim

WORKDIR /app

# Build context is the repo root (docker-compose.yml), not this directory
# -- Phase 9 added a shared events/ package (events/producer.py) and a
# cross-service import (this service's _publish_seed_events() reads
# mock_services/crm/seed_data.py to resolve customer_id -> order_id), so
# the whole repo is copied in rather than just this service's own subtree.

COPY mock_services/billing/requirements.txt mock_services/billing/requirements.txt
RUN pip install --no-cache-dir -r mock_services/billing/requirements.txt

COPY mock_services mock_services
COPY events events

EXPOSE 8002
CMD ["uvicorn", "mock_services.billing.main:app", "--host", "0.0.0.0", "--port", "8002"]
