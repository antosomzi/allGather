FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app/

# Install system dependencies for PostGIS and geospatial libraries
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libmagic1 \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

ENV PYTHONPATH=/app

# Copy application files
COPY ./driver_score /app/driver_score
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/
COPY ./configs /app/configs

# Copy and setup prestart script for database migrations
COPY ./prestart.sh /app/prestart.sh
RUN chmod +x /app/prestart.sh

# Set the module to run
ENV MODULE_NAME=driver_score.app
ENV VARIABLE_NAME=app
