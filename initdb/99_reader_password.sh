#!/bin/bash
# Sets the read-only Connect login's password from the container environment (docker run --env-file bible.env),
# so no password is stored in the repository. Runs last (99_), after 01_schema.sql has created the role.
set -euo pipefail
: "${TIMEBASE_READER_PASSWORD:?TIMEBASE_READER_PASSWORD must be set (see bible.env)}"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
     -v pw="$TIMEBASE_READER_PASSWORD" <<'SQL'
ALTER ROLE timebase_reader PASSWORD :'pw';
SQL
