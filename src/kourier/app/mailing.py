# -*- encoding: utf-8 -*-
"""
KERI
kourier.app.mailing package

"""
import json
from urllib.parse import urlparse, urlsplit

import falcon
from falcon.media.multipart import MultipartParseError
from hio.base import doing
from hio.core import http
from hio.help import decking
from keri import kering, core, help
from keri.app import indirecting, habbing, storing, forwarding, oobiing, configing
from keri.core import routing, eventing, parsing, serdering, coring
from keri.db.basing import BaserDoer
from keri.help import helping
from keri.peer import exchanging
from kourier.core import basing, httping, ending

logger = help.ogler.getLogger()


def setup(host="127.0.0.1", port=9632, bootHost="127.0.0.1", bootPort=9631, base=None, temp=False,
          headDirPath=None, keypath=None, certpath=None, cafilepath=None):

    db = basing.Baser(name="kourier", base=base, temp=temp)
    dbDoer = BaserDoer(baser=db)
    cf = configing.Configer(name=db.name, headDirPath=headDirPath)

    kry = Kouriery(db, cf=cf)
    bootApp = falcon.App(middleware=falcon.CORSMiddleware(
        allow_origins='*', allow_credentials='*',
        expose_headers=['cesr-attachment', 'cesr-date', 'content-type', 'signature', 'signature-input',
                        'signify-resource', 'signify-timestamp']))

    bootServer = indirecting.createHttpServer(host=bootHost, port=bootPort, app=bootApp, keypath=keypath,
                                              certpath=certpath, cafilepath=cafilepath)
    bootSrvrDoer = http.ServerDoer(server=bootServer)
    korColEnd = KourierCollectionEnd(kry=kry)
    bootApp.add_route("/mailboxes", korColEnd)
    korResEnd = KourierResourceEnd(kry=kry)
    bootApp.add_route("/mailboxes/{eid}", korResEnd)

    app = falcon.App(middleware=falcon.CORSMiddleware(
        allow_origins='*', allow_credentials='*',
        expose_headers=['cesr-attachment', 'cesr-date', 'content-type', 'signature', 'signature-input',
                        'signify-resource', 'signify-timestamp']))
    loadEnds(app, kry=kry)
    httping.loadEnds(app, kry=kry)
    oobiEnd = ending.OOBIEnd(kry=kry)
    app.add_route("/oobi", oobiEnd)
    app.add_route("/oobi/{aid}", oobiEnd)
    app.add_route("/oobi/{aid}/{role}", oobiEnd)
    app.add_route("/oobi/{aid}/{role}/{eid}", oobiEnd)

    server = indirecting.createHttpServer(host=host, port=port, app=app, keypath=keypath,
                                          certpath=certpath, cafilepath=cafilepath)
    serverDoer = http.ServerDoer(server=server)

    doers = [kry, serverDoer, bootSrvrDoer, dbDoer]

    return doers


def loadEnds(app, kry):
    aidEnd = AuthCollectionEnd(kry=kry)
    app.add_route("/{aid}/mailboxes", aidEnd)


class Kouriery(doing.DoDoer):

    def __init__(self, db, cf=None):
        self.cf = cf
        if self.cf is not None:
            conf = self.cf.get()
            if "kourier" in conf:
                conf = conf["kourier"]
                if "dt" in conf:  # datetime of config file
                    if "curls" in conf:
                        curls = conf["curls"]
                        self.url = curls[0]
                        splits = urlsplit(self.url)
                        self.host = splits.hostname
                        self.port = splits.port
                        self.scheme = (splits.scheme if splits.scheme in kering.Schemes
                                       else kering.Schemes.http)

        self.db = db
        self.kors = dict()

        self.reload()

        doers = self.kors.values()
        super(Kouriery, self).__init__(doers=doers, always=True)

    def reload(self):
        for said, kor in self.db.kors.getItemIter():
            hby = habbing.Habery(name=kor.name, base=self.db.base, temp=self.db.temp)
            hab = hby.habByName(kor.name)

            kourier = Kourier(kry=self, pobox=self.db, hby=hby, hab=hab, cid=kor.cid)
            self.kors[hab.pre] = kourier

    def lookup(self, aid):
        if aid in self.kors:
            return self.kors[aid]

        return None

    def createKourier(self, aid):
        # Create a random name from Salter
        name = core.Salter().qb64

        # We need to manage keys from an HSM here
        hby = habbing.Habery(name=name, base=self.db.base, bran=None)
        hab = hby.makeHab(name=name, transferable=False)
        dt = helping.nowIso8601()

        msgs = bytearray()
        msgs.extend(hab.makeEndRole(eid=hab.pre,
                                    role=kering.Roles.controller,
                                    stamp=dt))
        msgs.extend(hab.makeLocScheme(url=f"{self.scheme}://{self.host}:{self.port}/{hab.pre}",
                                      scheme=self.scheme,
                                      stamp=dt))
        hab.psr.parse(ims=msgs)

        kor = basing.Kor(
            name=name,
            cid=aid,
            eid=hab.pre
        )

        self.db.kors.pin(keys=(hab.pre,), val=kor)
        self.db.cids.add(keys=(aid,), val=hab.kever.prefixer.qb64)

        kourier = Kourier(kry=self, pobox=self.db, hby=hby, hab=hab, cid=aid, )
        self.kors[hab.pre] = kourier

        self.extend([kourier])

        return kourier

    def deleteKourier(self, eid):
        if eid not in self.kors:
            raise ValueError(f"Unable to delete mailbox, {eid} is not a valid mailbox identifier")

        kourier = self.kors[eid]

        cid = kourier.cid
        self.db.kors.rem(keys=(eid,))
        self.db.cids.rem(keys=(cid,), val=eid)
        kourier.hby.close(clear=True)

        self.remove([kourier])


class Kourier(doing.DoDoer):
    def __init__(self, kry, pobox, hby, hab, cid):
        self.kry = kry
        self.pobox = pobox
        self.hby = hby
        self.hab = hab
        self.cid = cid
        self.cues = decking.Deck()

        self.mbx = storing.Mailboxer(name=self.pobox.name, temp=self.pobox.temp)
        forwarder = forwarding.ForwardHandler(hby=hby, mbx=self.mbx)
        exchanger = exchanging.Exchanger(hby=hby, handlers=[forwarder])
        oobiery = oobiing.Oobiery(hby=hby)

        app = falcon.App(cors_enable=True)
        httping.loadEnds(app=app, kry=self)

        rvy = routing.Revery(db=hby.db, cues=self.cues)
        kvy = eventing.Kevery(db=hby.db,
                              lax=True,
                              local=False,
                              rvy=rvy,
                              cues=self.cues)
        kvy.registerReplyRoutes(router=rvy.rtr)
        self.parser = parsing.Parser(framed=True,
                                     kvy=kvy,
                                     exc=exchanger,
                                     rvy=rvy)

        doers = [*oobiery.doers]

        super(Kourier, self).__init__(doers=doers, always=True)

    def exit(self, deeds=None):
        if self.hby:
            logger.info(f"Closing Kourier database {self.hby.name}")
            self.hby.close()

    def oobis(self):
        oobis = []
        urls = self.hab.fetchUrls(eid=self.hab.pre, scheme=kering.Schemes.http)
        if kering.Schemes.https in urls:
            oobis.append(f"https://{self.kry.host}:{self.kry.port}/oobi/{self.hab.pre}/controller")
        elif kering.Schemes.http in urls:
            oobis.append(f"http://{self.kry.host}:{self.kry.port}/oobi/{self.hab.pre}/controller")

        return oobis


class KourierCollectionEnd:
    """ Endpoint class for responding to HTTP POST requests to provision new Kouriers for AIDs


    """
    def __init__(self, kry):
        """ Create Kourier endpoint class

        Args:
            kry (Kouriery): Kourier factory instance

        """
        self.kry = kry

    def on_post(self, req, rep):
        """ POST End point for provisioning Kouriers from the KERI Inbox as a Service

        Parameters:
            req (Request): Falcon HTTP request object
            rep (Response): Falcon HTTP response object


        """
        body = req.get_media()
        aid = httping.getRequiredParam(body, "aid")

        try:
            prefixer = core.Prefixer(qb64=aid)
        except Exception as e:
            raise falcon.HTTPBadRequest(description=f"invalid AID for witnessing: {e.args[0]}")

        try:
            kourier = self.kry.createKourier(aid=aid)
        except kering.ConfigurationError as e:
            raise falcon.HTTPBadRequest(description=e.args[0])

        oobis = kourier.oobis()

        data = dict(
            cid=prefixer.qb64,
            eid=kourier.hab.pre,
            oobis=oobis
        )
        rep.status = falcon.HTTP_200
        rep.content_type = "application/json"
        rep.data = json.dumps(data).encode("utf-8")


class AuthCollectionEnd:

    def __init__(self, kry):
        self.kry = kry

    def on_post(self, req, rep, aid):
        """

        Parameters:
            req (Request): Falcon HTTP request object
            rep (Response): Falcon HTTP response object
            aid (str): qb64 AID of controller of mailbox

        The body of this POST request must be a multipart form POST with 2 parts, one named
        'kel' that is the current KEL of the controller identified in the 'aid' query path
        parameter, and one named 'rpy' that has a route of '/end/role/add' adding the Kourier
        AID with a role of mailbox.

        {
          "v" : "KERI10JSON00011c_",
          "t" : "rep",
          "d": "EZ-i0d8JZAoTNZH3ULaU6JR2nmwyvYAfSVPzhzS6b5CM",
          "dt": "2020-08-22T17:50:12.988921+00:00",
          "r" : "/end/role/add",
          "a" :
          {
             "cid":  "EaU6JR2nmwyZ-i0d8JZAoTNZH3ULvYAfSVPzhzS6b5CM",
             "role": "mailbox",
             "eid": "BrHLayDN-mXKv62DAjFLX1_Y5yEUe0vA9YPe_ihiKYHE",
          }
        }

        """

        kourier = self.kry.lookup(aid)
        if kourier is None:
            raise falcon.HTTPBadRequest(description=f"AID {aid} is not recognized")

        form = req.get_media()
        serder = None
        try:
            for part in form:
                if part.name == "kel":
                    msg = part.stream.read()
                    kourier.parser.parse(msg, local=False)
                elif part.name == "rpy":
                    msg = part.stream.read()
                    serder = serdering.SerderKERI(raw=msg)
                    if serder.ked['t'] != coring.Ilks.rpy:
                        raise falcon.HTTPBadRequest(description=f"Invalid reply message, evt={serder.pretty()}")

                    payload = serder.ked['a']
                    cid = payload['cid']
                    role = payload['role']
                    eid = payload['eid']
                    if cid != kourier.cid:
                        raise falcon.HTTPBadRequest(description="controller of rpy does not match AID")

                    if role != kering.Roles.mailbox:
                        raise falcon.HTTPBadRequest(description="role must be mailbox")

                    if eid != kourier.hab.pre:
                        raise falcon.HTTPBadRequest(
                            description=f"mailbox eid={eid} does not match kourier aid={kourier.hab.pre}")

                    # Parse the event, get the KEL in our Kevers
                    kourier.parser.parse(msg, local=False)
        except MultipartParseError:  # The form works but still raises this exception so ignore for now...
            pass

        if aid not in kourier.hab.kevers:  # Not a valid, signed inception event
            raise falcon.HTTPBadRequest(description="body does not contain a valid inception KEL")

        if kourier.hab.db.rpys.get(keys=(serder.said,)) is None:
            raise falcon.HTTPBadRequest(description=f"end role authorization event not saved {serder.said}")

        urls = (kourier.hab.fetchUrls(eid=kourier.hab.pre, scheme=kering.Schemes.http)
                or kourier.hab.fetchUrls(eid=kourier.hab.pre, scheme=kering.Schemes.https))
        if not urls:
            raise falcon.HTTPBadRequest(
                description=f"{kourier.hab.name} identifier {kourier.hab.pre} does not have any controller endpoints")

        url = urls[kering.Schemes.http] if kering.Schemes.http in urls else urls[kering.Schemes.https]
        up = urlparse(url)
        oobi = f"{up.scheme}://{up.hostname}:{up.port}/oobi/{kourier.hab.pre}/controller"

        body = dict(
            oobi=oobi
        )

        rep.content_type = "application/json"
        rep.status = falcon.HTTP_200
        rep.data = json.dumps(body).encode("utf-8")


class KourierResourceEnd:

    def __init__(self, kry: Kouriery):
        self.kry = kry

    def on_delete(self, _, rep, eid):
        """
        Delete a running witness, this is not undo-able
        Args:
            _ (Request): Falcon request object
            rep (Response): Falcon response object
            eid (str): qb64 identifier of witness to delete

        """
        try:
            coring.Prefixer(qb64=eid)
        except Exception as e:
            raise falcon.HTTPBadRequest(description=f"invalid AID for a kourier: {e.args[0]}")

        try:
            self.kry.deleteKourier(eid=eid)
        except kering.ConfigurationError as e:
            raise falcon.HTTPBadRequest(description=e.args[0])

        rep.status = falcon.HTTP_204
