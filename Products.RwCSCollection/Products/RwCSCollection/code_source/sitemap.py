# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

import os
import logging

#Zope
from Globals import InitializeClass, package_home
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from zope.interface import implements

#Formulator
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm

#Silva
from silva.core import conf as silvaconf

from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.CodeSource import CodeSource
from Products.SilvaExternalSources.CodeSourceService import INSTALLERS
from Products.Silva.SilvaPermissions import ViewManagementScreens, ChangeSilvaAccess, AccessContentsInformation

from Products.RwCSCollection.code_source.CodeSourceHelper import AbstractCSEditForm, AbstractCSAddForm, manage_addCSBase
from Products.RwLayout.rw_layout import getLocalSite


pjoin = os.path.join
_phome = package_home(globals())
_folder = 'www'
_script_id = 'view'
_view_template = 'sitemap_view.pt'

logger = logging.getLogger('Products.RwCSCollection.sitemap')

class EditCSSiteMapForm(AbstractCSEditForm):
    def _getActionName(self):
        return "manage_editSiteMap"
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
        self._add_pt(_view_template)
        
    def _add_pt(self, template):
        if hasattr(self.aq_explicit, _script_id):
            return
        
        name, extension = os.path.splitext(template)
        installer = INSTALLERS.get(extension, None)
        if installer is None:
            logger.info(u"don't know how to install file %s for code source %s" % (template, 'sitemap'))
        else:
            with open(pjoin(_phome, _folder, template), 'rb') as data:
                installer(self, data, _script_id, extension)

    security.declareProtected(ViewManagementScreens, 'test_source')
    def test_source(self):
        # return a list of problems or None
        errors = []
        # in real life the parent of the form is the document. We try
        # to do the same here.
        root = self.get_root()
        if root.get_default():
            root = root.get_default()
        if self.parameters is not None:
            try:
                aq_base(self.parameters).__of__(root).test_form()
            except ValueError as error:
                errors.extend(error.args)
        if not self.title:
            errors.append(u'Missing required source title.')
        if errors:
            return errors
        return None
    
    security.declareProtected(ViewManagementScreens, 'manage_editSiteMap')
    def manage_editSiteMap(self, title, data_encoding, description=None,
        cacheable=None, previewable=None, usable=None):
        """ Edit CodeSource object
        """
        location = None
        msg = self.manage_editCodeSource(title, '', data_encoding, description, location, cacheable, previewable, usable)
        return msg.replace(u'<b>Warning</b>: no script id specified!<b>Warning</b>: This code source does not contain an object with identifier ""!', '')
    
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
