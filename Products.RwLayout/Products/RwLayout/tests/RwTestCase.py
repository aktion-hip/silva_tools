# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from Testing import ZopeTestCase
import transaction

from Products.Silva.testing import FunctionalLayer
from Products.Silva.tests.layer import users, setUp, tearDown


class RwTestCase(ZopeTestCase.Sandboxed, ZopeTestCase.ZopeTestCase):
    layer = FunctionalLayer

    def setUp(self):
        transaction.abort()
        self.beforeSetUp()
        try:
            #self.app = self._app()
            self.app = self.layer.get_application()
            setUp(self)
            self.silva = self.root = self.getRoot()
            self.catalog = self.silva.service_catalog
            self.layer.login('author')
            #self.login()
            self.app.REQUEST.AUTHENTICATED_USER = \
                self.app.acl_users.getUser(ZopeTestCase.user_name)
            self.afterSetUp()
        except:
            self.beforeClose()
            self._clear()
            raise
    
    def afterSetUp(self):
        pass
    
    def afterClear(self):
        pass

    def beforeSetUp(self):
        '''Called before the ZODB connection is opened,
           at the start of setUp(). By default begins
           a new transaction.
        '''
        transaction.begin()

    def beforeClose(self):
        '''Called before the ZODB connection is closed,
           at the end of tearDown(). By default aborts
           the transaction.
        '''
        transaction.abort()
    
    def _clear(self, call_close_hook=0):
        '''Clears the fixture.'''
        try:
            if call_close_hook:
                self.beforeClose()
        finally:
            tearDown(self)
            self._close()
            self.afterClear()

    def _close(self):
        '''Closes the ZODB connection.'''
        super(RwTestCase, self)._close()

    def getRoot(self):
        """Returns the silva root object, i.e. the "fixture root".
           Override if you don't like the default.
        """
        return self.app.root

    #add Silva Objects helper methods
    
    def addObject(self, container, type_name, id, product='Silva', **kw):
        getattr(container.manage_addProduct[product],
            'manage_add%s' % type_name)(id, **kw)
        # gives the new object a _p_jar ...
        transaction.savepoint()
        return getattr(container, id)


    def add_folder(self, object, id, title, **kw):
        folder = self.addObject(object, 'Folder', id, title=title, **kw)
        # Emulate old add index feature
        policy = kw.get('policy_name', None)
        if policy == 'Silva Document':
            self.addObject(folder, 'Document', 'index',
                           title=title, product='SilvaDocument')
        if policy == 'Silva AutoTOC':
            self.addObject(folder, 'AutoTOC', 'index', title=title)
        return folder

    def add_publication(self, object, id, title, **kw):
        publication = self.addObject(
            object, 'Publication', id, title=title, **kw)
        policy = kw.get('policy_name', None)
        if policy == 'Silva Document':
            self.addObject(publication, 'Document', 'index',
                           title=title, product='SilvaDocument')
        if policy == 'Silva AutoTOC':
            self.addObject(publication, 'AutoTOC', 'index', title=title)
        return publication

    def add_document(self, object, id, title):
        return self.addObject(object, 'Document', id, title=title,
                              product='SilvaDocument')
