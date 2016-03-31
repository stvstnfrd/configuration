#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boto.vpc import VPCConnection


class Model(object):
    _model = False
    name = None
    environment = None
    type_api = VPCConnection

    def __init__(self, environment, name, model=False, api=None, **kwargs):
        if model:
            name = model.tags.get('Name', name)
            environment = model.tags.get('environment', environment)
        self.name = name
        self.environment = environment
        self._model = model
        self.api = api or self.type_api()

    @property
    def exists(self):
        return self.model is not None

    @property
    def model(self):
        if not self._model:
            self.lookup()
        return self._model

    @property
    def tags(self):
        data = {}
        if self.exists:
            data = self.model.tags
        return data

    def __repr__(self):
        data = {
            'name': self.name,
            'environment': self.environment,
            '_model': self._model,
        }
        if hasattr(self, 'vpc') and self.vpc:
            data['vpc_id'] = self.vpc.id
        if hasattr(self, 'subnet') and self.subnet:
            data['subnet_id'] = self.subnet.id
        string = "{klass}({kwargs})".format(
            klass=self.__class__.__name__,
            kwargs=unicode(data),
        )
        return string

    def lookup(self):
        model = self._get_one()
        self._model = model

    def destroy(self, dry_run=False, **kwargs):
        print('check if exists', self)
        if not self.exists:
            print('cannot destroy what does not exist', self)
            return False
        print('try destroy', self)
        if dry_run:
            print('opting not to destroy', self)
            return
        self._destroy(**kwargs)
        self._model = False

    def create(self, dry_run=False, **kwargs):
        print('check if exists', self)
        if self.exists:
            print('cowwardly refusing to recreate', self)
            return False
        print('try create', self)
        if dry_run:
            print('opting not to create', self)
            return
        model = self._create(**kwargs)
        self._model = model

    @property
    def id(self):
        return getattr(self.model, 'id', None)
