#!/bin/bash
# A convenience wrapper for manage.py
#
# This should be equivalent to running:
# sudo -u www-data PYTHONPATH=$PYTHONPATH:`pwd` DJANGO_SETTINGS_MODULE=lms.envs.aws ../venvs/bin/python ./manage.py lms $@

WORKING_DIR="/edx/app/edxapp"
PLATFORM_DIR="${WORKING_DIR}/edx-platform"
VENV_BIN="${WORKING_DIR}/venvs/edxapp/bin"

SERVICE_VARIANT="lms"
PYTHONPATH="${PYTHONPATH}:${PLATFORM_DIR}"
DJANGO_SETTINGS_MODULE="${SERVICE_VARIANT}.envs.aws"

GUNICORN_USER="www-data"

cd ${PLATFORM_DIR}
source ${VENV_BIN}/activate
export SERVICE_VARIANT PYTHONPATH DJANGO_SETTINGS_MODULE

/usr/bin/sudo -E -u ${GUNICORN_USER} ${VENV_BIN}/python ${PLATFORM_DIR}/manage.py ${SERVICE_VARIANT} ${@}
