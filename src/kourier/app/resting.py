# -*- encoding: utf-8 -*-
"""
KERI
kourier.app.resting package

"""
import json

import falcon
from hio.core import http
from keri.app import indirecting


def setup(host="127.0.0.1", port=8989, keypath=None, certpath=None, cafilepath=None):
    ####################################################################
    # Create / Configure your Database Here to inject to your handlers #
    ####################################################################

    app = falcon.App(middleware=falcon.CORSMiddleware(
        allow_origins='*', allow_credentials='*',
        expose_headers=['cesr-attachment', 'cesr-date', 'content-type', 'signature', 'signature-input',
                        'signify-resource', 'signify-timestamp']))
    server = indirecting.createHttpServer(host=host, port=port, app=app, keypath=keypath,
                                          certpath=certpath, cafilepath=cafilepath)
    serverDoer = http.ServerDoer(server=server)

    doers = [serverDoer]

    return doers
