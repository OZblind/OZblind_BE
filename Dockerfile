FROM python:3.13-slim

# uv 설치
RUN pip install --no-cache-dir uv

# 환경 변수
ENV PATH="/app/.venv/bin:${PATH}" \
PYTHONDONTWRITEBYTECODE=1 \
PYTHONUNBUFFERED=1

WORKDIR /app

# 의존성 설치
COPY pyproject.toml uv.lock /app/

COPY backend /app/backend

COPY manage.py /app/
RUN uv pip install --system --no-cache .