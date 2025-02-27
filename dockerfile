FROM python:3.9-slim

WORKDIR /app

COPY imagesplit.py /app/
COPY requirements.txt /app/

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "imagesplit.py", "--server.port=8501", "--server.address=0.0.0.0"]