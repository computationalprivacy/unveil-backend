FROM continuumio/miniconda3:latest

# Copy files from the repository
COPY environment.yml /app/environment.yml

# Change work directory to files
WORKDIR /app

# Create conda environment with required creds
RUN conda env create -f environment.yml

# Install tcpdump for scapy and supervisor to manage services
RUN apt-get update && apt-get install --no-install-recommends -y \
    tcpdump supervisor chromium chromium-driver

# Create logging folder for supervisor
RUN mkdir -p /var/log/supervisor

# Copy requirements.txt file
COPY requirements.txt /app/requirements.txt

# Move your shell to conda environment
SHELL ["conda", "run", "-n", "wifibackend", "/bin/bash", "-c"]

# Install pip libraries
RUN pip install -r requirements.txt

# Copy wifiservice files
COPY wifiservice /app/wifiservice

COPY ./services/supervisord.conf /etc/supervisor/supervisord.conf

# Create logging folder for rqworker, rqscheduler and django
RUN mkdir -p /var/log/rqworker

RUN mkdir -p /var/log/rqscheduler

RUN mkdir -p /var/log/django

RUN mkdir -p /var/log/django-migrations

COPY ./services/rqworker.conf /etc/supervisor/supervisord/rqworker.conf

COPY ./services/rqscheduler.conf /etc/supervisor/supervisord/rqscheduler.conf

COPY ./services/django.conf /etc/supervisor/supervisord/django.conf

COPY ./services/django-migrations.conf /etc/supervisor/supervisord/django-migrations.conf

WORKDIR /app/wifiservice

CMD ["/usr/bin/supervisord"]