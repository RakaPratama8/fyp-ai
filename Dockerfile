FROM python:3.12-slim

# Install PostgreSQL C-bindings required by psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000. 
# Hugging Face Spaces strictly require applications to run as a non-root user.
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home environments
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install dependencies efficiently
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual AI python files
COPY --chown=user . .

# Hugging Face requires applications to boot strictly on Port 7860
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
