FROM python:3.10-buster 

COPY requirements.txt .
RUN sed -i 's,psycopg2,psycopg2-binary,g' requirements.txt && \
    pip install -r requirements.txt 

COPY . .
EXPOSE 5000
ENV FLASK_APP=streak.main:app
ENTRYPOINT ["flask", "run"]
