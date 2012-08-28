# I18N stuff
from Products.Silva.i18n import translate as _

model = context.REQUEST.model

error = model.execute()
if error:
    m = error
    msg_type = 'error'
    return context.tab_edit(message_type=msg_type, message=m)

m = _('Successfully created the static html pages.')
msg_type = 'feedback'
return context.tab_feedback(message_type=msg_type, message=m)
