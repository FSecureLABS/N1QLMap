#!/bin/bash
docker-compose run -d --service-ports --name n1ql-couchbase n1ql-nodejs
echo 'Waiting 30 secs on Couchbase container...'
sleep 30
docker restart n1ql-couchbase # restart docker instance when couchbase ready
curl -X POST -u Administrator:password -d '{"all_access": true, "allowed_urls": ["*"], "disallowed_urls": []}' http://localhost:8091/settings/querySettings/curlWhitelist
echo 'Everything should be ready, run docker restart n1ql-couchbase if any connection problem occurs'
echo 'http://localhost:3000/'
