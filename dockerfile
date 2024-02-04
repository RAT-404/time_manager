FROM python:3.11-slim-bookworm
EXPOSE 8000
COPY . /code
WORKDIR /code
RUN pip install -r ./requirements.txt
WORKDIR /code/app/backend
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
