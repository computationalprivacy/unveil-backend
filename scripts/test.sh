#!/bin/bash

docker-compose -f docker-compose.yml up -d
cd wifiservice
python manage.py test ap_manager/ display_manager/ security_manager/

