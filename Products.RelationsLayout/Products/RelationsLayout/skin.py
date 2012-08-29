# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from silva.core.layout.interfaces import ISilvaSkin
from silva.core import conf as silvaconf

from silva.core.layout.porto.interfaces import IPorto

class IRelations(IPorto):
    """Relations layer used to attach resources.
    """
    silvaconf.resource('relations.css')

class IRelationsSkin(IRelations, ISilvaSkin):
    """Skin for Relations Layout.
    """
    silvaconf.skin('RelationsLayout')
