#!/usr/bin/python3

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
import socketserver
import json
import gzip
import psycopg2
import datetime

from zoe_logger.config import load_configuration, get_conf

log = logging.getLogger("main")


class GELFUDPHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        data = self.rfile.read()
        data = gzip.decompress(data)
        data = json.loads(data.decode('utf-8'))
        # log.debug(data)
        self.server.cursor.execute('INSERT INTO logs (container_name, image_name, host, container_id, timestamp, message) VALUES (%s,%s,%s,%s,%s,%s)', (data['_container_name'], data['_image_name'], data['host'], data['_container_id'], datetime.datetime.fromtimestamp(data['timestamp']), data['short_message']))
        self.server.db_conn.commit()


class ZoeLoggerUDPServer(socketserver.UDPServer):
    def __init__(self, server_address, handler_class, db_conn):
        self.allow_reuse_address = True
        super().__init__(server_address, handler_class)
        self.db_conn = db_conn
        self.cursor = db_conn.cursor()


def udp_listener(db_conn):
    while True:
        try:
            server = ZoeLoggerUDPServer(("0.0.0.0", 12201), GELFUDPHandler, db_conn)
            server.serve_forever()
        except KeyboardInterrupt:
            break
        except:
            log.exception('Exception in UDP listener')


def setup_postgres():
    conn = psycopg2.connect(database='docker_logs', user='postgres', password='zoepostgres', host='192.168.45.252')
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS logs (
                        id BIGSERIAL PRIMARY KEY,
                        container_name TEXT NOT NULL,
                        image_name TEXT NOT NULL,
                        host TEXT NOT NULL,
                        container_id TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        message TEXT NOT NULL
                    )""")
    conn.commit()
    cursor.close()
    return conn


def main():
    """
    The entrypoint for the zoe-observer script.
    :return: int
    """
    load_configuration()
    args = get_conf()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    db_conn = setup_postgres()
    udp_listener(db_conn)
