#!/bin/sh
# shellcheck shell=sh
set -e

psql "postgresql://$POSTGRES_USER@:5432/$POSTGRES_DB" -v ON_ERROR_STOP=1 <<-EOSQL
  CREATE USER siteplan_dev WITH PASSWORD 'secret';
  CREATE DATABASE siteplan_dev;
  GRANT ALL PRIVILEGES ON DATABASE siteplan_dev TO siteplan_dev;
  ALTER USER siteplan_dev SUPERUSER;
EOSQL

psql -v ON_ERROR_STOP=1 "postgresql://$POSTGRES_USER@:5432/siteplan_dev" <<-EOSQL
  CREATE EXTENSION IF NOT EXISTS pgcrypto;
  SELECT gen_random_uuid();
EOSQL
