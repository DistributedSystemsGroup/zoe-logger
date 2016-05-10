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
import json

import tornado.gen

import web_logger.base_handler


def dt2str(dt):
    assert isinstance(dt, datetime.datetime)
    return dt.timestamp()


class APIContainerLogHandler(web_logger.base_handler.BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        container_name = self.get_argument('container_name')
        count = self.get_argument('count')
        last_id = self.get_argument('last_id')
        if int(count) > 0:
            cursor = yield self.db.execute('SELECT timestamp, message, id FROM logs WHERE container_name = %s and id > %s ORDER BY timestamp ASC LIMIT %s', (container_name, last_id, count))
        else:
            cursor = yield self.db.execute('SELECT timestamp, message, id FROM logs WHERE container_name = %s and id > %s ORDER BY timestamp ASC', (container_name, last_id))
        log = [(dt2str(x[0]), x[1], x[2]) for x in cursor.fetchall()]
        self.write(json.dumps(log))
        self.finish()
