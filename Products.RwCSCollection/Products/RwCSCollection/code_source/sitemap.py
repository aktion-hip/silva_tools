# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

import os

#Zope
from Globals import InitializeClass, package_home
from AccessControl import ClassSecurityInfo
from zope.interface import implements

#Formulator
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm

#Silva
from silva.core import conf as silvaconf

from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.CodeSource import CodeSource
from Products.Silva.SilvaPermissions import ViewManagementScreens, ChangeSilvaAccess, AccessContentsInformation

# SilvaLayout
#from Products.SilvaLayout.browser.tree import NotPublic, NotVisible

#from Products.RwLayout.browser.tree import IsInfrastructure

from Products.RwCSCollection.code_source.CodeSourceHelper import AbstractCSEditForm, AbstractCSAddForm, manage_addCSBase
from Products.RwCSCollection.code_source.SitemapCode import SitemapRenderingAdapter
from Products.RwLayout.rw_layout import getLocalSite

pjoin = os.path.join
_phome = package_home(globals())
_folder = 'www'
_script_id = 'view'

class EditCSSiteMapForm(AbstractCSEditForm):
    def _getActionName(self):
        return "manage_editCodeSource"
    def _getDescription(self):
        return "Edit SiteMap Code Source"

class SiteMap(CodeSource):
    __doc__ = '''Codes source for displaying the site's sitemap.'''

    implements(IExternalSource)
    meta_type = 'CS Sitemap'
    silvaconf.factory('manage_addSiteMapForm')
    silvaconf.factory('manage_addSiteMap')
    silvaconf.icon('code_source/www/codesource.png')

    security = ClassSecurityInfo()
    
    security.declareProtected(ViewManagementScreens, 'editCodeSource')
    editCodeSource = EditCSSiteMapForm()    
    
    def __init__(self, id):
        CodeSource.inheritedAttribute('__init__')(self, id)
        self._script_id = _script_id
        self._data_encoding = 'UTF-8'
        self._description = self.__doc__

    def manage_afterAdd(self, item, container):
        self._set_form()
        self._set_views()

    security.declareProtected(ChangeSilvaAccess, 'refresh')
    def refresh(self):
        """reload the form and pt"""
        if _script_id in self.objectIds():
            self.manage_delObjects([_script_id])
        self._set_form()
        self._set_views()
        return 'refreshed form and script'
    
    def _set_form(self):
        self.parameters = ZMIForm('form', 'Properties Form')
        f = open(pjoin(_phome, _folder, 'sitemap.form'))
        XMLToForm(f.read(), self.parameters)
        f.close()

    def _set_views(self):
        pass
            
    def _add_python_script(self, script, obj_id):
        if hasattr(self.aq_explicit, _script_id):
            return
        
        f = open(pjoin(_phome, _folder, script), 'rb')
        text = f.read()
        f.close()
        self.manage_addProduct['PythonScripts'].manage_addPythonScript(obj_id)
        pscript = getattr(self, obj_id)
        pscript.write(text)

    security.declareProtected(AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """Render HTML for code source
        """
        #0=flat, 1=indented
        list_type = int(parameters.get('list_type', 0))
        #comma separated list of Silva containers to filter from sitemap display
        to_ignore = parameters.get('to_ignore', '')
        
        sitemap = SitemapRenderingAdapter(getLocalSite(content.get_container(), request), request)
        sitemap.set_filters((InfrastructureFilter([item.strip() for item in to_ignore.split(',')]),))

        return sitemap.render(list_type)
    
InitializeClass(SiteMap)


class InfrastructureFilter(object):
    def __init__(self, infrastructure_items):
        self._infrastructure_items = infrastructure_items
    def filter(self, context):
        if context.getId() in self._infrastructure_items:
            return True
        return False
    def __call__(self, context):
        return self.filter(context)

###

class AddCSSiteMapForm(AbstractCSAddForm):
    def _getActionName(self):
        return "manage_addSiteMap"
    def _getName(self):
        return "manage_addSiteMapForm"
    def _getDescription(self):
        return "Add SiteMap, a Silva CodeSource variant that allows displaying the site's documents."

manage_addSiteMapForm = AddCSSiteMapForm()

def manage_addSiteMap(context, id, title, REQUEST=None):
    """Add a SiteMap code source"""
    return manage_addCSBase(SiteMap, context, id, title, REQUEST=REQUEST)
