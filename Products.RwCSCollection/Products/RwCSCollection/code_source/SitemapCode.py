# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

# Python
from time import localtime
from xml.sax.saxutils import escape

# Zope
from five import grok
from zope import schema
from zope.component import getUtility
from zope.interface import Interface, directlyProvides
from zope.contentprovider.interfaces import ITALNamespaceData
from zope.traversing.browser import absoluteURL

# Silva
from silva.core.services.interfaces import IContentFilteringService
from silva.core.interfaces import IContainer, IPublishable, IOrderManager
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IPreviewLayer
from Products.RwLayout.rw_layout import getLocalSite


_marker = []
_content_type = ["Silva Page", "Silva Document", "Silva Folder", "Silva Publication", "Silva Find", "Silva Ghost", "Silva Ghost Folder", "Silva Indexer", "Silva AutoTOC"]

def compute_default_show_types():
    return []

class ISitemapRenderingOptions(Interface):
    list_type = schema.Int(
        title=u"List indented (1) of flat (0)")
    to_ignore = schema.List(
        title=u'Containers types to ignore', value_type=schema.TextLine())
    model = toc_container = schema.Object(
        title=u"The model containing the sitemap cs", schema=IPublishable)
    
directlyProvides(ISitemapRenderingOptions, ITALNamespaceData)
    

class SitemapRendering(silvaviews.ContentProvider):
    """Render a site map
    """
    grok.name('sitemap')
    grok.context(Interface)
    grok.view(Interface)
    grok.implements(ISitemapRenderingOptions)
    
    def __init__(self, *args):
        super(SitemapRendering, self).__init__(*args)
        self.list_type = '0'
        self.to_ignore = []
        self.model = None

    def list_container_items(self, container, is_displayable):
        """List the given container items that are a candidates to be
        listed in the TOC.
        """
        items = filter(
            is_displayable,
            container.objectValues(_content_type))
        items.sort(
            key=IOrderManager(container).get_position,
            reverse=False)
        return items        
    
    def is_preview_displayable(self, item):
        """Return true if the item is displayable in preview mode.
        """
        return IPublishable.providedBy(item) and not item.is_default()

    def is_public_displayable(self, item):
        """Return true if the item is displayable in public mode.
        """
        return (IPublishable.providedBy(item) and
                (not item.is_default()) and
                item.is_published())
        
    def list_toc_items(self, container, level, is_displayable, to_ignore=[]):
        """Yield for every element in this toc.  The 'depth' argument
        limits the number of levels, defaults to unlimited.
        """
        filter_content = getUtility(
            IContentFilteringService).filter(self.request)

        for item in filter_content(self.list_container_items(
                container, is_displayable)):
            
            if (level == 0) and item.id in to_ignore:
                continue

            yield (level, item)

            if IContainer.providedBy(item):
                for data in self.list_toc_items(item, level + 1, is_displayable):
                    yield data
    
    def render(self):
        to_ignore = [entry.strip() for entry in self.to_ignore.split(',')]
        public = not IPreviewLayer.providedBy(self.request)
        
        is_displayable = public and self.is_public_displayable or self.is_preview_displayable
        html = []
        a_templ = '<a href="%s">%s</a>'
        isIndented = int(self.list_type)

        localRoot = getLocalSite(self.model, self.request)
        depth = -1
        prev_depth = [-1]
        item = None
        for (depth, item) in self.list_toc_items(localRoot, 0, is_displayable, to_ignore):
            pd = prev_depth[-1]
            if pd < depth: #down one level
                if depth == 0 or isIndented:
                    html.append('<ul>')
                prev_depth.append(depth)
            elif pd > depth: #up one level
                for i in range(pd-depth):
                    prev_depth.pop()
                    if isIndented:
                        html.append('</ul></li>')
            elif pd == depth: #same level
                html.append('</li>')
            css_class = (IContainer.providedBy(item) and depth == 0) and ' class="topContainer"' or ''
            html.append('<li%s>' %css_class)
            title = (public and item.get_title() or item.get_title_editable()) or item.id
            
            html.append(a_templ % (absoluteURL(item, self.request), escape(title)) + self._add(item))
        else:
            #do this when the loop is finished, to
            #ensure that the lists are ended properly
            #the last item in the list could part of a nested list (with depth 1,2,3+, etc)
            #so need to loop down the depth and close all open lists
            while depth >= 0:
                html.append('</li></ul>')
                depth -= 1
        if not isIndented:
            html.append('</ul>')
        return u'\n'.join(html)
        
    def _add(self, item):
        try:
            date_tmpl = '&#160;- <span %s>%s</span>'
            last_mod = item.get_modification_datetime()
            span_class = self._age(last_mod) < 4 and 'class="highlited"' or ''
            return date_tmpl %(span_class, last_mod.strftime('%d.%m.%Y'))
        except:
            pass
        return ""
        
    def _age(self, date):
        if not date:
            return 'n/a'
        
        # calculation of Rata Die by Peter Baum, published in Scientific American, May 1997 issue
        now = localtime()
        d_now = now[2]
        m_now = now[1]
        y_now = now[0]
        
        if m_now < 3: 
            m_now = m_now + 12 
            y_now = y_now - 1 
        
        rd_now = d_now + (153*m_now - 457)/5 + 365*y_now + y_now/4 - y_now/100 + y_now/400 - 306 
    
        d = date.day()
        m = date.month()
        y = date.year()
        
        if m < 3: 
            m = m + 12 
            y = y - 1 
        
        rd = d + (153*m - 457)/5 + 365*y + y/4 - y/100 + y/400 - 306 
        return rd_now - rd
