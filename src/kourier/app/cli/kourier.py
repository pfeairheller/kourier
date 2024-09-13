# -*- encoding: utf-8 -*-
"""
kourier.app.cli module

"""
import multicommand
from hio.base import doing
from keri import help

from kourier.app.cli import commands

logger = help.ogler.getLogger()


def main():
    parser = multicommand.create_parser(commands)
    args = parser.parse_args()

    if not hasattr(args, 'handler'):
        parser.print_help()
        return

    try:
        doers = args.handler(args)
        tock = 0.00125
        doist = doing.Doist(limit=0.0, tock=tock, real=True)
        doist.do(doers=doers)

    except Exception as ex:
        import os
        if os.getenv('DEBUG_KOURIER'):
            import traceback
            traceback.print_exc()
        else:
            print(f"ERR: {ex}")
        return -1


if __name__ == "__main__":
    main()
