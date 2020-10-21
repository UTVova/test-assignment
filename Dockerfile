FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV input="resources/test.xml"
ENV output="resources/test-output.csv"

WORKDIR /app/

RUN pip install poetry==1.1.3

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install --no-dev

COPY attendance_analyzer/ ./attendance_analyzer/

ENTRYPOINT ["python", "-m", "attendance_analyzer"]
