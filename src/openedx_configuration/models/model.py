#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Define base behavior for AWS models
"""
from boto.vpc import VPCConnection


class Model(object):
    """
    Represent a base AWS object model
    """
    _model = False
    name = None
    environment = None
    type_api = VPCConnection

    def __init__(self, environment, name, model=False, api=None, **kwargs):
        """
        Initialize a base AWS object, set common values
        """
        if model:
            name = model.tags.get('Name', name)
            environment = model.tags.get('environment', environment)
        self.name = name
        self.environment = environment
        self._model = model
        self.api = api or self.type_api()

    def __repr__(self):
        """
        Represent the object as a string
        """
        data = {
            'name': self.name,
            'environment': self.environment,
            '_model': self._model,
        }
        if hasattr(self, 'vpc') and self.vpc:
            data['vpc_id'] = self.vpc.id
        if hasattr(self, 'subnet') and self.subnet:
            data['subnet_id'] = self.subnet.id
        string = u"{klass}({kwargs})".format(
            klass=self.__class__.__name__,
            kwargs=unicode(data),
        )
        return string

    def create(self, *args, **kwargs):
        """
        Delegate creation to the subclass, if it doesn't exist
        """
        print('check if exists', self)
        if self.exists:
            print('cowwardly refusing to recreate', self)
            return False
        print('try create', self)
        if kwargs.get('dry_run'):
            print('opting not to create', self)
            return
        model = self._create(*args, **kwargs)
        self._model = model
        print('created', self)

    def destroy(self, *args, **kwargs):
        """
        Delegate deletion to the subclass, if it does exist
        """
        print('check if exists', self)
        if not self.exists:
            print('cannot destroy what does not exist', self)
            return False
        print('try destroy', self)
        if kwargs.get('dry_run'):
            print('opting not to destroy', self)
            return
        self._destroy(**kwargs)
        self._model = False
        print('destroyed', self)

    @property
    def exists(self):
        """
        Check if the model exists in AWS
        """
        return self.model is not None

    @property
    def id(self):
        """
        Mirror the ID of the underlying model
        """
        return getattr(self.model, 'id', None)

    @property
    def model(self):
        """
        Load the model lazily
        """
        self._model = self._model or self._get_one()
        return self._model

    @property
    def tags(self):
        """
        Mirror the tags of the underlying model
        """
        data = {}
        if self.exists:
            data = self.model.tags
        return data
