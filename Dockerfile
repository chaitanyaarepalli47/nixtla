FROM python:latest

RUN mkdir /app

ADD . /app

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7000"]
