#!/bin/bash
set -e
DEF='\033[0m'
GRN='\033[0;32m'

cd $PWD
git pull -q
echo -e "Update repository -- ${GRN}OK${DEF}"

docker-compose up --build -d

echo -e "Compose build -- ${GRN}OK${DEF}"

GIT_SHA=$(git rev-parse HEAD)
curl -s --request POST \
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