FROM python:3.11-slim

# Set the working directory
WORKDIR /usr/src/app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files and install
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD [ "python", "src/app.py" ]
