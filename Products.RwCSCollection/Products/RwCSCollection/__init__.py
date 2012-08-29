# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

# Python
import os
import logging

# Zope
from App.Common import package_home
# Silva
from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface
from Products.SilvaExternalSources.install import INSTALLERS

from Products.RwCSCollection.code_source.configure import code_sources, code_sources_derived

pjoin = os.path.join
_fs_cs_path = pjoin(package_home(globals()), 'code_source', 'plain')
_cs_prefix = 'cs_'
    
logger = logging.getLogger('Products.RwCSCollection')

_extensionName = "RwCSCollection"
silvaconf.extensionName(_extensionName)
silvaconf.extensionTitle("RelationWare Code Sources")
silvaconf.extensionDepends(["RwLayout", "SilvaExternalSources"])   
_cs_service = 'service_codesources'

class IExtension(Interface):
    '''
    RwCSCollection Extension
    '''

class RwCSCollectionInstaller(DefaultInstaller):
    def install_custom(self, root):
        install_code_sources(root, _fs_cs_path, code_sources, code_sources_derived)
    
    def uninstall_custom(self, root):
        delete_code_sources(root, code_sources_derived)
        delete_code_sources(root, code_sources)

install = RwCSCollectionInstaller(_extensionName, IExtension)

###

def install_code_sources(folder, cs_path, code_sources={}, derived_code_sources={}, product='RwCSCollection'):
    '''
    Method to install Silva code source objects.
    The code source objects described in the dictionary are created in the specified folder.

    @param folder: the Zope folder where the code sources are created
    @param cs_path: the path to the code source templates in the file system
    @param code_sources: dictionnary describing the code sources to install
    @param derived_code_sources:  dictionnary describing derived code sources to install, e.g.
        {'show_sitemap':{'title':'Sitemap', 'constructor':'manage_addSiteMap'} [,...]}
    @param product: the name of the product that can create the object [default: RwCSCollection]
    '''
    factory = folder.manage_addProduct['SilvaExternalSources']
    for cs_name, cs_info in code_sources.items():
        cs_id = _cs_prefix + cs_name
        if hasattr(folder.aq_inner.aq_explicit, cs_id):
            continue

        factory.manage_addCodeSource(cs_id, cs_info['title'], cs_name)
        source = getattr(folder, cs_id)
        source.set_description(cs_info['description'])
        source.set_previewable(cs_info.get('previewable', False))
        source.set_cacheable(cs_info.get('cacheable', False))
        source.set_elaborate(cs_info.get('elaborate', False))
        
        codesource_path = pjoin(cs_path, cs_name)
        for filename in os.listdir(codesource_path):
            name, extension = os.path.splitext(filename)
            installer = INSTALLERS.get(extension, None)
            if installer is None:
                logger.info(u"don't know how to install file %s for code source %s" % (filename, cs_name))
                continue
            with open(os.path.join(codesource_path, filename), 'rb') as data:
                installer(source, data, name)

    for cs_name, cs_info in derived_code_sources.items():
        if not cs_info.get('install', False):
            continue
        
        cs_id = _cs_prefix + cs_name
        if hasattr(folder.aq_inner.aq_explicit, cs_id):
            continue

        constructor = getattr(folder.manage_addProduct[product], cs_info['constructor'])
        if constructor:
            constructor(cs_id, cs_info['title'])

def delete_code_sources(folder, code_sources):
    """
    Removes the code_sources in the specified dictionary from the specified folder.
    @param folder: container of the resources to remove
    @param code_sources: dictionary
    """
    deleteObjectsHelper(folder, [_cs_prefix + key for key in code_sources.copy().keys()])

def deleteObjectsHelper(context, ids):
    '''
    Helper method to delete the specified objects.
    @param context: context from which the objects with the specified ids have to be removed
    @param ids: list of ids
    '''
    if type(ids) == type(''):
        ids = [ids]
    delete_list = [id for id in ids if hasattr(context.aq_inner.aq_explicit, id)]
    context.manage_delObjects(delete_list)
