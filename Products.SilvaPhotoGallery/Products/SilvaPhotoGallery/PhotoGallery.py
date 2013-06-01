# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare. All rights reserved.
# See also LICENSE.txt
# $Revision: 4760 $
#
# Inspired by Marc's SilvaPhotoGallery Code Source (some code was copied from that product too).

import os

#Zope
from Globals import InitializeClass, package_home
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from zope.interface import implements
from OFS.Image import Image

#Silva
from silva.core import conf as silvaconf

from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.CodeSource import CodeSource
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit

#Formulator
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm

from Products.SilvaPhotoGallery.Renderer import Renderer
from Products.SilvaPhotoGallery.configuration import dft_language

_scripts = ['gallery_helper_scripts.js', 'lightbox.js', 'lightbox.css', 'photo_gallery.css']
_files = ['prototype.js', 'scriptaculous.js', 'effects.js']
_python = [] #['captions.xml']
_images = ['blank.gif', 'close.gif', 'loading.gif', 'minus.gif', 'next.gif', 'overlay.png', 'plus.gif', 'prev.gif']

pjoin = os.path.join
_phome = package_home(globals())
_folder = 'www'


class PhotoGallery(CodeSource):
    __doc__ = """A photo gallery to show thumbnails and the original pictures within a Silva document."""

    implements(IExternalSource)
    meta_type = 'Silva Photo Gallery'
    silvaconf.factory('manage_addPhotoGalleryForm')
    silvaconf.factory('manage_addPhotoGallery')
    silvaconf.icon('www/codesource.png')
    
    security = ClassSecurityInfo()
    
    security.declareProtected(SilvaPermissions.ViewManagementScreens, 'editCodeSource')
    editCodeSource = PageTemplateFile(
        _folder + '/photoGalleryEdit', globals(),  __name__='editCodeSource')      
    
    def __init__(self, id):
        CodeSource.inheritedAttribute('__init__')(self, id)
        self._script_id = ''
        self._data_encoding = 'UTF-8'
        self._description = self.__doc__
        
    def manage_afterAdd(self, item, container):
        self._set_form()
        self._set_views()

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                                'refresh')
    def refresh(self):
        """reload the form and pt"""
        self._set_form()
        self._set_views()
        return 'refreshed form and pagetemplate'

    def _set_form(self):
        self.parameters = ZMIForm('form', 'Properties Form')
        f = open(pjoin(_phome, _folder, 'photo_gallery_form.form'))
        XMLToForm(f.read(), self.parameters)
        f.close()

    def _set_views(self):        
        self._add_images()
        self._add_dtml()
        self._add_file()
        self._add_python()
        
    def _add_images(self):
        for image in _images:
            if hasattr(self.aq_inner, image):
                continue            
            f = open(pjoin(_phome, _folder, image), 'rb')
            self._setObject(image, Image(image, image, f))
            f.close()
            
    def _add_dtml(self):
        for script in _scripts:
            if hasattr(self.aq_inner, script):
                continue
            f = open(pjoin(_phome, _folder, script + '.dtml'), 'rb')
            text = f.read()
            f.close()
            self.manage_addDTMLMethod(script)
            getattr(self, script).manage_edit(text, '')
            
    def _add_file(self):
        for file in _files:
            if hasattr(self.aq_inner, file):
                continue
            f = open(pjoin(_phome, _folder, file), 'rb')
            text = f.read()
            f.close()
            self.manage_addFile(id=file, file=text, content_type='application/x-javascript')
            
    def _add_python(self):
        for script in _python:
            if hasattr(self.aq_inner, script):
                continue
            f = open(pjoin(_phome, _folder, script), 'rb')
            text = f.read()
            f.close()
            self.manage_addProduct['PythonScripts'].manage_addPythonScript(script)
            pscript = getattr(self, script)
            pscript.write(text)
            
    security.declareProtected(SilvaPermissions.ViewManagementScreens, 'manage_editPhotoGallery')
    def manage_editPhotoGallery(self, title, data_encoding, description=None, cacheable=None, previewable=None, usable=None):
        '''
        Saves the edited values
        
        @param title:
        @param data_encoding:
        @param description:
        @param cacheable:
        @param previewable:
        @param usable:
        @return: html of the changed form and feedback messages.
        '''
        #beautificaton of return value
        retval = self.manage_editCodeSource(title, 'gallery_helper_scripts.js', data_encoding, description=description, 
                                            cacheable=cacheable, previewable=previewable, usable=usable)
        return retval.replace("<b>Warning</b>: no script id specified!", "")
            
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'to_html')
    def to_html(self, content, request, **parameters):
        """render the photo gallery"""
        photos = self._getPhotos(content.get_content())
        if not photos:
            return u'<p>no photos found!</p>'
        
        renderer = Renderer(parameters.get('language', dft_language))
        result = renderer.render(self, photos, **parameters)
        if type(result) is unicode:
            return result
        return unicode(result, self.get_data_encoding(), 'replace')
        
    def _getPhotos(self, model=None):
        """Returns a sorted list of photos found in the container.
        """
        try:
            if not model:
                model = self.REQUEST.model
            photos = model.get_container().objectValues('Silva Image')
        except:
            return []
        photos.sort(lambda x,y : cmp(x.getId(),y.getId()))
        return photos
    
    security.declarePublic('pg_values_i18n')
    def pg_values_i18n(self, form, field_name):
        from Products.SilvaPhotoGallery import _form_translation
        return _form_translation.values_i18n(form, field_name)

InitializeClass(PhotoGallery)


manage_addPhotoGalleryForm = PageTemplateFile(
    "www/photoGalleryAdd", globals(), __name__='manage_addPhotoGalleryForm')

def manage_addPhotoGallery(context, id, title, REQUEST=None):
    """Add an Inline Viewer"""
    v = PhotoGallery(id)
    v.title = unicode(title, 'UTF-8')
    context._setObject(id, v)
    add_and_edit(context, id, REQUEST)
    return ''
