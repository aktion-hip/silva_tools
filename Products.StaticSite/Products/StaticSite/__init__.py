# -*- coding: utf-8 -*-
# Copyright (c) 2012 RelationWare. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface
from silva.core.conf.installer import DefaultInstaller
from silva.core import conf as silvaconf
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
        configureSecurity(root)
        configureAddables(root)


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
