#!/bin/bash
set -e
DEF='\033[0m'
GRN='\033[0;32m'

cd /opt/starburger/
git pull -q
echo -e "Update repository -- ${GRN}OK${DEF}"
/root/.pyenv/versions/starburger/bin/pip install -r requirements.txt -q
echo -e "Update requirements -- ${GRN}OK${DEF}"
apt-get -yqq install nodejs
apt-get -yqq install npm
echo -e "Update nodejs -- ${GRN}OK${DEF}"
npm ci --dev --silent
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./" --log-level warn
echo -e "Rebuild frontend -- ${GRN}OK${DEF}"
/root/.pyenv/versions/starburger/bin/python manage.py collectstatic --noinput --verbosity=0
echo -e "Collect staticfiles -- ${GRN}OK${DEF}"
/root/.pyenv/versions/starburger/bin/python manage.py migrate --verbosity=0
echo -e "Accept migrations -- ${GRN}OK${DEF}"
systemctl reload nginx
echo -e "Reload nginx -- ${GRN}OK${DEF}"
echo -e "${GRN}UPDATE COMPLETE${DEF}"
