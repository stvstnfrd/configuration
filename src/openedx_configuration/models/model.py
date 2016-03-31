#!/usr/bin/env python
# -*- coding: utf-8 -*-
class Model(object):
    _model = False
    name = None
    environment = None

    def __init__(self, environment, name, model=False, **kwargs):
        if model:
            name = model.tags.get('Name')
            environment = model.tags.get('environment')
        self.name = name
        self.environment = environment
        self._model = model

    @property
    def exists(self):
        return self.model is not None

    @property
    def model(self):
        if self._model is False:
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
        model = self._lookup()
        self._model = model

    def destroy(self, *args, **kwargs):
        if self.exists:
            self._destroy(*args, **kwargs)
            self._model = False

    def create(self, *args, **kwargs):
        print('kwargs', kwargs, self)
        if not self.exists:
            model = self._create(*args, **kwargs)
            self._model = model

    @property
    def id(self):
        return getattr(self.model, 'id', None)
