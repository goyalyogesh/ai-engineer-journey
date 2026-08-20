FROM python:3.13-slim

WORKDIR /app

# See mock_services/crm/Dockerfile for why the package path is recreated
# rather than switching to plain imports just for Docker.
RUN mkdir -p mock_services/provisioning && touch mock_services/__init__.py

COPY requirements.txt mock_services/provisioning/
RUN pip install --no-cache-dir -r mock_services/provisioning/requirements.txt

COPY . mock_services/provisioning/

EXPOSE 8003
CMD ["uvicorn", "mock_services.provisioning.main:app", "--host", "0.0.0.0", "--port", "8003"]
