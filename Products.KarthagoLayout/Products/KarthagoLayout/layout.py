# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from zope.cachedescriptors.property import CachedProperty
from zope import component

from silva.core.views import views as silvaviews
from silva.core.layout.porto import porto
from silva.core import conf as silvaconf

from Products.RwLayout import rw_layout

from Products.KarthagoLayout.configuration import infrastructure
from Products.KarthagoLayout.skin import IKarthago

portlets_id = "portlets"

silvaconf.layer(IKarthago)

class Layout(rw_layout.Layout):
    pass
    
class Search(silvaviews.ContentProvider):
    def render(self):
        '''
        Returns the search widget
        '''
        tmpl = """  <form action="%s/search/">
    <input class="search-field" type="text" name="fulltext" size="22" />
    <input type="hidden" name="search_submit" value="Suchen" />
    <input class="button" type="submit" value="Suche" />
  </form>"""
        localSite = rw_layout.getLocalSite(self.context.get_publication(), self.request)
        return tmpl %localSite.absolute_url()
    
class Infrastructure(silvaviews.ContentProvider):
    def render(self):
        tmpl = u"""
<script language="JavaScript" type="text/javascript">
  function printpage() {
    if (window.print)
      window.print();
    else alert("Please use the printfunction in your browser.\\n\\nBitte benutzen Sie die Printfunktion Ihres Webbrowsers.");
  }
</script>        
<a href="%s/contact/">Kontakt</a> | <a href="%s/sitemap/">Übersicht</a> | <a href="javascript:printpage()">Drucken</a> | <a href="%s/edit">Login</a>
"""
        root_url = rw_layout.getLocalSite(self.context.get_publication(), self.request).absolute_url()
        return tmpl %(root_url, root_url, root_url)
        

class Navigation(rw_layout.Navigation):

    @CachedProperty
    def filter_service(self):
        return rw_layout.InfrastructureFilter(infrastructure)

class Portlet(silvaviews.ContentProvider):
    @CachedProperty
    def get_portlets(self):
        view = self.context
        root = rw_layout.getLocalSite(view.get_publication(), self.request)
        #we show the portlets only on the site root
        if (view != root) and (view != root.get_default()):
            return []
        
        folder = getattr(root, portlets_id, None)
        if not folder: return []

        portlets = []
        for indent, portlet in folder.get_public_tree():
            portlets.append(portlet)
        return portlets

class Footer(silvaviews.ContentProvider):
    @CachedProperty
    def modificationdate(self):
        date = self.layout.metadata['silva-extra']['modificationtime']
        if not date:
            return "n.n."
        return date.strftime("%d.%m.%Y")
