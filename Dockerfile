FROM python:3.10

WORKDIR /line_bot

ADD . /line_bot

RUN pip install -r requirements.txt

CMD ["python3", "app.py"]