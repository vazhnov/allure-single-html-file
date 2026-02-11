FROM python:3.11-slim

ARG ALLURE_VERSION=2.29.0
ENV DEBIAN_FRONTEND=noninteractive
ENV ALLURE_HOME=/opt/allure-${ALLURE_VERSION}
ENV PATH="${ALLURE_HOME}/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        openjdk-21-jre-headless \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/${ALLURE_VERSION}/allure-commandline-${ALLURE_VERSION}.tgz" \
      -o /tmp/allure-commandline.tgz \
    && tar -xzf /tmp/allure-commandline.tgz -C /opt \
    && ln -s "/opt/allure-${ALLURE_VERSION}/bin/allure" /usr/local/bin/allure \
    && rm -f /tmp/allure-commandline.tgz

WORKDIR /workspace
COPY . /workspace

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir pytest allure-pytest \
    && pip install --no-cache-dir .

CMD ["/workspace/integration_tests/run_dummy_allure.sh"]
