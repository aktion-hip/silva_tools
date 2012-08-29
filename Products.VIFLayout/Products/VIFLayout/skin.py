# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from silva.core.layout.interfaces import ISilvaSkin
from silva.core import conf as silvaconf

from silva.core.layout.porto.interfaces import IPorto

class IVif(IPorto):
    """VIF layer used to attach resources.
    """
    #silvaconf.resource('css/book.css')
    silvaconf.resource('css/schema2.css')
    silvaconf.resource('css/schema.css')
    silvaconf.resource('css/viflayout.css')

class IVifSkin(IVif, ISilvaSkin):
    """Skin for VIF Layout.
    """
    silvaconf.skin('VIFLayout')
