# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

# Python
from time import localtime
from xml.sax.saxutils import escape

# Zope
from zope.interface import Interface, implements

# Silva
from silva.core import interfaces
from silva.core.views.interfaces import IPreviewLayer
#from Products.Silva.adapters.tocrendering import compute_default_show_types, TOCRenderingAdapter
from cgitb import html

_marker = []

def compute_default_show_types():
    return []

#class SitemapRenderingAdapter(TOCRenderingAdapter):
class SitemapRenderingAdapter(object):
    """Represents the structure of the sitemap.
    """
    def __init__(self, site_root, request):
        self._context = site_root
        self._filter = SiteMapFilter(self._context.service_toc_filter)
        self._request = request
        
    def set_filters(self, filters):
        '''
        Sets the sitemap's filters
        @param filters: List of filters
          filter should be a callable accepting one argument that returns True if the argument should be filtered out, 
          False if it should not be filtered out.
        '''
        for filter in filters:
            self._filter.registerFilter(filter)
        
    def _get_sitemap_iterator(self, container, indent=0, show_types=_marker, sort_order='silva'):
        if show_types == _marker:
            show_types = compute_default_show_types()
            
        items = self._get_container_items(container, sort_order, show_types)
        for (name, item) in items:
            if not (item.is_published() or
                    interfaces.IAsset.providedBy(item)) or \
                   (name=='index'):
                continue
            if self._filter.filter(item):
                    continue
            yield (indent, item)
            if interfaces.IContainer.providedBy(item):
                for (depth, object) in self._get_sitemap_iterator(item, indent+1, show_types=show_types):
                    yield (depth, object)

    
    def render(self, indenting=True):
        """Renders the sitemap.
        """
        show_types = compute_default_show_types()
        public = not IPreviewLayer.providedBy(self._request)
        
        isRoot = True
        html = []
        prev_depth = [-1]
        depth = -1

        clazz = indenting and ChildStruct or ChildStructFlat
        actStruct = None
        for (depth, item) in self._get_sitemap_iterator(self._context, show_types=show_types):
            previousDepth = prev_depth[-1]
            if previousDepth < depth: #down one level
                actStruct = clazz(actStruct, context=self._context)
                prev_depth.append(depth)
            elif previousDepth > depth: #up one level
                for i in range(previousDepth - depth):
                    prev_depth.pop()
                    actStruct = actStruct.close()
            elif previousDepth == depth: #same level
                pass
            
            actStruct.add_item(ItemRenderer(item, public)(depth, isRoot))
            isRoot = False 
        else:
            #do this when the loop is finished, to
            #ensure that the lists are ended properly
            #the last item in the list could part of a nested list (with depth 1,2,3+, etc)
            #so need to loop down the depth and close all open lists
            while True:
                parent = actStruct.close()
                if parent:
                    actStruct = parent
                else:
                    break
            html.append('</ul>')

        return '\n'.join(actStruct.get_items())
    
    def _decorateTitle(self, title, depth, isRoot, item):
        if isRoot: return title
        if depth: return title
        return interfaces.IContainer.providedBy(item) and ('<h4>%s</h4>' %title) or title        
    
    def traverse(self):
        """Traverse the tree. 
           Use this method for debugging purpose.
        """
        self._root.traverse(0)


class RootRenderer(object):
    def render(self, context):
        return '<h3>%s</h3>' %escape(context.get_title())
    def __call__(self, context):
        return self.render(context)

class ItemRenderer(object):
    a_templ = '<a href="%s">%s</a>'
    date_tmpl = '&#160;- <span %s>%s</span>'

    def __init__(self, item, public):
        self._isContainer = interfaces.IContainer.providedBy(item)        
        title = (public and item.get_title() or item.get_title_editable()) or item.id
        self._out = self._add = ''
        try:
            self._out = ItemRenderer.a_templ %(item.absolute_url(), escape(title))
            
            last_mod = item.get_modification_datetime()
            span_class = self._age(last_mod) < 4 and 'class="highlited"' or ''
            self._add = ItemRenderer.date_tmpl %(span_class, last_mod)
        except:
            try:
                url = item.absolute_url()
                self._out = ItemRenderer.a_templ %(url, "Problem with object at %s" %url)
            except:
                self._out = ItemRenderer.a_templ %('', "Problem with object")                
        
    def render(self, depth, isRoot):
        if isRoot: return self._out + self._add
        if depth: return self._out + self._add
        return self._isContainer and ('<h4>%s</h4>' %self._out) or self._out + self._add
    
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
        
    def __call__(self, depth, isRoot):
        return self.render(depth, isRoot)

    
class ChildStruct(object):
    def __init__(self, parent, content='<ul>', context=None):
        self._parent = parent
        if self._parent:
            self._parent._items.pop()
            self._parent._items.append(self)
            self._parent._items.append(ItemStruct(self, '</li>'))            
            self._items = [ItemStruct(self, content='<ul>')]
        else:
            self._items = [ItemStruct(self, content='<ul class="sitemap">')]
            self.add_item(RootRenderer()(context))
    def close(self):
        self._items.append(ItemStruct(self, '</ul>'))
        return self._parent
    def add_item(self, content):
        if not content: return
        self._items.append(ItemStruct(self, '<li>'))
        self._items.append(ItemStruct(self, content))
        self._items.append(ItemStruct(self, '</li>'))
    def get_items(self):
        out = []
        for item in self._items:
            out += item.get_items()
        return out
    
class ChildStructFlat(ChildStruct):
    def __init__(self, parent, content='', context=None):
        self._parent = parent
        if self._parent:
            self._parent._items.append(self)
            self._items = [ItemStruct(parent=self, content='')]
        else:
            self._items = [ItemStruct(parent=self, content='<ul class="sitemap">')]
            self.add_item(RootRenderer()(context))
    def close(self):
        if not self._parent:
            self._items.append(ItemStruct(self, '</ul>'))
        return self._parent

class ItemStruct(ChildStruct):
    def __init__(self, parent=None, content='', context=None):
        self._parent = parent
        self._content = content
    def get_items(self):
        return [self._content]
    
class SiteMapFilter(object):
    def __init__(self, tocfilter):
        self._tocfilter = tocfilter
        self._filters = []
        
    def registerFilter(self, filter):
        self._filters.append(filter)
        
    def filter(self, context):
        '''
        @return: True if the argument should be filtered out, False if it should not be filtered out.
        '''
        if self._tocfilter.filter(context):
            return True
        for filter in self._filters:
            if filter(context):
                return True
        return False
    