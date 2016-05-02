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
import pykafka

from zoe_logger.config import load_configuration, get_conf

log = logging.getLogger("main")
LOG_FORMAT = '%(asctime)-15s %(levelname)s %(name)s (%(threadName)s): %(message)s'


class GELFUDPHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        data = self.rfile.read()
        data = gzip.decompress(data)
        parsed_data = json.loads(data.decode('utf-8'))
#        service_id = '.'.join([data['_zoe.service.name'], data['_zoe.execution.name'], data['_zoe.owner'], data['_zoe.deployment_name']])
#        log_line = ' '.join([str(data['timestamp']), data['host'], service_id, data['short_message']])
        with self.server.kafka_producer.get_producer() as producer:
            if 'host' in parsed_data:
                producer.produce(data, partition_key=parsed_data['host'].encode('utf-8'))
            else:
                producer.produce(data, partition_key=b'no_host')
        # log.debug(log_line)


class ZoeLoggerUDPServer(socketserver.UDPServer):
    def __init__(self, server_address, handler_class, kafka_producer):
        self.allow_reuse_address = True
        super().__init__(server_address, handler_class)
        self.kafka_producer = kafka_producer


def udp_listener(kafka_producer):
    while True:
        try:
            server = ZoeLoggerUDPServer(("0.0.0.0", 12201), GELFUDPHandler, kafka_producer)
            server.serve_forever()
        except KeyboardInterrupt:
            break
        except:
            log.exception('Exception in UDP listener')


def setup_kafka():
    client = pykafka.KafkaClient(hosts=get_conf().kafka_broker)
    return client.topics[b'docker_logs']


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

    kafka_producer = setup_kafka()
    udp_listener(kafka_producer)
