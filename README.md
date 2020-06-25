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

```
# user credentials
admin:WiFiUnveIL
```

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

`2cc98f701bfc5633eae325eb56695e2c8ea88aff1a10ea5f14609e875165ab24`

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
