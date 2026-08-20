FROM python:3.13-slim

WORKDIR /app

# See mock_services/crm/Dockerfile for why the package path is recreated
# rather than switching to plain imports just for Docker.
RUN mkdir -p mock_services/inventory && touch mock_services/__init__.py

COPY requirements.txt mock_services/inventory/
RUN pip install --no-cache-dir -r mock_services/inventory/requirements.txt

COPY . mock_services/inventory/

EXPOSE 8004
CMD ["uvicorn", "mock_services.inventory.main:app", "--host", "0.0.0.0", "--port", "8004"]
