#!/usr/bin/env python
# -*- coding: utf-8 -*-
class Model(object):
    def __init__(self, environment):
        self._name = None
        self._model = False
        self.environment = environment

    @property
    def exists(self):
        return self.model is not None

    @property
    def model(self):
        if self._model is False:
            self.fetch()
        return self._model

    @property
    def tags(self):
        data = {}
        if self.exists:
            data = self.model.tags
        return data

    @property
    def name(self):
        name = self._name
        if self.exists:
            name = self.model.tags.get('Name', '')
        return name

    def __repr__(self):
        data = self.__dict__
        string = "{klass}({kwargs})".format(
            klass=self.__class__.__name__,
            kwargs=unicode(data),
        )
        return string
