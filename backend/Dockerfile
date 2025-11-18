# Dockerfile located at: backend/Dockerfile

# --- Stage 1: Build dependencies ---
FROM public.ecr.aws/amazonlinux/amazonlinux:2023 AS builder

RUN dnf install -y python3.11 python3.11-devel python3.11-pip gcc g++ make && \
    python3.11 -m pip install --upgrade pip

WORKDIR /app
COPY requirements.txt .
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt -t /app/deps

# --- Stage 2: Runtime ---
FROM public.ecr.aws/amazonlinux/amazonlinux:2023

RUN dnf install -y python3.11 python3.11-pip && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    python3 -m pip install --upgrade pip

WORKDIR /app

# Copy installed dependencies and source code
COPY --from=builder /app/deps /usr/local/lib/python3.11/site-packages
COPY app /app/app
COPY app/indexes.json /app/indexes.json
COPY requirements.txt .

ENV ATLAS_CSV_CFG="app/csv_path.json"
ENV INDEXES_CFG="app/indexes.json"


# Expose the port FastAPI will run on
EXPOSE 8080

# Command to run FastAPI
CMD ["python3", "-m", "uvicorn", "atlas_core.atlas_api:app", "--host", "0.0.0.0", "--port", "8080", "--app-dir", "app"]

