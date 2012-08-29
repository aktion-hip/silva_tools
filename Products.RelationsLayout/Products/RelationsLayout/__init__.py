# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

# Python
import os

# Zope
#TODO: package_home is deprecated, import from App.Common instead
from Globals import package_home
from zope.interface import Interface

# Silva
from silva.core.conf.installer import DefaultInstaller

from silva.core import conf as silvaconf

_extensionName = "RelationsLayout"
silvaconf.extensionName(_extensionName)
silvaconf.extensionTitle('Relations Layout')
silvaconf.extensionDepends('RwLayout')

pjoin = os.path.join

metadatasets = [('relations-layout', 'relations.xml', 
                     ('Silva Root', 'Silva Publication')),
               ]

class IExtension(Interface):
    '''
    RelationsLayout Extension
    '''

class RelationsLayoutInstaller(DefaultInstaller):

    def install_custom(self, root):
        self._configureMetadata(root)
    
    def uninstall_custom(self, root):
        self._removeMetadata(root)
        
    def _configureMetadata(self, context):
        #map relations-layout metadata set to the types defined in metadatasets.types
        product = package_home(globals())
        schema = pjoin(product, 'schema')
        
        service_metadata = context.service_metadata
        for setid, xmlfilename, types in metadatasets:
            collection = service_metadata.getCollection()
            if not setid in collection.objectIds():
                xmlfile = pjoin(schema, xmlfilename)
                definition = open(xmlfile, 'r')        
                collection.importSet(definition)
    
            service_metadata.addTypesMapping(types, (setid, ))
        service_metadata.initializeMetadata()
        
    def _removeMetadata(self, context):
        set_ids = []
        service_metadata = context.service_metadata
        for setid, xmlfilename, types in metadatasets:
            collection = service_metadata.getCollection()
            context.service_metadata.removeTypesMapping(types, (setid, ))
            set_ids.append(setid)
        service_metadata.initializeMetadata()
        service_metadata.getCollection().manage_delObjects(set_ids)    
    

install = RelationsLayoutInstaller(_extensionName, IExtension)