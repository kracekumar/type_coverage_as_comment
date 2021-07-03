FROM python:3.9-slim AS builder
ADD . /app
WORKDIR /app

# We are installing a dependency here directly into our app source dir
RUN pip install --target=/app click===8.0.1 beautifulsoup4==4.9.3 lxml==4.6.3

# A distroless container image with Python and some basics like SSL certificates
# https://github.com/GoogleContainerTools/distroless
# FROM gcr.io/distroless/python3-debian10
FROM builder
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
ENTRYPOINT ["python", "/app/main.py"]
