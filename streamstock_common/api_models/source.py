from .model import Model
from .compilation import Compilation
from .const import *


class Source(Model):
    API_NAME = 'sources'

    JSON_FIELDS = [
        SOURCE_CREDENTIALS,
    ]

    def get_compilations(self, **kwargs):
        params = {
            'source': self['id']
        }

        if 'params' in kwargs:
            params.update(kwargs['params'])
            del kwargs['params']

        return Compilation.get_(params=params, **kwargs)
