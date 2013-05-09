# -*- coding: utf-8 -*-
# Copyright (c) 2012 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from silva.core.layout.interfaces import ISilvaSkin
from silva.core import conf as silvaconf

from silva.core.layout.porto.interfaces import IPorto

class IRipla(IPorto):
    """Ripla layer used to attach resources.
    """
    silvaconf.resource('styles.css')
    silvaconf.resource('pygment_trac.css')

class IRiplaSkin(IRipla, ISilvaSkin):
    """Skin for Ripla Layout.
    """
    silvaconf.skin('RiplaLayout')
