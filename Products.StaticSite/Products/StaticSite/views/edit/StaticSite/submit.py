from Products.Formulator.Errors import FormValidationError

# I18N stuff
from Products.Silva.i18n import translate as _

###

model = context.REQUEST.model

try:
    result = context.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error", message=context.render_form_errors(e))

if result.has_key('directory'):
    directory = result['directory'].strip()
    model.set_directory(directory)

m = _('Directory changed.')

msg_type = 'feedback'

return context.tab_edit(message_type=msg_type, message=m)
