# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from silva.core.layout.interfaces import ISilvaSkin
from silva.core import conf as silvaconf

from silva.core.layout.porto.interfaces import IPorto

class IHip(IPorto):
    """Hip layer used to attach resources.
    """
    silvaconf.resource('main.css')
    silvaconf.resource('print.css')
    silvaconf.resource('aural.css')

class IHipSkin(IHip, ISilvaSkin):
    """Skin for Hip Layout.
    """
    silvaconf.skin('HipLayout')
