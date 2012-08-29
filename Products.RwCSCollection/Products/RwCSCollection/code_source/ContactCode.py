# -*- coding: utf8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

import locale
import random
import re

from Products.PythonScripts.standard import html_quote

_FORM_HEADER_PATTERN = re.compile(r'action=[\"\'](.*?)[\"\']')
TRAP_NAME = "bot_trap"
SUBMISSION_FIELD = "formulator_submission"
numerical = ['IntegerField', 'RangedIntegerField', 'FloatField']

form_tmpl = u"""%s
%s
<div class="tablemargin contactform">
  <table class="silvatable listing" cellpadding="0" cellspacing="0">
  %s
  </table>
  <table class="silvatable" cellpadding="0" cellspacing="0">
%s
    <tr>
      <td>
        <input type="submit" value="%s">
      </td>
    </tr>
  </table>
  <input type="text" name="%s" size="40" maxlength="80" style="display: none" />
</div>
%s
"""
form_madatory_tmpl = u"""    <tr>
      <td>%s</td>
    </tr>
    <tr>
      <td style="height:7px"></td>
    </tr>
"""

group_tmpl = u"""%s
<tr>
  <td>
    <table class="silvatable" cellpadding="0" cellspacing="0">
      <colgroup>
        <col valign="top" align="left" width="%i%%" />
        <col valign="top" align="left" width="%i%%" />
        <col valign="top" align="left" width="%i%%" />
      </colgroup>
      %s
    </table>
  </td>
</tr>
"""

group_heading_tmpl = u"""<tr class="rowheading"><td>%s</td></tr>"""

field_tmpl = u"""<tr align="left" valign="top">
  <td class="%s">
    <b>%s</b>%s
  </td>
  <td>%s</td>
  <td><p>%s</p></td>
</tr>
"""

def makeUnicode(value, encoding='utf-8'):
    try:
        return unicode(value, encoding, 'replace')
    except:
        return value

def get_header(form, action_url):
    '''
    Returns the form header.
    @param form: the actual form
    @param action_url: the page's url where the form is displayed
    @return: the form header, e.g. '<form action="http://localhost/form" name="my_form" method="post">'
    '''
    return _FORM_HEADER_PATTERN.sub('action="%s?session=%s"' %(action_url, str(random.random())), form.header())

###
class FormDisplay(object):
    '''
    Helper class for form rendering.
    '''

    def __init__(self, form, url):
        '''
        @param form: the form to display
        @param url: the url to call in the form's action
        '''
        self._col_width = (25, 50, 25)
        self._form = form
        self._url = url

    def set_col_width(self, col1, col2, col3):
        '''
        Sets the width of the table columns that display the form.
        The three numbers provided must sum up to 100 (percent).
        @param col1: integer, width of field title column (percent value)
        @param col2: integer, width of input fields column (percent value)
        @param col3: integer, width of field description column (percent value)
        '''
        self._col_width = (col1, col2, col3)

    def render(self, request, label=' Ok ', remark='', prolog=''):
        '''
        Renders the form for public view.
        @param request: the request object
        @param label: the send button's label
        @param remark: the remark concerning mandatory fields
        @param prolog: a prolog sentence (may be html) to display on top of the form [optional]
        @return: the rendered form
        '''
        colorize = len(self._form.get_fields()) > 4

        formHelper = FormHelper(self._form, request)
        groups = []
        hasRequired = 0
        for group in formHelper.getGroups():
            heading = group.getHeading()
            if heading:
                heading = group_heading_tmpl %heading
            fields = []
            odd = 1
            for field in group.getFields():
                #we don't want hidden fields displayed in our form
                if field.isHidden:
                    fields.append(field.fieldRendered)
                    continue

                color_class = (colorize and odd) and 'grey-back' or 'bright-back'
                required = field.isRequired and """&nbsp;<span class="warning">*</span>""" or ""
                hasRequired = hasRequired or required
                odd = not odd
                fields.append(field_tmpl %(color_class,
                                           field.fieldTitle,
                                           required,
                                           field.fieldRendered,
                                           field.fieldDescription))
            groups.append(group_tmpl %(heading,
                                       self._col_width[0],
                                       self._col_width[1],
                                       self._col_width[2],
                                       "".join(fields)))
        return form_tmpl %(prolog,
                           get_header(self._form, self._url),
                           "".join(groups),
                           hasRequired and (form_madatory_tmpl %makeUnicode(remark)) or "",
                           label,
                           TRAP_NAME,
                           self._form.footer())

class FormHelper(object):
    '''
    Helper class that contains all form information prepared for easy and flexible form rendering.
    '''
    def __init__(self, form, request):
        '''
        @param form: the form to evaluate
        @param request: the REQUEST object containing possible user input
        '''
        self._form = form
        self._groups = []
        for group in self._form.get_groups():
            self._groups.append(FormGroup(group, self._form, request))

    def getGroups(self):
        '''
        @return: the form's group. At least, this is the default group.
        '''
        return self._groups

class FormGroup(object):
    '''
    A group of form fields.
    '''
    def __init__(self, group, form, request):
        self._groupId = group
        self._group_heading = ""
        if group and group != 'Default':
            self._group_heading = makeUnicode(group)

        self._fields = []
        for field in form.get_fields_in_group(self._groupId):
            self._fields.append(FormField(field, request))

    def getFields(self):
        '''
        @return: the fields contained in the group
        '''
        return self._fields

    def getHeading(self):
        '''
        @return: the group's heading, may be empty
        '''
        return self._group_heading

class FormField(object):
    '''
    A form field.

    This class contains the following instance attributes:
    *isHidden: is this field hidden?
    *isRequired: is this field required?
    *fieldId: the field's id
    *fieldTitle: the field's title
    *fieldDescription: the field's description
    *fieldRendered: the rendered form field (html)
    '''
    def __init__(self, field, request):
        self.isHidden = field.get_value('hidden')
        self.isRequired = field.is_required()
        self.fieldId = field.id
        self.fieldTitle = makeUnicode(field.get_value('title'))
        self.fieldDescription = makeUnicode(field.get_value('description'))
        self.fieldRendered =  makeUnicode(field.render_from_request(request))

###
class Validator(object):
    def __init__(self, form, request):
        self.fields = []
        self.values = []
        self.isBotSuspect = 0
        self.mail_body = []
        self.mail_body_html = []
        self.error_msg = self._validate(form, request)
    
    def _validate(self, form, request):
        from Products.Formulator.Errors import ValidationError, FormValidationError
        locale.setlocale(locale.LC_TIME, '')
        
        if request.get(TRAP_NAME, ''):
            self.isBotSuspect = 1
            return ''

        try:
            validated = form.validate_all(request)
            for field in form.get_fields():
                field_id = field.id
                title = makeUnicode(form.get_field(field_id).get_value('title'))
                value = validated.get(field_id, '')
                if value:
                    value = self._trasform_value(field, value)                    
                    self.fields.append(u'`%s`' %field_id)
                    self.values.append(value)
                    self._fieldPostProcess(field, value, title)            
            return ''            
            
        except FormValidationError, errlist:
            msg = []
            for error in errlist.errors:
                msg.append(u'<em>%s</em>: %s<br />' %(makeUnicode(error.field.get_value('title')), error.error_text))
            return '<p style="color:red;">%s</p>' %"\n".join(msg)

    def _trasform_value(self, field, value):
        if field.meta_type == 'DateTimeField':
            format = '%Y-%m-%d %X'
            if value.hour() + value.minute() == 0:
                format = '%Y-%m-%d'
            return makeUnicode(value.strftime(format))
        elif field.meta_type in numerical:
            return value
        elif field.meta_type == "CheckBoxField":
            return value
        elif field.meta_type == "MultiCheckBoxField":
            return u', '.join([html_quote(makeUnicode(item)) for item in value])
        else:
            if type(value) == type([]):
                return u', '.join([html_quote(makeUnicode(item)) for item in value])
            else:
                return html_quote(makeUnicode(value))                
        return value
    
    def _fieldPostProcess(self, field, value, title):
        #mail body: we don't want to include hidden fields here
        if not field.get_value('hidden'):        
            if field.meta_type == "CheckBoxField":
                self.mail_body.append(u'%s\n' %title)
                self.mail_body_html.append(u'<i>%s</i><br />' %title)
            else:
                self.mail_body.append(u'%s: %s\n' %(title, value))
                self.mail_body_html.append(u'<i>%s</i>: %s<br />' %(title, htmlUnquote(value, structure=1)))            
    
def htmlUnquote(text, structure=0):
    '''
    Returns the text with html markups unquoted (i.e. escaped characters transformed back) if requested

    @param text: the text to process
    @param structure: if true, escaped html markups are transformed back.
    @return: the processed string
    '''
    if not structure: return text
    try:
        return text.replace('&gt;', '>').replace('&lt;', '<')
    except:
        return text
    