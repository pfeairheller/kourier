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


class Baser(dbing.LMDBer):
    TailDirPath = "keri/kourier"
    AltTailDirPath = ".keri/kourier"
    TempPrefix = "keri_kourier_"

    def __init__(self, name="kourier", headDirPath=None, reopen=True, **kwa):
        """

        Parameters:
            headDirPath:
            perm:
            reopen:
            kwa:
        """
        self.kors = None
        self.cids = None

        super(Baser, self).__init__(name=name, headDirPath=headDirPath, reopen=reopen, **kwa)

    def reopen(self, **kwa):
        """  Reopen database and initialize sub-dbs
        """
        super(Baser, self).reopen(**kwa)

        # Kourier dataclass keyed by watcher AID
        self.kors = koming.Komer(db=self, subkey='kors.', schema=Kor, )
        # Controller AID to mailbox AID index
        self.cids = subing.Suber(db=self, subkey='cids.')

        return self.env

