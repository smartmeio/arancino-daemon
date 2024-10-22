###########################################################
# arduinoSTM32load and rp2040load tools gobuilder Section #
###########################################################
FROM golang:1.17.3-alpine3.14 as gobuilder

RUN echo "cross-build-start-golang"


RUN apk update \
	&& apk add git make vim nano

RUN git clone https://github.com/artynet/arduino101load.git /arduinoSTM32load \
	&& cd /arduinoSTM32load \
	&& go build -o arduinoSTM32load

RUN git clone https://github.com/arduino/rp2040tools.git -b 1.0.3 /rp2040tools \
	&& cd /rp2040tools \
	&& go build -o rp2040load

RUN echo "cross-build-end-golang"

################################
# Upload tools builder Section #
################################
FROM alpine:3.14.2 as builder

RUN echo "cross-build-start"

RUN : \
	&& apk update \
	&& apk add vim wget nano curl git bash gcc g++ make \
	   autoconf m4 gettext libtool automake libusb libusb-dev \
	   gcc g++ make openssl libressl-dev musl-dev build-base \
	   bsd-compat-headers libc-dev bash-completion cmake \
	&& :

RUN git clone https://github.com/artynet/dfu-util-official.git -b smartme-stm32 dfu-util \
	&& cd /dfu-util \
	&& ./autogen.sh \
	&& ./configure \
	&& make -j3 \
	&& cd /

# build bossac
RUN git clone https://github.com/artynet/BOSSA.git -b arduino-alpine \
	&& cd /BOSSA \
	&& make bin/bossac \
	&& cd /

# build elf2uf2
RUN git clone https://github.com/raspberrypi/pico-sdk.git -b 1.3.0 pico-sdk \
	&& cd /pico-sdk/tools/elf2uf2 \
	&& mkdir build \
	&& cd build/ && cmake ../ \
	&& make \
	&& cd /

# build picotool
RUN git clone https://github.com/raspberrypi/picotool.git -b 1.1.0 picotool \
	&& cd /picotool \
	&& mkdir build \
	&& cd build/ && cmake -DPICO_SDK_PATH=/pico-sdk ../ \
	&& make \
	&& cd /


RUN echo "cross-build-end"

####################
# Arancino Section #
####################
FROM alpine:3.18.6

# RUN : \
#     && apk update \
#     && apk add vim wget nano curl python3 python3-dev linux-pam \
#        gcc musl-dev linux-headers procps coreutils bash shadow \
#        sudo net-tools libffi libffi-dev sed \
#        libusb libusb-dev libftdi1 libftdi1-dev avrdude openocd \
#        g++ make libressl-dev libc-dev  build-base \
#        bsd-compat-headers bash-completion cmake bluez\
#     && :

RUN : \
    && apk update \
    && apk add py3-pip python3-dev musl-dev gcc bluez linux-headers linux-pam bash\
    && :

RUN apk add 
ARG user=me
ARG group=me
ARG uid=1000
ARG gid=1000
ARG http_port=8080
ARG agent_port=50000
ARG ARANCINO_HOME=/home/me

ENV ARANCINO_HOME $ARANCINO_HOME
ENV ARANCINO=/etc/arancino
ENV ARANCINOCONF=/etc/arancino/config
ENV ARANCINOLOG=/var/log/arancino
ENV ARANCINOENV=PROD
ENV FLASK_ENV=production


# Arancino is run with user `me`, uid = 1000
# If you bind mount a volume from the host or a data container,
# ensure you use the same uid
RUN mkdir -p $ARANCINO_HOME \
  && chown ${uid}:${gid} $ARANCINO_HOME \
  && addgroup -g ${gid} ${group} \
  && adduser -h "$ARANCINO_HOME" -u ${uid} -G ${group} -s /bin/bash -D ${user} \
  && echo me:arancino | chpasswd \
  && echo root:arancino | chpasswd


# arduinoSTM32load copy from gobuilder
ENV BINDIR /usr/bin/
COPY --from=gobuilder /arduinoSTM32load/arduinoSTM32load "$BINDIR"

# rp2040load copy from gobuilder
COPY --from=gobuilder /rp2040tools/rp2040load "$BINDIR"

# bossac copy from builder
COPY --from=builder /BOSSA/bin/bossac "$BINDIR"

# dfu-util-stm32 copy from builder
COPY --from=builder /dfu-util/src/dfu-* "$BINDIR"

# elf2uf2 copy from builder
COPY --from=builder /pico-sdk/tools/elf2uf2/build/elf2uf2 "$BINDIR"

# picotool copy from builder
COPY --from=builder /picotool/build/picotool "$BINDIR"

COPY ./extras/pip.conf /etc/pip.conf

# copying upload tool scripts
COPY ./extras/uf2conv.py /usr/bin/uf2conv.py

COPY ./extras/run-arancino-bossac.sh /usr/bin/run-arancino-bossac
COPY ./extras/run-arancino-arduinoSTM32load.sh /usr/bin/run-arancino-arduinoSTM32load
COPY ./extras/run-arancino-adafruit-nrfutil.sh /usr/bin/run-arancino-adafruit-nrfutil
COPY ./extras/run-arancino-rp2040load.sh /usr/bin/run-arancino-rp2040load
COPY ./extras/run-arancino-uf2conv.sh /usr/bin/run-arancino-uf2conv
RUN chmod +x /usr/bin/run-arancino-*

# copying upload tool scripts
COPY ./extras/uf2conv.py /usr/bin/uf2conv.py

WORKDIR $ARANCINO_HOME/src

COPY . $ARANCINO_HOME/src

RUN pip3 install --no-cache-dir -r ./requirements.txt

RUN pip3 install . && pip3 cache purge 
RUN rm -r $ARANCINO_HOME/src

COPY ./config/arancino.cfg.yml /etc/arancino/config/arancino.cfg.yml
COPY ./config/arancino.dev.cfg /etc/arancino/config/arancino.dev.cfg
COPY ./config/gunicorn.cfg.py /etc/arancino/config/gunicorn.cfg.py

WORKDIR $ARANCINO_HOME/
EXPOSE 1475

ENTRYPOINT ["gunicorn","-c","/etc/arancino/config/gunicorn.cfg.py","arancino.ArancinoStart:app"]
