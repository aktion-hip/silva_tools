# -*- coding: utf-8 -*-
# Copyright (c) 2012 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt
from zope.cachedescriptors.property import CachedProperty

from silva.core.views import views as silvaviews
from silva.core.layout.porto import porto
from silva.core import conf as silvaconf

from Products.RwLayout import rw_layout
from Products.RiplaLayout.skin import IRipla

silvaconf.layer(IRipla)

class MainLayout(porto.MainLayout):
    @CachedProperty
    def get_site_title(self):
        return rw_layout.getLocalSite(self.context.get_publication(), self.request).get_title()

class Layout(rw_layout.Layout):
    pass

class Breadcrumbs(rw_layout.Breadcrumbs):
    pass

class Footer(silvaviews.ContentProvider):
    pass
