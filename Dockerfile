# Define Python version variables
ARG PYTHON_MINOR=3.15
ARG PYTHON_FULL=3.15.0a8
ARG DISTROLESS_TAG=3.14.4-debian13

##################
### base image ###
##################
FROM python:${PYTHON_FULL}-slim AS base
ARG PYTHON_MINOR
ARG PYTHON_FULL
ARG DISTROLESS_TAG

# Create directories for easy cross-architecture support.
# This makes `COPY` work easily for 64-bit ARM and x86, and creates our app dir.
RUN mkdir -p \
    /lib/aarch64-linux-gnu \
    /usr/lib/aarch64-linux-gnu \
    /lib/x86_64-linux-gnu \
    /usr/lib/x86_64-linux-gnu \
    /etc/fonts \
    /usr/share/fonts/ \
    /usr/share/fontconfig/ \
    /app/.venv \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to use for `/app/.venv`.
RUN useradd --create-home appuser && chown appuser:appuser /app/.venv
WORKDIR /app

# Copy files for `uv` including README.
COPY --chown=appuser:appuser pyproject.toml uv.lock README.md LICENSE /app/

USER appuser

ENV PYTHONPATH="/usr/local/lib/python${PYTHON_MINOR}/site-packages:/app/.venv/lib/python${PYTHON_MINOR}/site-packages:/app"

# Create a real venv, install uv into it, then sync runtime deps.
RUN python -m venv /app/.venv \
    && /app/.venv/bin/pip install uv==0.11.8 \
    && UV_PROJECT_ENVIRONMENT=/app/.venv /app/.venv/bin/uv sync --locked --no-group dev --no-install-project

ENTRYPOINT ["/app/.venv/bin/python"]
CMD ["-m", "pie"]

##################
### dev image  ###
##################
FROM base AS dev
ARG PYTHON_MINOR
ARG PYTHON_FULL

USER appuser

# Install development dependencies.
RUN UV_PROJECT_ENVIRONMENT=/app/.venv \
    /app/.venv/bin/uv sync --locked --no-install-project

##################
### prod image ###
##################
# Distroless has no 3.15.0a8 tag. Start from newer Debian 13 distroless image,
# then overlay the full /usr/local runtime from the 3.15.0a8 base image.
FROM al3xos/python-distroless:${DISTROLESS_TAG} AS prod
ARG PYTHON_MINOR
ARG PYTHON_FULL
ARG DISTROLESS_TAG

ARG RELEASE_VERSION
ENV RELEASE_VERSION=${RELEASE_VERSION}

# Copy basic Linux architecture files from the base image.
COPY --from=base /lib/aarch64-linux-gnu/ /lib/aarch64-linux-gnu/
COPY --from=base /usr/lib/aarch64-linux-gnu/ /usr/lib/aarch64-linux-gnu/
COPY --from=base /lib/x86_64-linux-gnu/ /lib/x86_64-linux-gnu/
COPY --from=base /usr/lib/x86_64-linux-gnu/ /usr/lib/x86_64-linux-gnu/
COPY --from=base /lib64/ /lib64/
# Copy fonts for text rendering tools.
COPY --from=base /etc/fonts/ /etc/fonts/
COPY --from=base /usr/share/fonts/ /usr/share/fonts/
COPY --from=base /usr/share/fontconfig/ /usr/share/fontconfig/

# Overlay CPython 3.15.0a8 runtime and stdlib from the base image.
COPY --from=base /usr/local/ /usr/local/

# Copy the `uv` installed application dependencies.
COPY --from=base /app/.venv /app/.venv

ENV PYTHONPATH="/usr/local/lib/python${PYTHON_MINOR}/site-packages:/app/.venv/lib/python${PYTHON_MINOR}/site-packages:/app"

COPY --chown=monty:monty . /app

ENTRYPOINT ["/app/.venv/bin/python"]
CMD ["-m", "pie"]
