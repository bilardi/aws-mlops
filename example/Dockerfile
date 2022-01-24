FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app
COPY requirements.txt requirements.txt
COPY processing.py processing.py

RUN apt-get update && apt-get install -y git
RUN curl https://bootstrap.pypa.io/get-pip.py | python
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt

# # only for testing with example/test_docker.sh
RUN mkdir -p /app/aws-mlops/example
RUN mkdir -p /opt/ml/processing/input
RUN mkdir -p /opt/ml/processing/test
RUN mkdir -p /opt/ml/processing/train
RUN mkdir -p /opt/ml/processing/validation
RUN mkdir -p /opt/ml/processing/score
RUN mkdir -p /opt/ml/processing/prediction
RUN mkdir -p /opt/ml/processing/report
COPY auto_with_pandas.py /app/aws-mlops/example/auto_with_pandas.py
COPY prep_with_pandas.py /app/aws-mlops/example/prep_with_pandas.py
COPY test_with_pandas.py /app/aws-mlops/example/test_with_pandas.py
COPY config.py /app/aws-mlops/example/config.py
COPY processing/raw_data/winequality-red.csv /opt/ml/processing/input/winequality-red.csv
COPY processing/new_data/winequality-white.csv /opt/ml/processing/input/winequality-white.csv
COPY processing/test_data/test.csv /opt/ml/processing/test/
COPY processing/prediction/test.csv.out /opt/ml/processing/score/
# # only for testing with example/test_docker.sh

ENTRYPOINT ["python3", "processing.py"]