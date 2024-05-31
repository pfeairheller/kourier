#!/bin/bash

kli init --name controller --salt 0ACDEyMzQ1Njc4OWxtbZctrl --nopasscode --config-dir ${KOURIER_SCRIPT_DIR} --config-file controller
kli incept --name controller --alias controller --file ${KOURIER_SCRIPT_DIR}/data/controller.json

MAILBOX=$(curl -s -XPOST http://localhost:9631/mailboxes -d'{"aid": "ENcOes8_t2C7tck4X4j61fSm0sWkLbZrEZffq7mSn8On"}' -H "Content-Type: application/json")

OOBI=$(echo "${MAILBOX}" | jq -r .oobis[0])
EID=$(echo "${MAILBOX}" | jq -r .eid)

echo "${OOBI}"
kli oobi resolve --name controller --oobi-alias mailbox0 --oobi "${OOBI}"

kli mailbox add --name controller --alias controller --mailbox "${EID}"

COOBI=$(kli oobi generate --name controller --alias controller --role mailbox)

kli init --name controller1 --salt 0ACDEyMzQ1Njc4OWxtbZctr1 --nopasscode --config-dir ${KOURIER_SCRIPT_DIR} --config-file controller
kli incept --name controller1 --alias controller1 --file ${KOURIER_SCRIPT_DIR}/data/controller.json

MAILBOX=$(curl -s -XPOST http://localhost:9631/mailboxes -d'{"aid": "EC4Np106NSu6y4SjMAFSCr1vjBRWYkEoh11dnDOJhA3q"}' -H "Content-Type: application/json")

OOBI=$(echo "${MAILBOX}" | jq -r .oobis[0])
EID=$(echo "${MAILBOX}" | jq -r .eid)

echo "${OOBI}"
kli oobi resolve --name controller1 --oobi-alias mailbox0 --oobi "${OOBI}"
kli oobi resolve --name controller1 --oobi-alias controller --oobi "${COOBI}"
kli mailbox add --name controller1 --alias controller1 --mailbox "${EID}"

COOBI=$(kli oobi generate --name controller1 --alias controller1 --role mailbox)
kli oobi resolve --name controller --oobi-alias controller1 --oobi "${COOBI}"

words1="$(kli challenge generate --out string)"
words2="$(kli challenge generate --out string)"

echo "Challenging controller with ${words1}"
kli challenge respond --name controller --alias controller --recipient controller1 --words "${words1}"
kli challenge verify --name controller1 --alias controller1 --signer controller --words "${words1}"

echo "Challenging controller1 with ${words2}"
kli challenge respond --name controller1 --alias controller1 --recipient controller --words "${words2}"
kli challenge verify --name controller --alias controller --signer controller1 --words "${words2}"

