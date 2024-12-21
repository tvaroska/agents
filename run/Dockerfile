FROM langchain/langgraph-api:3.11



RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt langchain-community=^0.3.13 langchain-google-vertexai google-cloud-aiplatform

ADD ./accounts /deps/__outer_accounts/accounts
RUN set -ex && \
    for line in '[project]' \
                'name = "accounts"' \
                'version = "0.1"' \
                '[tool.setuptools.package-data]' \
                '"*" = ["**/*"]'; do \
        echo "$line" >> /deps/__outer_accounts/pyproject.toml; \
    done

RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt -e /deps/*

ENV LANGSERVE_GRAPHS='{"accounts": "/deps/__outer_accounts/accounts/agent.py:app"}'

