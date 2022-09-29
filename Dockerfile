FROM selenium/standalone-chrome
RUN sudo apt update && sudo apt install -y python3-pip
RUN cd /usr/bin && sudo ln -s python3 python
