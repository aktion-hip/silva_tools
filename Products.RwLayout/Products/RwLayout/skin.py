# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from silva.core.layout.interfaces import ISilvaSkin
from silva.core import conf as silvaconf
from silva.core.layout.porto.interfaces import IPorto


class IRelationWare(IPorto):
    """RelationWare layer used to attach resources.
    """
    silvaconf.resource('relations.css')

class IRelationWareSkin(IRelationWare, ISilvaSkin):
    """Skin for RelationWare Layout.
    """
    silvaconf.skin('RelationWare')
