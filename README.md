# UNVEIL: Backend Service

## Environment setup

```bash
# download and install miniconda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda-latest-Linux-x86_64.sh
./Miniconda-latest-Linux-x86_64.sh
```

## Redis-Server

### Django RQ

Set user credentials in `docker-compose.yml` and same are used in `production.py`.

### RQ Workers

```
python manage.py rqworker data --settings=wifiservice.settings.production
python manage.py rqworker instructions --settings=wifiservice.settings.production
```

### RQ Scheduler

```
python manage.py rqscheduler --queue instructions -i 10 -v 3 --settings=wifiservice.settings.production
```

### RQ Dashboard

To debug and visualise redis-queue, we use [rq-dashboard](https://github.com/Parallels/rq-dashboard).

## Security Notes

### Password on Control Screen

1. User enters the password
2. Authentication on the server with the password and receives token for the session
3. Uses that token for each request

### Security for display screens

1. No check required if the requests are from IPs 146.169.10.*

### Security for Raspberry Pis

1. All should be token based authentication

### Security Implementation

1. A middleware which will rely on a table which will contain date of creation of token, token itself and for whom it is being used.
2. All requests should be logged.
3. A request will be accepted if coming from safe IPs, token will be returned if request is for that and passed if token is correct.

## Data Analysis

### ChromeDriver

```
sudo apt-get install chromium-chromedriver
```
