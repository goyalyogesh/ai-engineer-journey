FROM python:3.13-slim

WORKDIR /app

# See mock_services/crm/Dockerfile for why the package path is recreated
# rather than switching to plain imports just for Docker.
RUN mkdir -p mock_services/billing && touch mock_services/__init__.py

COPY requirements.txt mock_services/billing/
RUN pip install --no-cache-dir -r mock_services/billing/requirements.txt

COPY . mock_services/billing/

EXPOSE 8002
CMD ["uvicorn", "mock_services.billing.main:app", "--host", "0.0.0.0", "--port", "8002"]
