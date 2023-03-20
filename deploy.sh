#!/bin/bash
set -e
DEF='\033[0m'
GRN='\033[0;32m'

cd $PWD
git pull -q
echo -e "Update repository -- ${GRN}OK${DEF}"
$PYENV_ROOT/versions/starburger/bin/pip install -r requirements.txt -q
echo -e "Update requirements -- ${GRN}OK${DEF}"
npm ci --dev --silent
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./" --log-level warn
echo -e "Rebuild frontend -- ${GRN}OK${DEF}"
$PYENV_ROOT/versions/starburger/bin/python manage.py collectstatic --noinput --verbosity=0
echo -e "Collect staticfiles -- ${GRN}OK${DEF}"
$PYENV_ROOT/versions/starburger/bin/python manage.py migrate --verbosity=0
echo -e "Accept migrations -- ${GRN}OK${DEF}"
systemctl reload nginx
echo -e "Reload nginx -- ${GRN}OK${DEF}"

GIT_SHA=$(git rev-parse HEAD)
curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header "X-Rollbar-Access-Token: ${ROLLBAR_TOKEN}" \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "environment": "production",
  "revision": "'$GIT_SHA'",
  "local_username": "'$USER'"
}
' > /dev/null
echo -e "Send to rollbar -- ${GRN}OK${DEF}"
echo -e "${GRN}UPDATE COMPLETE${DEF}"
