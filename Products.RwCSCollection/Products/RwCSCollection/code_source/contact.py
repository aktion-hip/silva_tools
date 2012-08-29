# -*- coding: utf8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

import os

#Zope
from Globals import InitializeClass, package_home
from zope.interface import implements
from AccessControl import ClassSecurityInfo

#Silva
from silva.core import conf as silvaconf

from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaExternalSources.CodeSource import CodeSource
from Products.Silva.SilvaPermissions import ViewManagementScreens, ChangeSilvaAccess, AccessContentsInformation
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Formulator
from Products.Formulator.Errors import ValidationError, FormValidationError
from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm

from Products.RwCSCollection.Mailer import send_mail 
from Products.RwCSCollection.configuration import contact_success, contact_failure, contact_tmpl
from Products.RwCSCollection.code_source.CodeSourceHelper import AbstractCSEditForm, AbstractCSAddForm, manage_addCSBase
from Products.RwCSCollection.code_source.ContactCode import FormDisplay, Validator, SUBMISSION_FIELD

pjoin = os.path.join
_phome = package_home(globals())
_folder = 'www'
_contact_form = 'contact_formDefault'


class ContactForm(CodeSource):
    __doc__ = '''Codes source for the contact form.'''

    implements(IExternalSource)
    meta_type = 'CS Contact Form'
    silvaconf.factory('manage_addContactFormForm')
    silvaconf.factory('manage_addContactForm')
    silvaconf.icon('code_source/www/codesource.png')
    
    security = ClassSecurityInfo()
    
    security.declareProtected(ViewManagementScreens, 'editCodeSource')
    editCodeSource = PageTemplateFile(
        _folder + '/contact_formEdit', globals(),  __name__='editCodeSource')
    
    def __init__(self, id):
        CodeSource.inheritedAttribute('__init__')(self, id)
        self._script_id = ''
        self._data_encoding = 'UTF-8'
        self._description = self.__doc__
        self.public_form = None

    def manage_afterAdd(self, item, container):
        self._set_form()
        self._set_public_form()

    security.declareProtected(ChangeSilvaAccess, 'refresh')
    def refresh(self):
        """reload the form and pt"""
        self._set_form()
        self._set_public_form()
        return 'refreshed form and script'
    
    def _set_form(self):
        self.parameters = ZMIForm('form', 'Properties Form')
        f = open(pjoin(_phome, _folder, 'contact_parameters.form'))
        XMLToForm(f.read(), self.parameters)
        f.close()
        
    def _set_public_form(self):
        if self.public_form: return
        
        self._setObject('public_form', ZMIForm(_contact_form, 'Contact form'))
        form = getattr(self, 'public_form')
        f = open(pjoin(_phome, _folder, _contact_form + ".form"))
        form.set_xml(f.read())
        f.close()

    security.declareProtected(ViewManagementScreens, 'manage_editContactForm')
    def manage_editContactForm(self, title, data_encoding, description=None,
        cacheable=None, elaborate=None, previewable=None):
        """ Edit CodeSource object
        """
        msg = self.manage_editCodeSource(title, '', data_encoding, description, cacheable, elaborate, previewable)
        return msg.replace(u'<b>Warning</b>: no script id specified!<b>Warning</b>: This code source does not contain an object with identifier ""!', '')

    security.declareProtected(AccessContentsInformation, 'to_html')
    def to_html(self, content, request, **parameters):
        """Render HTML for code source
        """
        mail_to = parameters.get('mail_to', None)
        if not mail_to:
            return u'<p>Please provide a mail address!</p>'
        if not hasattr(self, 'public_form'):
            return u'<p>No form found!</p>'
        
        subject = parameters.get('subject')
        label = parameters.get('label')
        remark = parameters.get('remark')
        colWidth = parameters.get('col_width')
        
        model = content.get_content()        
        if request.get(SUBMISSION_FIELD, ''):
            return self._process(model, request, mail_to, subject, colWidth, label, remark)
        return self._display(model, request, colWidth, label, remark)
        
    def _process(self, model, request, mail_to, subject, colWidth, label, remark):
        validator = Validator(self.public_form, request)
        if validator.isBotSuspect: return ''
        if validator.error_msg:
            return self._display(model, request, colWidth, label, remark, validator.error_msg)
        try:
            body = contact_tmpl %"\n".join(validator.mail_body_html)
            result = send_mail(self, mail_to, mail_to, subject, body)
            if result:
                return contact_failure
        except:
            return contact_failure
        return contact_success
    
    def _display(self, model, request, colWidth, label, remark, errors=''):
        display = FormDisplay(self.public_form, model.absolute_url())
        display = self._checkColWidth(display, colWidth)
        return errors + display.render(request, label=label, remark=remark)
    
    def _checkColWidth(self, display, colWidth):
        cols = colWidth.split(',')
        if len(cols) != 3: return display
        try:
            display.set_col_width(int(cols[0]), int(cols[1]), int(cols[2]))
        except:
            pass
        return display

InitializeClass(ContactForm)

###
class AddCSContactForm(AbstractCSAddForm):
    def _getActionName(self):
        return "manage_addContactForm"
    def _getName(self):
        return "manage_addContactFormForm"
    def _getDescription(self):
        return "Add ContactForm, a Silva CodeSource to display a contact form."

manage_addContactFormForm = AddCSContactForm()

def manage_addContactForm(context, id, title, REQUEST=None):
    """Add a ContactForm code source"""
    return manage_addCSBase(ContactForm, context, id, title, REQUEST=REQUEST)
