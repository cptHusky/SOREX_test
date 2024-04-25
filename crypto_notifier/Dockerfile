FROM python:3.9-slim

WORKDIR /crypto_notifier_container

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "crypto_notifier/run.py", "--log-level", "INFO", "--log-path", "bot.log"]
