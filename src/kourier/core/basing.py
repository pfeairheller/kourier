# -*- encoding: utf-8 -*-
"""
KERI
kourier.core.basing package

"""


from dataclasses import dataclass
from keri.db import dbing, koming, subing


@dataclass
class Kor:
    """
        Class to track allocated and running Sentinals
    """
    name: str
    eid: str
    cid: str


class PostOffice(dbing.LMDBer):
    TailDirPath = "keri/postoffice"
    AltTailDirPath = ".keri/postoffice"
    TempPrefix = "keri_postoffice_"

    def __init__(self, name="postoffice", headDirPath=None, reopen=True, **kwa):
        """

        Parameters:
            headDirPath:
            perm:
            reopen:
            kwa:
        """
        self.kors = None
        self.cids = None

        super(PostOffice, self).__init__(name=name, headDirPath=headDirPath, reopen=reopen, **kwa)

    def reopen(self, **kwa):
        """  Reopen database and initialize sub-dbs
        """
        super(PostOffice, self).reopen(**kwa)

        # Kourier dataclass keyed by watcher AID
        self.kors = koming.Komer(db=self, subkey='kors.', schema=Kor, )
        # Controller AID to mailbox AID index
        self.cids = subing.Suber(db=self, subkey='cids.')

        return self.env

