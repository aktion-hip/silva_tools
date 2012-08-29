# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare. All rights reserved.
# See also LICENSE.txt

#Add the following code to the field in the form xml:
#    <tales>
#      <items>python:here.values_i18n(here, 'mail_from_option')</items>
#    </tales>
#

i18n_domain = 'photo_gallery'

from Products.Silva.i18n import translate as _

values = {
  'form':
    {'caption':[(_('hide', i18n_domain), '0'), (_('show', i18n_domain), '1')],
     'slide_show_settings':[(_('none', i18n_domain), '0'), (_('above', i18n_domain), '1'), (_('underneath', i18n_domain), '2')],
     'help_info':[(_('none', i18n_domain), '0'), (_('above', i18n_domain), '1'), (_('underneath', i18n_domain), '2')]
    }
}


def values_i18n(form, field_name):
    form_id = form.aq_inner.id
    i18n_list = values.get(form_id, {}).get(field_name, [])
    return [(unicode(label), value) for label, value in i18n_list]