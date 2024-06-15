FROM python:3

WORKDIR /app

COPY ./requirements.txt ./
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scheduler.py"]

EXPOSE 5001