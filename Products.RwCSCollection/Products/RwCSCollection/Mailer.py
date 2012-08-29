# -*- coding: utf8 -*-
# Copyright (c) 2011 Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Header import Header

#Zope
import zLOG
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Globals import InitializeClass

charset='iso-8859-1'
from Products.RwCSCollection.configuration import mailhost_id

ModuleSecurityInfo('Products.RwCSCollection.Mailer').declarePublic('send_mail')

errorMsg = 'Systemfehler: Mail konnte nicht abgeschickt werden / System error: Mail could not be sent'
_tmpl_mail = u"""<div style="font-family:verdana,arial,helvetica,sans-serif; font-size:10pt;">
%s
</div>"""

class Mailer(object):
    '''
    Class for sending html mails.
    '''
    
    security = ClassSecurityInfo()
        
    def __init__(self, mailhost):
        '''
        @param mailhost: the mailhost object to use for sending the mails.
        '''
        self._mailhost = mailhost
    
    security.declarePublic('send')    
    def send(self, mail_to, mail_from, subject, text, text_plain='', encoding=charset, mail_cc='', mail_bcc=''):
        '''
        Creates and sends a mail with the specified information.
        
        @param mail_to: the receivers address
        @param mail_from: the senders address
        @param subject: the mail subject
        @param text: the mail body as hmtl.
        @param text_plain: the mail body as plain text (optional) [optional].
        @param encoding: the encoding for the html part (optional, default 'iso-8859-1').
        @param mail_cc: the cc address(es) [optional].
        @param mail_bcc: the bcc address(es) [optional].
        @return: empty string or error message.
        '''
        mime_msg = MIMEMultipart('related')
        header = Header(subject, charset)
        mime_msg['Subject'] = header
        mime_msg['From'] = mail_from
        mime_msg['To'] = mail_to
        if mail_cc:
            mime_msg['Cc'] = mail_cc
        if mail_bcc:
            mime_msg['Bcc'] = mail_bcc
        mime_msg.preamble = 'This is a multi-part message in MIME format.'
        
        alternative = MIMEMultipart('alternative')
        mime_msg.attach(alternative)
        
        if text_plain:
            msg_txt = MIMEText(text_plain, _charset=charset)
            alternative.attach(msg_txt)
        
        msg_txt = MIMEText((_tmpl_mail %text).encode(encoding, 'replace'), _subtype='html', _charset=encoding)
        alternative.attach(msg_txt)
        
        try:
            self._mailhost.send(mime_msg.as_string())
        except Exception, e:
            zLOG.LOG('RwCSCollection:', zLOG.ERROR, 'Mailer error', e)
            return errorMsg
        return ''
    
InitializeClass(Mailer)

def send_mail(context, mail_to, mail_from, subject, text, encoding='utf-8'):
    ''' Convenience method to send mails using the installed mailhost.
        Parameters: context
                    mail_to
                    mail_from
                    subject
                    text
        Returns an empty string if the mail has been processed without errors, 
        else an error message is returned.
    '''
    mailhost = getattr(context.get_root(), mailhost_id)
    mailer = Mailer(mailhost)
    return mailer.send(mail_to, mail_from, subject, text)
