FROM python:3.11-slim

WORKDIR /app
COPY webhook_listener.py .

RUN pip install fastapi uvicorn requests pytz

ENV VIKUNJA_API=https://your-vikunja-instance/api/v1
ENV VIKUNJA_USERNAME=your-username
ENV VIKUNJA_PASSWORD=your-password

CMD ["uvicorn", "webhook_listener:app", "--host", "0.0.0.0", "--port", "8000"]
