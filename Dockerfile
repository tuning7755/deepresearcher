FROM docker.m.daocloud.io/library/python:3.11-slim

WORKDIR /workspace

COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

COPY . /workspace

ENV PYTHONPATH=/workspace/src

EXPOSE 8000

CMD ["uvicorn", "deepresearcher.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
