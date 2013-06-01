# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt
from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface

_extensionName = "RwLayout"
silvaconf.extensionName(_extensionName)
silvaconf.extensionTitle("RelationWare Layout")
silvaconf.extensionDepends(("SilvaDocument", "SilvaExternalSources"))

from Products.PythonScripts.Utility import allow_module
allow_module('Products.RwLayout.helpers')


class IExtension(Interface):
    '''
    RwLayout Extension
    '''

class RwLayoutInstaller(DefaultInstaller):

    def install_custom(self, root):
        pass
    
    def uninstall_custom(self, root):
        pass
    
install = RwLayoutInstaller(_extensionName, IExtension)
