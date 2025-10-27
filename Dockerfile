FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

RUN find /usr/local -type f -name "*.pyc" -delete \
    && find /usr/local -type d -name "__pycache__" -delete

CMD ["bash"]
