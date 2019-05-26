# latest is not actually the most recent, currently
FROM vzhong/corenlp-server:latest

RUN \
  mkdir -p /var/cache/apt/archives/partial && \
  apt update && \
  apt install -y git

# we need python 3.6 because sqlova uses f strings
RUN \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt update && \
  apt install -y python3.6

# Get pip (for 3.5, but python 3.6 will be able to share it)
RUN \
  apt update && \
  apt install -y python3-pip && \
  pip3 install --upgrade pip

# ujson has some native code to be compiled
RUN \
  apt install -y python3.6-dev

RUN mkdir -p /opt/sqlova-deps
WORKDIR /opt/sqlova-deps

ADD requirements.txt requirements.txt

RUN \
  python3.6 -m pip install -r requirements.txt

# brutal but handy
RUN \
  ln -s /usr/bin/python3.6 /usr/bin/python && \
  rm /usr/bin/python3 && \
  ln -s /usr/bin/python3.6 /usr/bin/python3

RUN mkdir -p /opt/sqlova
WORKDIR /opt/sqlova

RUN \
  cd /opt && \
  git clone https://github.com/paulfitz/sqlova/ -b add_plain_prediction

RUN mkdir -p /share
WORKDIR /share

# run corenlp-server
CMD ["/sbin/my_init"]

