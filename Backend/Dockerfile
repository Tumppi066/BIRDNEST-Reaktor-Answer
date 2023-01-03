FROM python:3.7-alpine
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install fastapi
RUN pip install "uvicorn[standard]"
EXPOSE 8001
COPY . .
CMD ["uvicorn", "api:app", "--port", "8001"]