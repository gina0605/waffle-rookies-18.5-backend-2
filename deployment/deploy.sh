#!/bin/bash

source ~/.bash_profile

cd ~/waffle-rookies-18.5-backend-2
git pull origin deploy

pyenv activate waffle-backend
pip install -r requirements.txt

cd waffle_backend
python manage.py migrate

python manage.py check --deploy

uwsgi --ini waffle-backend_uwsgi.ini

sudo nginx -t

sudo service nginx restart

