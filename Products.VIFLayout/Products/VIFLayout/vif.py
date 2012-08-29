# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from zope.cachedescriptors.property import CachedProperty

from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

from Products.RwLayout import rw_layout
from Products.RelationsLayout import relations

from Products.VIFLayout.skin import IVif

silvaconf.layer(IVif)

class MainLayout(rw_layout.MainLayout):
    @CachedProperty
    def get_page_title(self):
        doctitle = self.context.get_title_or_id()
        prefix = ''
        if not doctitle.startswith('VIF:'):
            prefix = 'VIF: '
        return prefix + doctitle

class Navigation(rw_layout.Navigation):
    pass

class Breadcrumbs(rw_layout.Breadcrumbs):
    pass

class Layout(relations.Layout):
    pass

class MainMenu(relations.MainMenu):
    pass
