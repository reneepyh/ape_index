FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN playwright install --with-deps
CMD ["python", "run_pipeline.py"]