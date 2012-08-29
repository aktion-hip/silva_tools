# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from silva.core.layout.interfaces import ISilvaSkin
from silva.core import conf as silvaconf
from silva.core.layout.porto.interfaces import IPorto

class IKarthago(IPorto):
    """Karthago layer used to attach resources.
    """
    silvaconf.resource('css/karthago.css')

class IKarthagoSkin(IKarthago, ISilvaSkin):
    """Skin for Karthago Layout.
    """
    silvaconf.skin('KarthagoLayout')
