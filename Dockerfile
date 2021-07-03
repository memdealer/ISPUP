FROM python:3.8
WORKDIR app
COPY ./ISPup /app/
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
