FROM python:3.10-slim
ENV STATIC_PATH="static/"
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python","./manage.py", "runserver", "0.0.0.0:8000" ]
