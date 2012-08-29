# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

from math import floor
import os

# Silva
from Products.Formulator.Form import ZMIForm

pjoin = os.path.join

def scramble_mail(email, title=None, css=None):
    '''
    Helper method for mail scrambling.
    The template has to be passed in the following form (note the quotation marks):
    'css="my_CSS_class"' (i.e. the string after the equal sign has to be enclosed in double quotes)
    
    @param email: The mail address to scramble.
    @param title: The text to display hyperlinked with the scrambled mailto.
    @param css: A css class template. 
    '''
    if not title:
        title = email
    css_templ = ''
    if css:
        css_templ = css
    out = """document.write('<a %s href="mailto:%s">%s</a>')""" %(css_templ, email, title)
    return """<script type="text/javascript">eval(unescape('""" + hex_string(out) + """'))</script>"""

def hex_string(oldstring):
    '''
    Hexify a string.
    Taken from http://www.happysnax.com.au/testemail.php
    
    @param oldstring:
    '''
    hs='0123456789ABCDEF'
  
    newstring=''
    for i in range(len(oldstring)):
        n = ord(oldstring[i])
        newstring += '%' + hs[int(floor(n/16))] + hs[n%16]
    return newstring

def read_file(filename):
    '''
    Reads the specified file.    
    @param filename:
    '''
    f = open(filename, 'rb')
    text = f.read()
    f.close()
    return text
