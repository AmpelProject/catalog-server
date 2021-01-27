#!/bin/sh

mongorestore --host 127.0.0.1 --port 27017 -d milliquas /docker-entrypoint-initdb.d/milliquas
