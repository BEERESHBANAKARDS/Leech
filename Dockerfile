FROM anasty17/mltb:heroku

RUN mkdir ./app
RUN chmod 777 ./app
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

RUN apt -qq update --fix-missing && \
    apt -qq upgrade && \
    apt -qq install -y git \
    aria2 \
    wget \
    curl \
    busybox \
    unzip \
    unrar \
    tar \
    python3 \
    ffmpeg \
    python3-pip \
    p7zip-full \
    p7zip-rar \
    pv \
    jq \
    python3-dev \
    mediainfo

RUN wget https://rclone.org/install.sh
RUN bash install.sh

RUN mkdir /app/gautam
RUN wget -O /app/gautam/gclone.zip https://github.com/l3v11/gclone/releases/download/v1.59.0-abe/gclone-v1.59.0-abe-linux-amd64.zip
RUN gzip -d /app/gautam/gclone.zip
RUN chmod 0775 /app/gautam/gclone

RUN pip install -U pip

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash","start.sh"]
