FROM ubuntu:18.04

RUN \
  apt update && \
  apt install -y git wget && \
  rm -rf /var/lib/apt/lists/*

ADD install.sh install.sh

RUN \
  apt update && \
  apt install -y virtualenv

RUN \
  bash ./install.sh

# Oy, there's a stray mysqlclient dependency :(
RUN \
  apt update && \
  apt-get install -y libmysqlclient-dev build-essential python3-dev libssl-dev

RUN \
  . venv/bin/activate && \
  pip install -r IRNet/requirements.txt

RUN \
  apt update && \
  apt install -y unzip

ADD requirements.txt requirements.txt

RUN \
  . venv/bin/activate && \
  pip install -r /requirements.txt

ADD setup.sh setup.sh

RUN \
  bash ./setup.sh

ADD serve.sh serve.sh

ADD server server

ADD example_data /valuenet/data/paulfitz

RUN \
  AUTOEXIT=1 bash ./serve.sh

CMD ["./serve.sh"]

EXPOSE 5050
