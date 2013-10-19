# -*- coding: utf-8 -*-
# Copyright (c) 2013 RelationWare. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.i18nmessageid import MessageFactory
from zope import interface, schema

from Products.StaticSite.interfaces import IStaticSite, IExecuteAction

from silva.core.conf.interfaces import ITitledContent
from zeam.form.base import SUCCESS, FAILURE
from zeam.form.base.widgets import ActionWidget
from zeam.form.base.actions import Action, Actions
from zeam.form.silva.interfaces import ISMIForm
from zeam.form.base.interfaces import IAction
from zeam.form.silva.actions import CancelEditAction, EditAction
from zeam.form import silva as silvaforms

_ = MessageFactory('staticsite')


class IStaticSiteFields(interface.Interface):
    """The form to trigger an export of the site. 
    """
    directory = schema.TextLine(
                                title=_(u"Directory"),
                                description=_(u"Directory to export the static html pages."), 
                                required=True)

    
#class StaticExecuteWidget(ActionWidget):
#    """Widget to style the execute button
#    """    
#    grok.adapts(IExecuteAction, ISMIForm, interface.Interface)
    
class ExecuteAction(Action):
    grok.implements(IAction)
    #grok.implements(IExecuteAction)
    title = _(u"Execute")
    description = _(u"Start the static export.")
    
    def __call__(self, form):
        error = form.context.execute()
        if error:
            form.send_message(error, type="error")
            return FAILURE
        form.send_message(_(u"Successfully created the static html pages."), type="feedback")
        return SUCCESS
    

class StaticSiteAddForm(silvaforms.SMIAddForm):
    """Add Form for Static Site
    """
    grok.context(IStaticSite)
    grok.name(u"Static Site")

    fields = silvaforms.Fields(ITitledContent, IStaticSiteFields)
    
class StaticSiteEditForm(silvaforms.SMIEditForm):
    """Edit Form for Static Site, containing the execute button for the ExecuteAction
    """
    grok.context(IStaticSite)
    fields = silvaforms.Fields(IStaticSiteFields)
    actions = Actions(ExecuteAction(),
                      CancelEditAction(),
                      EditAction())
    
