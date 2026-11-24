FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml requirements.txt requirements-service.txt ./
COPY src/ src/
COPY data/reference/ data/reference/

RUN pip install --no-cache-dir -r requirements-service.txt \
    && pip install --no-cache-dir --no-deps .

ENV ANALYZER_REFERENCE_DIR=/app/data/reference \
    ANALYZER_SVC_VAR_DIR=/data \
    ANALYZER_SVC_HOST=0.0.0.0 \
    ANALYZER_MAX_APK_BYTES=157286400 \
    PYTHONUNBUFFERED=1

# The image is unusable unless reference verification prints OK.
RUN python -m analyzer_core verify-reference > /tmp/verify-reference.txt \
    && grep -qx OK /tmp/verify-reference.txt

CMD ["python", "-m", "analyzer_service", "serve"]
