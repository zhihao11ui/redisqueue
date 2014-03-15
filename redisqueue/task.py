__author__ = 'Jeff Kehler'

import json
import hashlib

class Task:
    def __init__(self, payload=None, raw=False, uid=None, unique=False):
        if not raw:
            self._payload = json.dumps(payload)

            self._raw = False
        else:
            self._payload = payload
            self._raw = True
        self.uid = uid
        self._unique = unique
        self._hash = None

    @property
    def payload(self):
        if not self._raw:
            return json.loads(self._payload)
        else:
            return self._payload

    @property
    def json(self):
        if not self._raw:
            return self._payload
        return None

    @property
    def unique(self):
        return self._unique

    @unique.setter
    def unique(self, value):
        self._unique = value

    @property
    def hash(self):
        if self._raw:
            return hashlib.sha512(self._payload.encode('utf-8')).hexdigest()
        else:
            # convert our json object to dict then sort it to generate a hash
            payload_dict = json.loads(self._payload)

            return hashlib.sha512(
                json.dumps(sorted(payload_dict.items())).encode('utf-8')
            ).hexdigest()