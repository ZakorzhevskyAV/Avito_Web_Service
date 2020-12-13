FROM python:3.8
WORKDIR .
COPY . .
RUN python -m pip install -r requirements.txt
EXPOSE 5000
EXPOSE 6379