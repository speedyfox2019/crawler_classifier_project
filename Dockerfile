FROM ubuntu:20.04

# We need wget to set up the PPA and xvfb to have a virtual screen and unzip to install the Chromedriver
RUN apt-get -y update
RUN apt-get install -y wget xvfb unzip gnupg2 python3.8

# Set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update the package list and install chrome
RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends google-chrome-stable

# Set up Chromedriver Environment variables
ENV CHROMEDRIVER_VERSION 95.0.4638.54
ENV CHROMEDRIVER_DIR /opt/chromedriver/$CHROMEDRIVER_VERSION
RUN mkdir -p $CHROMEDRIVER_DIR

# Download and install Chromedriver
RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# Setup the location for the virtual env, then insert into $PATH for running pip
RUN apt install -y python3.8-venv
ENV VIRTUAL_ENV=/opt/crawler_venv
RUN python3.8 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR:$PATH

# Known to have problem when running Docker on Windows host
RUN apt-get install -y dos2unix

COPY app.py .
