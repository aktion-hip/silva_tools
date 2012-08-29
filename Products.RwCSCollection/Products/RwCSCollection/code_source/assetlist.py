# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

import os

#Zope
from App.Common import package_home
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Formulator
from Products.Formulator.Errors import ValidationError, FormValidationError
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm

#Silva
from silva.core import conf as silvaconf

from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.CodeSource import CodeSource
from Products.Silva.SilvaPermissions import ViewManagementScreens, ChangeSilvaAccess, AccessContentsInformation
from Products.Silva.helpers import add_and_edit

from Products.Silva.Image import Image
from Products.Silva.File import File

from Products.RwCSCollection.code_source.CodeSourceHelper import AbstractCSEditForm, AbstractCSAddForm, manage_addCSBase
from Products.RwCSCollection.code_source.AssetListCode import AssetList as AssetRenderer

types = [File.meta_type, Image.meta_type]
get_id_strategies = ['get_title_or_id', 'getId']

pjoin = os.path.join
_phome = package_home(globals())
_folder = 'www'
_script_id = 'view'

_tmpl_script = 'get_asset_templates'
_tmpl = u"""
<div class="tablemargin">
  <table class="silvatable grid" cellspacing="0" cellpadding="3">
    %s
  </table>
</div>"""
_item_render_template="""<a href="%s" title="opens %s '%s' (%s) in new window" target="_blank">%s%s</a>"""
_item_template="""<tr><td class="asset_list">%s</td></tr>"""
_section_template="""<tr><td><h4>%s</h4></td></tr>"""

class EditCSAssetListForm(AbstractCSEditForm):
    def _getActionName(self):
        return "manage_editCodeSource"
    def _getDescription(self):
        return "Edit AssetList Code Source"   
    def _before_exec(self, kw):
        kw['supress_content'] = True

class AssetList(CodeSource):
    __doc__ = '''Codes source for listing assets in a Silva container.'''

    implements(IExternalSource)
    meta_type = 'CS Asset List'
    silvaconf.factory('manage_addAssetListForm')
    silvaconf.factory('manage_addAssetList')
    silvaconf.icon('code_source/www/codesource.png')
    
    security = ClassSecurityInfo()
    
    security.declareProtected(ViewManagementScreens, 'editCodeSource')
    editCodeSource = EditCSAssetListForm()    
    
    def __init__(self, id):
        CodeSource.inheritedAttribute('__init__')(self, id)
        self._script_id = _tmpl_script
        self._data_encoding = 'UTF-8'
        self._description = self.__doc__

    def manage_afterAdd(self, item, container):
        self._set_form()
        self._set_views()

    security.declareProtected(ChangeSilvaAccess, 'refresh')
    def refresh(self):
        """reload the form and pt"""
        if _tmpl_script in self.objectIds():
            self.manage_delObjects([_tmpl_script])
        self._set_form()
        self._set_views()
        return 'refreshed form and script'
    
    def _set_form(self):
        self.parameters = ZMIForm('form', 'Properties Form')
        f = open(pjoin(_phome, _folder, 'assetlist.form'))
        XMLToForm(f.read(), self.parameters)
        f.close()

    def _set_views(self):
        self._add_python_script(_tmpl_script + '.py', _tmpl_script)
            
    def _add_python_script(self, script, obj_id):
        if hasattr(self.aq_explicit, obj_id):
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
        container = content.get_container()
        #asset_type: 0 (all), 1 (files), 2(images)
        asset_type = int(parameters.get('asset_type', 0))
        #show_size: display the asset's size?
        show_size = int(parameters.get('show_size', 0))
        #sort_field: sort asset list by title or id?
        sort_field = int(parameters.get('sort_field', 0))
        
        templates = self._get_asset_templates()
        if asset_type:
            assets = container.get_assets_of_type(types[meta_type - 1])
        else:
            assets = container.get_assets()        

        assetList = AssetRenderer(assets, "")
        assets = assetList.render(templates.get('item_render_template', _item_render_template), 
                                  templates.get('item_template', _item_template),
                                  templates.get('section_template', _section_template),
                                  show_size, 
                                  get_id_strategies[sort_field])
        if not assets:
            return ""
        return _tmpl %assets
    
    def _get_asset_templates(self):
        templates = {'item_render_template': _item_render_template,
                     'item_template': _item_template,
                     'section_template': _section_template,
                     }
        if hasattr(self, _tmpl_script):
            try:
                tdir = getattr(self, _tmpl_script)()
                templates['item_render_template'] = tdir.get('item_render_template', _item_render_template) 
                templates['item_template'] = tdir.get('item_template', _item_template) 
                templates['section_template'] = tdir.get('section_template', _section_template) 
            except:
                pass
        return templates        

InitializeClass(AssetList)

###

class AddCSAssetListForm(AbstractCSAddForm):
    def _getActionName(self):
        return "manage_addAssetList"
    def _getName(self):
        return "manage_addAssetListForm"
    def _getDescription(self):
        return "Add AssetList, a Silva CodeSource variant that allows displaying the container's assets."

manage_addAssetListForm = AddCSAssetListForm()

def manage_addAssetList(context, id, title, REQUEST=None):
    """Add a SiteMap code source"""
    return manage_addCSBase(AssetList, context, id, title, REQUEST=REQUEST)
