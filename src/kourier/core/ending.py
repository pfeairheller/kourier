# -*- encoding: utf-8 -*-

"""
KERI
kourier.core.oobiing package

"""
import falcon
from keri.end import ending


class OOBIEnd:
    """ REST API for OOBI endpoints

    Attributes:
        .hby (Habery): database access

    """

    def  __init__(self, kry, default=None):
        """  End point for responding to OOBIs

        Parameters:
            kry (Kouriery): database environment
            default (str) qb64 AID of the 'self' of the node for

        """
        self.kry = kry
        self.default = default

    def on_get(self, req, rep, aid=None, role=None, eid=None):
        """  GET endoint for OOBI resource

        Parameters:
            req: Falcon request object
            rep: Falcon response object
            aid: qb64 identifier prefix of OOBI
            role: requested role for OOBI rpy message
            eid: qb64 identifier prefix of participant in role

        """
        if aid is None:
            if self.default is None:
                raise falcon.HTTPNotFound(description="no blind oobi for this node")

            aid = self.default

        kourier = self.kry.lookup(aid)
        if kourier is None:
            raise falcon.HTTPNotFound(description=f"aid {aid} not found")

        if aid not in kourier.hby.kevers:
            raise falcon.HTTPNotFound(description=f"aid {aid} not found")

        kever = kourier.hby.kevers[aid]
        if kever.prefixer.qb64 in kourier.hby.prefixes:  # One of our identifiers
            hab = kourier.hby.habs[kever.prefixer.qb64]

        else:
            end = kourier.hab.db.ends.get(keys=(aid, role, eid))
            # We serve in this role for identifier
            if end and end.allowed and end.enabled is not False and aid == kourier.cid and eid == kourier.hab.pre:
                hab = kourier.hby.habs[eid]

            else:  # Not allowed to respond
                raise falcon.HTTPNotAcceptable(description="invalid OOBI request")

        eids = []
        if eid:
            eids.append(eid)

        msgs = hab.replyToOobi(aid=aid, role=role, eids=eids)
        if msgs:
            rep.status = falcon.HTTP_200  # This is the default status
            rep.set_header(ending.OOBI_AID_HEADER, aid)
            rep.content_type = "application/json+cesr"
            rep.data = bytes(msgs)

        else:
            rep.status = falcon.HTTP_NOT_FOUND
