# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 RelationWare. All rights reserved.
# See also LICENSE.txt

import AccessControl

#from Products.SilvaExternalSources import install
from zope.interface import Interface
from silva.core.conf.installer import DefaultInstaller

from silva.core import conf as silvaconf

from Products.SilvaPhotoGallery.configuration import cs_container, dft_id, dft_title

_extensionName = "SilvaPhotoGallery"
silvaconf.extensionName(_extensionName)
silvaconf.extensionTitle('Silva Photo Gallery')
silvaconf.extensionDepends(["SilvaExternalSources"])


class IExtension(Interface):
    '''
    SilvaPhotoGallery Extension
    '''

class GalleryInstaller(DefaultInstaller):
    def install_custom(self, root):
        folder = getattr(root, cs_container, root)
        if hasattr(folder.aq_inner.aq_explicit, dft_id):
            return
        constructor = getattr(folder.manage_addProduct['SilvaPhotoGallery'], 'manage_addPhotoGallery')
        if constructor:
            constructor(dft_id, dft_title)
    
    def uninstall_custom(self, root):
        folder = getattr(root, cs_container, root)
        folder.manage_delObjects(dft_id)

install = GalleryInstaller(_extensionName, IExtension)
