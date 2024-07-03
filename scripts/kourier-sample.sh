#!/bin/bash

[[ -z "${KOURIER_CONFIG_DIR}" ]] && ConfigDir="/opt/healthkeri/kourier/config" || ConfigDir="$${KOURIER_CONFIG_DIR}"
[[ -z "${KOURIER_HOST}" ]] && Host="0.0.0.0" || Host="$${KOURIER_HOST}"
[[ -z "${KOUORIER_BOOT_HOST}" ]] && BootHost="127.0.0.1" || BootHost="${WITOPNET_BOOT_HOST}"

source /opt/healthkeri/kourier/venv/bin/activate
kourier start --config-dir "${ConfigDir}" --host "${Host}" --boothost "${BootHost}"
