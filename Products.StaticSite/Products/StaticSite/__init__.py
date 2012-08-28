# -*- coding: utf-8 -*-
# Copyright (c) 2012 RelationWare. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface
from silva.core.conf.installer import DefaultInstaller
from silva.core import conf as silvaconf
from Products.Silva.install import add_fss_directory_view
from Products.Silva import roleinfo

_extensionName = "StaticSite"
_meta_type = "Static Site"
silvaconf.extensionName(_extensionName)
silvaconf.extensionTitle('Static Site')
silvaconf.extensionDepends(["Silva"])   

class IExtension(Interface):
    '''
    StaticSite Extension
    '''

class StaticSiteInstaller(DefaultInstaller):
    def install_custom(self, root):
        add_fss_directory_view(
            root.service_views, _extensionName, __file__, 'views')
        # also register views
        registerViews(root.service_view_registry)
        # metadata registration
        configureSecurity(root)
        configureAddables(root)

    def uninstall_custom(self, root):
        unregisterViews(root.service_view_registry)
    
def registerViews(reg):
    reg.register('edit', _meta_type, ['edit', 'StaticSite'])    

def unregisterViews(reg):
    reg.unregister('edit', _meta_type)

def configureSecurity(root):
    """Update the security tab settings to the Silva defaults.
    """
    add_permissions = ('Add Static Sites',)
    for add_permission in add_permissions:
        root.manage_permission(add_permission, roleinfo.AUTHOR_ROLES)
    
def configureAddables(root):
    addables = [_meta_type]
    new_addables = root.get_silva_addables_allowed_in_container()
    for a in addables:
        if a not in new_addables:
            new_addables.append(a)
    root.set_silva_addables_allowed_in_container(new_addables)        

install = StaticSiteInstaller(_extensionName, IExtension)
