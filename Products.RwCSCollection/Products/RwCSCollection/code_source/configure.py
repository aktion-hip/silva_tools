# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

code_sources = {
    'mail_scrambler': {
        'title':'Mail Scrambler',
        'description':'Scrambles mail',
        'previewable':False,        
        'cacheable':True,
        'usable':True,
    },
    'clear_float': {
        'title':'Clear floating images',
        'description':'New start for floating images on right side',
        'previewable':False,
        'cacheable':True,
        'usable':True,
    },
    'html_anchor': {
        'title':'Anchor',
        'description':'Anchor for jumps inside a page',
        'previewable':False,
        'cacheable':True,
        'usable':True,
    },
}
code_sources_derived = {
    'show_sitemap': {
        'title':'Sitemap',
        'constructor':'manage_addSiteMap',
        'install':True,
    },
    'list_assets': {
        'title':'List of Assets', 
        'constructor':'manage_addAssetList',
        'install':True,
        },
    'contact_form': {
        'title':'Contact Form', 
        'constructor':'manage_addContactForm',
        'install':False,
    },
}    
