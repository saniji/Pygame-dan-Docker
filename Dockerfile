FROM python:slim

ENV DEBIAN_FRONTEND = noneinteractive

RUN apt-get update && apt-get upgrade -y
RUN apt update
RUN apt install -qqy x11-apps
RUN apt install -y xserver-xorg
RUN pip3 install pygame

WORKDIR /home/user