FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py pytest.ini ./
COPY config ./config
COPY .streamlit ./.streamlit
COPY sql ./sql
COPY src ./src
COPY data ./data
COPY tests ./tests
ENV CPD_RUNS_DIR=/app/runs PORT=8501
EXPOSE 8501
# Secrets/inputs (e.g. CPD_REFERENCE_DATE) come from Coolify-managed environment variables, never from the image.
CMD ["python", "app.py"]
