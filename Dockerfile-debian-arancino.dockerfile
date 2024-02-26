FROM python:3.11-slim-bookworm

# defining user 'me'
ARG user=me
ARG group=me
ARG uid=1000
ARG gid=1000
ARG ARANCINO_HOME=/home/me

ENV TZ 'Europe/Rome'

# Jenkins is run with user `jenkins`, uid = 1000
# If you bind mount a volume from the host or a data container,
# ensure you use the same uid
RUN mkdir -p $ARANCINO_HOME \
  && chown ${uid}:${gid} $ARANCINO_HOME \
  && groupadd -g ${gid} ${group} \
  && useradd -d "$ARANCINO_HOME" -u ${uid} -g ${gid} -m -s /bin/bash ${user} \
  && echo me:arancino | chpasswd \
  && echo root:arancino | chpasswd

# getting 'me' sudoer permissions
RUN echo "me ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        gnupg apt-transport-https  \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 

# adding arancino repository
COPY ./extras/arancino-os-public.key /tmp

RUN  echo "deb https://packages.smartme.io/repository/arancino-os-buster/ buster main" >> /etc/apt/sources.list.d/arancino.list \
    && apt-key add /tmp/arancino-os-public.key


RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        vim wget nano curl arduinostm32load \
        build-essential nano telnet net-tools  \
        systemd systemd-sysv bash-completion apt-utils \
        openocd avrdude dfu-util-stm32 bossa-cli \
        ca-certificates ca-cacert libssl-dev libyaml-dev \
        bluez \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 

RUN wget -qO- https://bootstrap.pypa.io/pip/get-pip.py | python3

COPY ./extras/pip.conf /etc/pip.conf

# Create a temporary directory in the Docker image
WORKDIR /tmp

# Copy the contents of tmp from the build context to the Docker image
COPY tmp/ .

# Estraggo il nome del file da pgk_name.txt
RUN ARANCINO_PACKAGE_FILE_DEBIAN=$(cat pgk_name.txt) \
    && echo "Using Arancino package file: $ARANCINO_PACKAGE_FILE_DEBIAN" \
    && pip3 install -v --no-cache-dir "$ARANCINO_PACKAGE_FILE_DEBIAN" adafruit-nrfutil


COPY ./config/arancino.cfg.yml /etc/arancino/config/arancino.cfg.yml
COPY ./config/arancino.dev.cfg /etc/arancino/config/arancino.dev.cfg


# copying upload tool scripts
COPY ./extras/run-arancino-bossac.sh /usr/bin/run-arancino-bossac
COPY ./extras/run-arancino-arduinoSTM32load.sh /usr/bin/run-arancino-arduinoSTM32load
COPY ./extras/run-arancino-adafruit-nrfutil.sh /usr/bin/run-arancino-adafruit-nrfutil
COPY ./extras/run-arancino-rp2040load.sh /usr/bin/run-arancino-rp2040load
COPY ./extras/run-arancino-uf2conv.sh /usr/bin/run-arancino-uf2conv
COPY ./extras/uf2conv.py /usr/bin/uf2conv.py
RUN chmod +x /usr/bin/run-arancino-*
RUN chmod +x /usr/bin/uf2conv.py

# Jenkins home directory is a volume, so configuration and build history
# can be persisted and survive image upgrades
VOLUME $ARANCINO_HOME

# USER ${user}

WORKDIR $ARANCINO_HOME

EXPOSE 1475
