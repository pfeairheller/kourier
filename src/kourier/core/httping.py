# -*- encoding: utf-8 -*-

"""
KERI
kourier.core.httping package

"""

import falcon
from keri import kering
from keri.app import httping
from keri.app.httping import CESR_DESTINATION_HEADER
from keri.app.indirecting import MailboxIterable
from keri.core import coring
from keri.help import ogler
from keri.kering import Ilks

logger = ogler.getLogger()


def loadEnds(app, kry):
    http = HttpEnd(kry=kry)
    app.add_route("/", http)


class HttpEnd:
    """
    HTTP handler that accepts and KERI events POSTed as the body of a request with all attachments to
    the message as a CESR attachment HTTP header.  KEL Messages are processed and added to the database
    of the provided Habitat.

    This also handles `req`, `exn` and `tel` messages that respond with a KEL replay.
    """

    def __init__(self, kry, rxbs=None):
        """
        Create the KEL HTTP server from the Habitat with an optional Falcon App to
        register the routes with.

        Parameters
             rxbs (bytearray): output queue of bytes for message processing

        """
        self.kry = kry
        self.rxbs = rxbs if rxbs is not None else bytearray()

    def on_post(self, req, rep):
        """
        Handles POST for KERI event messages.

        Parameters:
              req (Request) Falcon HTTP request
              rep (Response) Falcon HTTP response

        ---
        summary:  Accept KERI events with attachment headers and parse
        description:  Accept KERI events with attachment headers and parse.
        tags:
           - Events
        requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 description: KERI event message
        responses:
           200:
              description: Mailbox query response for server sent events
           204:
              description: KEL or EXN event accepted.
        """
        if req.method == "OPTIONS":
            rep.status = falcon.HTTP_200
            return

        if CESR_DESTINATION_HEADER not in req.headers:
            raise falcon.HTTPBadRequest(title="CESR request destination header missing")

        aid = req.headers[CESR_DESTINATION_HEADER]
        kourier = self.kry.lookup(aid)
        if kourier is None:
            raise falcon.HTTPNotFound(title=f"unknown destination AID {aid}")

        rep.set_header('Cache-Control', "no-cache")
        rep.set_header('connection', "close")

        cr = httping.parseCesrHttpRequest(req=req)
        sadder = coring.Sadder(ked=cr.payload, kind=kering.Kinds.json)
        msg = bytearray(sadder.raw)
        msg.extend(cr.attachments.encode("utf-8"))

        kourier.parser.parseOne(ims=msg, local=True)

        if sadder.proto in ("ACDC",):
            rep.set_header('Content-Type', "application/json")
            rep.status = falcon.HTTP_204
        else:
            ilk = sadder.ked["t"]
            if ilk in (Ilks.icp, Ilks.rot, Ilks.ixn, Ilks.dip, Ilks.drt, Ilks.exn, Ilks.rpy):
                rep.set_header('Content-Type', "application/json")
                rep.status = falcon.HTTP_204
            elif ilk in (Ilks.vcp, Ilks.vrt, Ilks.iss, Ilks.rev, Ilks.bis, Ilks.brv):
                rep.set_header('Content-Type', "application/json")
                rep.status = falcon.HTTP_204
            elif ilk in (Ilks.qry,):
                if sadder.ked["r"] in ("mbx",):
                    rep.set_header('Content-Type', "text/event-stream")
                    rep.status = falcon.HTTP_200
                    rep.stream = QryRpyMailboxIterable(kourier=kourier, said=sadder.said)
                else:
                    rep.set_header('Content-Type', "application/json")
                    rep.status = falcon.HTTP_204

    def on_put(self, req, rep):
        """
        Handles PUT for KERI mbx event messages.

        Parameters:
              req (Request) Falcon HTTP request
              rep (Response) Falcon HTTP response

        ---
        summary:  Accept KERI events with attachment headers and parse
        description:  Accept KERI events with attachment headers and parse.
        tags:
           - Events
        requestBody:
           required: true
           content:
             application/json:
               schema:
                 type: object
                 description: KERI event message
        responses:
           200:
              description: Mailbox query response for server sent events
           204:
              description: KEL or EXN event accepted.
        """
        if req.method == "OPTIONS":
            rep.status = falcon.HTTP_200
            return

        rep.set_header('Cache-Control', "no-cache")
        rep.set_header('connection', "close")

        if CESR_DESTINATION_HEADER not in req.headers:
            raise falcon.HTTPBadRequest(title="CESR request destination header missing")

        aid = req.headers[CESR_DESTINATION_HEADER]
        kourier = self.kry.lookup(aid)
        if kourier is None:
            raise falcon.HTTPNotFound(title=f"unknown destination AID {aid}")

        kourier.psr.parse(ims=req.bounded_stream.read(), local=True)

        rep.set_header('Content-Type', "application/json")
        rep.status = falcon.HTTP_204


def getRequiredParam(body, name):
    param = body.get(name)
    if param is None:
        raise falcon.HTTPBadRequest(description=f"required field '{name}' missing from request")

    return param


class QryRpyMailboxIterable:

    def __init__(self, kourier, said, retry=5000):
        self.kourier = kourier
        self.retry = retry
        self.said = said
        self.iter = None

    def __iter__(self):
        return self

    def __next__(self):
        if self.iter is None:
            if self.kourier.cues:
                cue = self.kourier.cues.pull()
                serder = cue["serder"]
                if serder.said == self.said:
                    kin = cue["kin"]
                    if kin == "stream":
                        pre = cue["pre"]
                        if pre != self.kourier.cid:
                            raise StopIteration()

                        self.iter = iter(MailboxIterable(mbx=self.kourier.mbx, pre=cue["pre"], topics=cue["topics"],
                                                         retry=self.retry))
                else:
                    self.kourier.cues.append(cue)

            return b''

        return next(self.iter)
