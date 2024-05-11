# -*- encoding: utf-8 -*-
"""
KERI
kourier.app.mailing package

"""
from kourier.app import mailing
from kourier.core import basing


def test_auth_collection_end():
    pobox = basing.PostOffice(name="test", temp=True)
    kry = mailing.Kouriery(pobox=pobox)
    auth = mailing.AuthCollectionEnd(kry=kry)

    assert auth is not None