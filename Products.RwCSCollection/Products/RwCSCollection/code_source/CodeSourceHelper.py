# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

#python
import os

#from zope.app.container.interfaces import IObjectAddedEvent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.Silva.helpers import add_and_edit
from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources import ExternalSource

pjoin = os.path.join
icondata = pjoin(
            os.path.abspath(
                os.path.dirname(ExternalSource.__file__)
            ), 'www/codesource.png')

_folder = 'www'

##interface for code sources in this layer, used for event subscription
class IRwSource(IExternalSource):
    def refresh():
        """Refreshes the code source instance"""
        pass

##classes for add/edit forms
class AbstractCSForm(PageTemplateFile):
    '''
    Base class for all add forms to create this product's code source instances.
    '''
    def __init__(self):
        PageTemplateFile.__init__(self, pjoin(_folder, self._getPageTemplateName()), 
                                  globals(), __name__=self._getName())

    def _exec(self, bound_names, args, kw):
        """Call a Page Template"""
        kw['form_action'] = self._getActionName()
        kw['form_description'] = self._getDescription()
        self._before_exec(kw)
        return PageTemplateFile._exec(self, bound_names, args, kw)
    
    def _getName(self):
        '''Name of the factory method that renders the ZMI form to create the code source instance.'''
        return ""
    
    def _getActionName(self):
        '''Name of the form's action that creates the code source instance.'''
        return ""
    
    def _getDescription(self):
        '''Text displayed on the page whith the form.'''
        return ""
    
    def _getPageTemplateName(self):
        return ''
    
    def _before_exec(self, kw):
        '''Hook for subclasses
        '''
    

## This class reuses the page template 'www/rw_CSAdd.zpt' for object instantiation in the ZODB.
class AbstractCSAddForm(AbstractCSForm):
    '''
    Base class for all add forms to create this product's code source instances.
    '''
    def _getPageTemplateName(self):
        return 'rw_CSAdd.zpt'

## This class reuses the page template 'www/rw_CSEdit.zpt' for object instantiation in the ZODB.
class AbstractCSEditForm(AbstractCSForm):
    '''
    Base class for all edit forms for this product's code source instances.
    '''
    def _getPageTemplateName(self):
        return 'rw_CSEdit.zpt'
    
    def _getName(self):
        '''Name of the factory method that renders the ZMI form to create the code source instance.'''
        return "editCodeSource"


## This function provides the functionality to add the code source instance.
## The code source module can delegate to this function to create an instance of the object 'class_ref'. 
def manage_addCSBase(class_ref, context, id, title, postCreationHook=None, REQUEST=None):
    """Add a code source object"""
    if id in context.objectIds():
        return u"""<p><a href="%s/manage_main">back</a></p><p><b>Object with id '%s' exists yet.</b></p>""" %(context.absolute_url(), id)

    cs = class_ref(id)
    cs.title = unicode(title, 'UTF-8')
    context._setObject(id, cs)
    if postCreationHook:
        postCreationHook(cs)
    add_and_edit(context, id, REQUEST, screen='editCodeSource')
    return ''

## event subscription
def added_CSInstance(object, event):
    #if object != event.object or (not IObjectAddedEvent.providedBy(event)) \
    #   or (not IRwSource.providedBy(object)):
    if object != event.object \
       or (not IRwSource.providedBy(object)):
        return
    object.refresh()

