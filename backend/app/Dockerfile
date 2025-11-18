# --- Stage 1: Build with compilers ---
FROM amazonlinux:2023 AS builder

# Install required build tools and Python 3.11
RUN yum install -y python3.11 python3.11-devel gcc gcc-c++ make && \
    python3.11 -m ensurepip && \
        python3.11 -m pip install --upgrade pip

# Set workdir and copy requirements
WORKDIR /app
COPY requirements.txt .

# Install dependencies into /app/python
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt -t /app/python

# --- Stage 2: Lambda runtime ---
FROM public.ecr.aws/lambda/python:3.11

# Copy built Python dependencies
COPY --from=builder /app/python ${LAMBDA_TASK_ROOT}

# Copy application code
COPY app ${LAMBDA_TASK_ROOT}/app

# ✅ Ensure indexes.json is placed correctly
COPY app/indexes.json ${LAMBDA_TASK_ROOT}/indexes.json

# Set the Lambda handler
CMD ["app.handler.lambda_handler"]

