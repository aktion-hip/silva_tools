# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from zope.cachedescriptors.property import CachedProperty
from zope.component import getMultiAdapter, getAdapter

from silva.core import conf as silvaconf
from silva.core.layout.porto import porto
from silva.core.views.interfaces import IVirtualSite
from silva.core.interfaces import ISiteManager

from Products.RwLayout.skin import IRelationWare
from Products.RwLayout.interfaces import IRwCustomRoot


silvaconf.layer(IRelationWare)

class MainLayout(porto.MainLayout):
    @CachedProperty
    def get_custom_root(self):
        '''
        @return: the custom root, i.e. the nearest container marked with 'IRwCustomRoot' or the site root.
        '''
        model = self.context
        site_root = _getSilvaRoot(self.request)
        while True: 
            if IRwCustomRoot.providedBy(model) or model == site_root:
                return model
            model = model.aq_inner.aq_parent
        return model
    

class Layout(porto.Layout):    
    @CachedProperty
    def site_title(self):
        return getLocalSite(self.context.get_publication(), self.request).get_title()
    
    @CachedProperty
    def site_url(self):
        return getLocalSite(self.context.get_publication(), self.request).absolute_url()


class Breadcrumbs(porto.Breadcrumbs):
    """Breadcrumbs.
    """
    def breadcrumbs(self):
        context = self.context
        adapter = getMultiAdapter((context, self.request), name='rw_url')
        return tuple(adapter.breadcrumbs())


class Navigation(porto.Navigation):
    """Navigation
    """

    def navigation_link_css_class(self, info, depth):
        # CSS class on a
        if info['current']:
            return 'subnav-on'
        if info['onbranch']:
            return 'subnav-off'
        return 'subnav-off'


class InfrastructureFilter(object):
    def __init__(self, infrastructure=[]):
        self._infrastructure = infrastructure
        
    def filter(self, context):
        # filter should be a callable accepting one argument that returns True
        # if the argument should be filtered out, False if it should not be
        # filtered out.
        if context.service_toc_filter.filter(context):
            return True
        return context.id in self._infrastructure


# utility functions

def getLocalSite(container, request):
    '''
    Returns the nearest root of a local site, i.e. a Silva Publication set with local site property.
    
    @param container: 
    @param request:
    @return: the local site or the Silva Root
    '''
    if container == _getSilvaRoot(request): return container
    if _isLocalSite(container): return container
    return getLocalSite(container.aq_parent.get_publication(), request)

def _isLocalSite(container):
    try:
        return ISiteManager(container).isSite()
    except:
        return False

def _getSilvaRoot(request):
    virtual_site = getAdapter(request, IVirtualSite)
    return virtual_site.get_root()        
