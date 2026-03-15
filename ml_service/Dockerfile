
FROM pytorch/pytorch:2.0.1-cpu
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn","inference:app","--host","0.0.0.0","--port","8001"]
