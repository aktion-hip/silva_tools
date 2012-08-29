# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

code_sources = {
    'mail_scrambler': {
        'title':'Mail Scrambler',
        'description':'Scrambles mail',
        'previewable':True,        
        'cacheable':True,
        'elaborate':False,
    },
    'clear_float': {
        'title':'Clear floating images',
        'description':'New start for floating images on right side',
        'previewable':False,
        'cacheable':True,
        'elaborate':False,
    },
    'html_anchor': {
        'title':'Anchor',
        'description':'Anchor for jumps inside a page',
        'previewable':False,
        'cacheable':True,
        'elaborate':False,
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
