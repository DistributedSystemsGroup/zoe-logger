# Copyright (c) 2016, Daniele Venzano
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from tornado.ioloop import IOLoop
import momoko

from web_logger import make_app
from web_logger.config import load_configuration, get_conf

log = logging.getLogger("web_logger")


def zoe_web_main() -> int:
    """
    This is the entry point for the Zoe Web script.
    :return: int
    """
    load_configuration()
    args = get_conf()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("tornado").setLevel(logging.DEBUG)

    log.info("Starting HTTP server...")
    ioloop = IOLoop.instance()
    app = make_app()

    app.db = momoko.Pool(
        dsn='dbname=' + args.db_name + ' user=' + args.db_user + ' password=' + args.db_pass + ' host=' + args.db_host + ' port=' + str(args.db_port),
        size=1,
        ioloop=ioloop,
    )

    future = app.db.connect()
    ioloop.add_future(future, lambda f: ioloop.stop())
    ioloop.start()
    future.result()  # raises exception on connection error

    app.listen(args.listen_port, args.listen_address)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        print("CTRL-C detected, terminating")
