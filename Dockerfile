FROM python:3.10-slim

WORKDIR /app

COPY crypto_notifier/requirements.txt .

RUN pip install -r ./requirements.txt

COPY . .

CMD ["python", "crypto_notifier/run.py", "--log-level", "INFO", "--log-path", "/var/log/bot.log"]
