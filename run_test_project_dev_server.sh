#!/usr/bin/env bash

set -e

cd pylucid_page_instance

while true
do
(
    clear
    echo "====================================================================="
    set +e
    (
        set -x
        ./manage.py run_test_project_dev_server $*
        sleep 2
    )
)
done
