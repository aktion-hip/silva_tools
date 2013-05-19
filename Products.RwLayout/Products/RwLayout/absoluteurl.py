# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from five import grok

from zope.proxy import sameProxiedObjects
from zope.interface import Interface
from zope.publisher.interfaces import IRequest
from zope.component import getMultiAdapter
from OFS.interfaces import ITraversable
from Products.Five.component.interfaces import IObjectManagerSite

from silva.core.interfaces import ISilvaObject, IFolder, IRoot
#from infrae.wsgi.interfaces import IVirtualHosting


class IRwUrl(Interface):
    def breadcrumbs():
        """Returns a tuple like ({'name':name, 'url':url}, ...)

        Name is the name to display for that segment of the breadcrumbs.
        URL is the link for that segment of the breadcrumbs.
        """
    
class RwUrl(grok.MultiAdapter):
    grok.adapts(ISilvaObject, IRequest)
    grok.provides(IRwUrl)
    grok.name('rw_url')

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def breadcrumbs(self):
        context = self.context
        request = self.request

        model = context.aq_inner
        if self.getStopCondition(model):
            return ({'name': model.get_short_title(), 'url': model.absolute_url()},)

        if isinstance(context, Exception):
            return ({'name':'', 'url': '.'}, )

        base = tuple(getMultiAdapter((model.aq_parent, request), name='rw_url').breadcrumbs())
        base += ({'name': context.get_short_title(),
                  'url': "%s/%s" % (base[-1]['url'], context.getId()),
                  }, )
        return base

    def getStopCondition(self, container):
        '''
        Returns true if recursive upward traversal has to stop.
        Subclasses may override.
        @param container: the actual container object
        '''
        return (container is None or
                self._isLocalSite(container) or
                IRoot.providedBy(container) or
                #self._isVirtualHostRoot(container) or
                not ITraversable.providedBy(container))
        
    def _isLocalSite(self, container):
        try:
            return IObjectManagerSite.providedBy(container)
        except:
            return False        

    #def _isVirtualHostRoot(self, context):
    #    return sameProxiedObjects(IVirtualHosting(context).getVirtualRoot(), context)
