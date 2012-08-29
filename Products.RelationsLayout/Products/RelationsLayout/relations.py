# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from zope.cachedescriptors.property import CachedProperty

from silva.core.views import views as silvaviews
from silva.core.layout.interfaces import IMetadata
from silva.core.layout.porto import porto
from silva.core import conf as silvaconf

from Products.RwLayout import rw_layout
from Products.RelationsLayout.skin import IRelations

silvaconf.layer(IRelations)

metadata_id = "relations-layout"

class Layout(rw_layout.Layout):
    def showSFLogo(self):
        context = self.context
        localSite = rw_layout.getLocalSite(self.context.get_publication(), self.request)
        metadata = IMetadata(localSite)
        try:
            value = metadata(metadata_id, "plain_layout")
            return not value and 1 or 0
        except:
            pass
        return 0

class MainMenu(porto.Layout):
    def get_menu_items(self):
        context = self.context
        localSite = rw_layout.getLocalSite(self.context.get_publication(), self.request)
        metadata = IMetadata(localSite)
        try:
            main_menu = metadata(metadata_id, "main_menu")
            if main_menu:
                return self._process(main_menu, localSite, context.absolute_url())
        except:
            pass
        return []
        
    def _process(self, main_menu, site_root, context_url):
        items = []        
        for menu_item in main_menu.split(","):
            menu_parts = menu_item.split("|")
            
            activity_class = u'inactive'
            target_url = menu_parts[1].strip()
            try:
                target = site_root.unrestrictedTraverse(target_url.split("/"))
                if target:
                    target_url = target.absolute_url()
                    if context_url.find(target_url) != -1:
                        activity_class = u'active'
            except:
                pass
            items.append({'url':target_url, 
                          'label':menu_parts[0].strip(), 
                          'class_active':activity_class})
        return items

class Navigation(rw_layout.Navigation):
    pass

class Breadcrumbs(rw_layout.Breadcrumbs):
    pass
