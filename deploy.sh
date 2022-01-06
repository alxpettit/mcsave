#!/usr/bin/env bash

source deploy.conf

SERVER_USER=${SERVER_USER:-root}
MAIN_PATH=${MAIN_PATH:-/opt}
PROJECT_NAME=${PROJECT_NAME:-mcsave}
RSYNC_ARGS=${RSYNC_ARGS:-}


SERVICE_FILE=${PROJECT_NAME}.service
SYSTEMD_PATH=${SYSTEMD_SYSTEM:-/etc/systemd/system}

rsync -Pavs . ${SERVER_USER}@${SERVER_DOMAIN}:${MAIN_PATH}/${PROJECT_NAME} ${RSYNC_ARGS}
rsync -Pavs ${SERVICE_FILE} ${SERVER_USER}@${SERVER_DOMAIN}:${SYSTEMD_PATH}/${SERVICE_FILE}
ssh ${SERVER_USER}@${SERVER_DOMAIN} \
	systemctl daemon-reload \&\& \
	systemctl enable --now ${PROJECT_NAME} \&\& \
	systemctl restart ${PROJECT_NAME} \&\& \
	sleep 0.5 \&\& \
	journalctl -xe -u ${PROJECT_NAME} --since='5\ minutes\ ago'
