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

import datetime
import logging
import json
import pykafka
import psycopg2

from pq_consumer.config import load_configuration, get_conf

log = logging.getLogger("main")
LOG_FORMAT = '%(asctime)-15s %(levelname)s %(name)s (%(threadName)s): %(message)s'


def main_loop(args, pq_conn):
    client = pykafka.KafkaClient(args.kafka_broker)
    consumer = client.topics[b'docker_logs'].get_simple_consumer(consumer_group=b'pq_consumer', auto_commit_enable=False)
    # consumer = KafkaConsumer('docker_logs', bootstrap_servers=args.kafka_broker, enable_auto_commit=False, group_id='pq_consumer')
    cursor = pq_conn.cursor()
    for message in consumer:
        if message is not None:
            data = json.loads(message.value.decode('utf-8'))
            log.debug(data)
            cursor.execute('INSERT INTO logs (container_name, image_name, host, container_id, timestamp, message) VALUES (%s,%s,%s,%s,%s,%s)',
                           (data['_container_name'],
                            data['_image_name'],
                            data['host'],
                            data['_container_id'],
                            datetime.datetime.fromtimestamp(data['timestamp']), data['short_message']))
        consumer.commit_offsets()


def setup_postgres(args):
    conn = psycopg2.connect(database=args.db_name, user=args.db_user, password=args.db_pass, host=args.db_host, port=args.db_port)
    conn.autocommit = True
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
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

#    logging.getLogger('kafka').setLevel(logging.WARN)

    pq_conn = setup_postgres(args)

    main_loop(args, pq_conn)
