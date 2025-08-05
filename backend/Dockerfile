FROM python:3.13-slim

# uv 설치
RUN pip install --no-cache-dir uv

# 환경 변수
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 의존성 설치
COPY pyproject.toml /app/
COPY uv.lock /app/
RUN uv pip install --system --no-cache

# 프로젝트 복사
COPY . /app/

# 개발 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
