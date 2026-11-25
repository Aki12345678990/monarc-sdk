FROM python:3.12-slim

WORKDIR /app

# Headless JRE for apktool. python:3.12-slim's apt repo provides openjdk-17-jre-headless.
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# Official apktool 2.12.1. The SHA-256 is the local frozen jar
# E:\AndroZoo\tools\apktool\apktool_2.12.1.jar. The build fails on mismatch.
RUN mkdir -p /opt/apktool \
    && curl -fsSL -o /opt/apktool/apktool_2.12.1.jar \
        https://github.com/iBotPeaches/Apktool/releases/download/v2.12.1/apktool_2.12.1.jar \
    && echo "66cf4524a4a45a7f56567d08b2c9b6ec237bcdd78cee69fd4a59c8a0243aeafa  /opt/apktool/apktool_2.12.1.jar" | sha256sum -c - \
    && java -jar /opt/apktool/apktool_2.12.1.jar --version | grep -qx 2.12.1

COPY pyproject.toml requirements.txt requirements-service.txt ./
COPY src/ src/
COPY data/reference/ data/reference/

RUN pip install --no-cache-dir -r requirements-service.txt \
    && pip install --no-cache-dir --no-deps .

ENV ANALYZER_REFERENCE_DIR=/app/data/reference \
    ANALYZER_SVC_VAR_DIR=/data \
    ANALYZER_SVC_HOST=0.0.0.0 \
    ANALYZER_MAX_APK_BYTES=157286400 \
    ANALYZER_JAVA=/usr/bin/java \
    ANALYZER_APKTOOL_JAR=/opt/apktool/apktool_2.12.1.jar \
    PYTHONUNBUFFERED=1

# The image is unusable unless reference verification prints OK.
RUN python -m analyzer_core verify-reference > /tmp/verify-reference.txt \
    && grep -qx OK /tmp/verify-reference.txt

CMD ["python", "-m", "analyzer_service", "serve"]
