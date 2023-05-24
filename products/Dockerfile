FROM alpine:latest
RUN apk update
RUN apk add py-pip
RUN apk add --no-cache python3-dev 
RUN pip install --upgrade pip
WORKDIR /app_cont
COPY . /app_cont

RUN mkdir db
RUN cp products.db db

RUN pip --no-cache-dir install -r requirements.txt
COPY app.py app.py
EXPOSE 8888/tcp
CMD ["python3", "app.py"]
