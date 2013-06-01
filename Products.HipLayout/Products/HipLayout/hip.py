# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt
from five import grok
from zope.cachedescriptors.property import CachedProperty

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.layout.porto import porto

# Silva
from silva.core.interfaces import IGhost
from Products.SilvaDocument.interfaces import IDocument

from Products.RwLayout import rw_layout
from Products.HipLayout.skin import IHip
from Products.HipLayout.configuration import infrastructure

from Products.Silva.Publication import Publication
from Products.Silva.Folder import Folder
from Products.Silva.Link import Link

_menu_objects = [Publication.meta_type, Folder.meta_type, Link.meta_type]

silvaconf.layer(IHip)

class MainLayout(rw_layout.MainLayout):
    pass

class Layout(rw_layout.Layout):
    pass

class HipInserts(silvaviews.Viewlet):
    grok.viewletmanager(porto.HTMLHeadInsert)

    def render(self):
        return u'''    <meta name="copyright" content="Code: Benno Luthiger, RelationWare" />
    <meta name="copyright" content="Design: Vit Dlouhy [Nuvio - www.nuvio.cz]" />
    <link rel="shortcut icon" type="image/x-icon" href="%s" />''' %self.static['favicon.png']()

class Favicon(silvaviews.Viewlet):
    grok.viewletmanager(porto.HTMLHeadInsert)
    
    def render(self):
        return ''


class Mainmenu(silvaviews.ContentProvider):
    @CachedProperty    
    def menu_items(self):
        context = self.context
        site_root = rw_layout.getLocalSite(context.get_publication(), self.request)
        out = []
        model_url = context.absolute_url()
        for item in site_root.get_ordered_publishables():
            if not item.meta_type in _menu_objects: continue
            if item.getId() in infrastructure: continue
            
            item_url = item.absolute_url()
            out.append({'state':model_url.startswith(item_url) and 'active' or 'default',
                       'url':item_url,
                       'label':item.get_short_title(),
                       })
        return out

class Breadcrumbs(rw_layout.Breadcrumbs):
    pass

class Footer(silvaviews.ContentProvider):
    pass

class Navigation(rw_layout.Navigation):
    @CachedProperty
    def items(self):
        out = []
        context = self.context
        container = context.get_container()
        site_root = rw_layout.getLocalSite(container, self.request)
        if container == site_root:
            for item in container.get_ordered_publishables():
                if not item.meta_type in _menu_objects: continue
                if item.getId() in infrastructure: continue
                out.append({'url':item.absolute_url(), 'label':item.get_short_title(), 'state':"category-default"})
        else:
            model_url = context.absolute_url()
            for item in container.get_ordered_publishables():
                out.append({'url':item.absolute_url(), 'label':item.get_short_title(), 
                            'state':model_url.startswith(item.absolute_url()) and "category-active" or "category-default"})
        return out

class Portlet(silvaviews.ContentProvider):
    def portlets(self):
        '''
        Renders the first paragraph of all ghost objects and documents contained in the site root.
        '''
        view = self.context
        root = rw_layout.getLocalSite(view, self.request)
        portlets = []
        index = root.get_default()
        for portlet in root.get_ordered_publishables():            
            model = None
            if IGhost.providedBy(portlet):
                model = portlet.getLastVersion().get_haunted()
            elif IDocument.providedBy(portlet):
                model = portlet
            if not model: continue
            
            view.REQUEST.model = model
            version = model.get_viewable()
            content = None
            if version:
                content = self._renderVersion(version, portlet.get_title(), model.absolute_url())                
            if content:
                portlets.append(content)

        return portlets and portlets or []

    def _renderVersion(self, version, title, url):
        doc_root = version.content.documentElement
        paras = doc_root.getElementsByTagName('p')
        if not paras:
            return None
        return {'url':url, 'title':title, 'content':paras[0], 'more_url':(len(paras) > 1) and url or ""}
