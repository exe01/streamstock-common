from .exceptions import *
from streamstock_common.time import str_to_timedelta, timedelta_to_str
import requests
import copy
import json


class Model(dict):
    DB_URL = 'http://localhost/api/1.0'
    API_NAME = 'model'
    TIMEDELTA_FIELDS = []
    JSON_FIELDS = []

    _DEFAULT_COUNT = 10

    def __init__(self, representation):
        super().__init__()
        self.update(representation)

    def save(self):
        create = True
        if 'id' in self:
            create = False

        representation = {}
        representation.update(self)

        representation = self._dump_timedelta_fields(representation)
        representation = self._dump_json_fields(representation)

        if create:
            url = '{}/{}/'.format(self.DB_URL, self.API_NAME)
            representation = self.request('POST', url, json=representation)
        else:
            url = '{}/{}/{}/'.format(self.DB_URL, self.API_NAME, self['id'])
            representation = self.request('PATCH', url, json=representation)

        model = self._create_instance(representation)
        self.update(model)

    @classmethod
    def get_(cls, **kwargs):
        url = '{}/{}'.format(cls.DB_URL, cls.API_NAME)

        params = {
            'page': 1,
            'count': cls._DEFAULT_COUNT,
        }

        if 'params' in kwargs:
            params.update(kwargs['params'])
            del kwargs['params']

        while True:
            json_response = cls.request('GET', url, params=params, **kwargs)

            models = []
            for representation in json_response['results']:
                model = cls._create_instance(representation)
                models.append(model)

            for model in models:
                yield model

            if json_response['meta']['current_page'] >= json_response['meta']['all_pages']:
                break

            params['page'] += 1

    @classmethod
    def get_first(cls, **kwargs):
        params = {
            'count': 1
        }

        if 'params' in kwargs:
            params.update(kwargs['params'])
            del kwargs['params']

        models = cls.get_(params=params, **kwargs)
        models = list(models)

        if len(models) == 0:
            raise NotFound('for next params {}'.format(params))

        return models[0]

    @classmethod
    def get_by_id(cls, id, **kwargs):
        url = '{}/{}/{}/'.format(cls.DB_URL, cls.API_NAME, id)
        representation = cls.request('GET', url, **kwargs)
        return cls._create_instance(representation)

    @classmethod
    def request(cls, method, url, **kwargs):
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        json_response = response.json()
        return json_response

    @classmethod
    def _create_instance(cls, representation):
        representation = cls._delete_none_fields(representation)
        representation = cls._load_timedelta_fields(representation)
        representation = cls._load_json_fields(representation)

        return cls(representation)

    @classmethod
    def _delete_none_fields(cls, representation):
        representation = copy.deepcopy(representation)

        keys = list(representation.keys())
        for key in keys:
            if representation[key] is None:
                del representation[key]

        return representation

    @classmethod
    def _load_timedelta_fields(cls, representation):
        representation = copy.deepcopy(representation)

        for field in cls.TIMEDELTA_FIELDS:
            if field in representation:
                if representation[field] is not None:
                    representation[field] = str_to_timedelta(representation[field])

        return representation

    @classmethod
    def _dump_timedelta_fields(cls, representation):
        representation = copy.deepcopy(representation)

        for field in cls.TIMEDELTA_FIELDS:
            if field in representation:
                representation[field] = timedelta_to_str(representation[field])

        return representation

    @classmethod
    def _load_json_fields(cls, representation):
        representation = copy.deepcopy(representation)

        for field in cls.JSON_FIELDS:
            if field in representation:
                if representation[field] is not None:
                    representation[field] = json.loads(representation[field])

        return representation

    @classmethod
    def _dump_json_fields(cls, representation):
        representation = copy.deepcopy(representation)

        for field in cls.JSON_FIELDS:
            if field in representation:
                representation[field] = json.dumps(representation[field])

        return representation
