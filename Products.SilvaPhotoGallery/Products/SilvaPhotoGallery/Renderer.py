# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare. All rights reserved.
# See also LICENSE.txt
# $Revision: $

_help_info_s1_EN = u"""<strong>Help</strong><br />
Click on a photo to see large version or select a delay and click on &quot;Slideshow&quot; to start the slideshow. Click on the right (of left) half of the image to change to the next (previous) image. To close the image or stop the slideshow, click on the cross.<br />
Alternatively, you can use the following keys:<br />
<table>
  <tr><td>x&#160;</td><td>stop slideshow or close image</td></tr>
  <tr><td>c&#160;</td><td>stop slideshow or close image</td></tr>"""
_help_info_s2_EN = u"""<strong>Help</strong><br />
Click on a photo to see large version. Click on the right (of left) half of the image to change to the next (previous) image. To close the image click on the cross.<br />
Alternatively, you can use the following keys:<br />
<table>
  <tr><td>x&#160;</td><td>stop slideshow or close image</td></tr>
  <tr><td>c&#160;</td><td>stop slideshow or close image</td></tr>"""
_help_info_s3_EN = u"""Note: The manual change of pictures is disabled during slide show."""
_help_info_e_EN = u"""
  <tr><td>n&#160;</td><td>show next image</td></tr>
  <tr><td>p&#160;</td><td>show previous image</td></tr>
</table>"""
_help_info_s1_DE = u"""<strong>Hilfe</strong><br />
Klicken Sie auf ein Foto, um es in voller Grösse anzusehen oder wählen Sie ein Zeitintervall und klicken Sie auf &quot;Diaschau&quot;, um die Diaschau zu starten. Klicken Sie auf die rechte (oder linke) Bildhälfte, um auf das nächste (vorherige) Bild zu wechseln. Klicken Sie auf das Kreuz, um das Foto zu schliessen oder die Diaschau zu beenden.<br />
Alternativ können Sie die folgenden Tasten benutzen:<br />
<table>
  <tr><td>x&#160;</td><td>Diaschau beenden oder Foto schliessen</td></tr>
  <tr><td>c&#160;</td><td>Diaschau beenden oder Foto schliessen</td></tr>"""
_help_info_s2_DE = u"""<strong>Hilfe</strong><br />
Klicken Sie auf ein Foto, um es in voller Grösse. Klicken Sie auf die rechte (oder linke) Bildhälfte, um auf das nächste (vorherige) Bild zu wechseln. Klicken Sie auf das Kreuz, um das Foto zu schliessen.<br />
Alternativ können Sie die folgenden Tasten benutzen:<br />
<table>
  <tr><td>x&#160;</td><td>Foto schliessen</td></tr>
  <tr><td>c&#160;</td><td>Foto schliessen</td></tr>"""
_help_info_s3_DE = u"""Hinweis: Der manuelle Bildwechsel ist während der Diaschau abgeschaltet."""
_help_info_e_DE = u"""
  <tr><td>n&#160;</td><td>nächstes Foto zeigen</td></tr>
  <tr><td>p&#160;</td><td>vorheriges Foto zeigen</td></tr>
</table>"""

_translations = {
'hint':{'DE':u'Klicken Sie auf ein Foto, um es in voller Grösse anzusehen.', 'EN':u'Click on a photo to see large version.'},
'slideshow':{'DE':u'Diaschau', 'EN':u'Slideshow'},
'show_help':{'DE':u'Hilfe einblenden', 'EN':u'Show help'},
'help':{'DE':u'Hilfe', 'EN':u'Help'},
'help_info_s1':{'DE':_help_info_s1_DE, 'EN':_help_info_s1_EN},
'help_info_s2':{'DE':_help_info_s2_DE, 'EN':_help_info_s2_EN},
'help_info_s3':{'DE':_help_info_s3_DE, 'EN':_help_info_s3_EN},
'help_info_e':{'DE':_help_info_e_DE, 'EN':_help_info_e_EN}
}

_tmpl_thumbnail = u"""<div id="lightbox_thumbnail" class="%s">
  <a href="%s" title="%s" rel="lightbox[gallery]" %s>
    %s
  </a>
  %s
</div>  
"""
_tmpl_caption = u"""  <div id="lightbox_caption">
    <a href="%s" rel="lightbox[gallery]" title="%s">
      %s
    </a>
  </div>
"""
_tmpl_html = u"""<p>%s</p>
  <p>%s</p>
  <div class="tablemargin">
    <table border="0" cellpadding="0" cellspacing="0"><tr><td>
      %s
    </td></tr></table>
  </div>  
  <p>%s</p>
"""

class Renderer(object):
    def __init__(self, language):
        self.language = language
        
    def render(self, context, photos, **kw):
        if not photos:
            return ""
        
        request = context.REQUEST
        show_captions = int(kw.get('caption'))
        slide_show_position = int(kw.get('slide_show_settings'))
        help_info_position = int(kw.get('help_info'))
        portrait = [x for x in photos if x.getOrientation()=='portrait' or x.getOrientation()=='square']
        
        tools_before = self._createTools(context, 1, slide_show_position, help_info_position)
        tools_after = self._createTools(context, 2, slide_show_position, help_info_position)
            
        css_class = 'lightbox_thumbnail '+(portrait and 'portrait' or 'landscape')
        
        out_photos = []
        pos = 0
        for photo in photos:
            caption = ''
            if show_captions:
                title = photo.get_title_or_id()
                caption = _tmpl_caption %(photo.absolute_url(), title, self._getCaption(title))
            
            title = show_captions and photo.get_title_or_id() or ''
            id = not pos and 'id="slideshowStartLink"' or '' 
            out_photos.append(_tmpl_thumbnail %(css_class, 
                                      photo.absolute_url(), 
                                      title, 
                                      id, 
                                      photo.tag(hires=0, thumbnail=1),
                                      caption))
            pos += 1
        
        html = _tmpl_html %(self._getHint(),
                            "\n".join(tools_before),
                            "\n".join(out_photos),
                            "\n".join(tools_after))
        return self._getScripts(context, request.URL1, show_captions) + html
    
    def _createTools(self, context, position, slide_show_position, help_info_position):
        tools = []
        if slide_show_position == position:
            tools.append(self._getSlideShow())
        if help_info_position == position:
            tools.append(self._getHelpButton(context))
            tools.append(self._getHelpInfo(slide_show_position))
        return tools

    def _getScripts(self, context, url, caption):
        html_style_templ = """<link rel="stylesheet" type="text/css" media="all" href="%s" />"""
        html_script_templ = """<script type="text/javascript" src="%s"></script>"""

        out = []
        out.append(html_style_templ %getattr(context, 'lightbox.css').absolute_url())
        out.append(html_style_templ %getattr(context, 'photo_gallery.css').absolute_url())
        out.append(html_script_templ %getattr(context, 'prototype.js').absolute_url())
        out.append(html_script_templ %(getattr(context, 'scriptaculous.js').absolute_url() + '?load=effects'))
        out.append("""<script type="text/javascript" src="%s?url=%s&amp;show_caption=%i"></script>""" %(getattr(context,'lightbox.js').absolute_url(), url, caption)) 
        out.append(html_script_templ %getattr(context, 'gallery_helper_scripts.js').absolute_url())
        return "\n".join(out)
    
    def _getHint(self):
        return _translations['hint'][self.language]
    
    def _getSlideShow(self):
        html = u"""<select id="timeSelect">
    <option value="2000">2sec</option>
    <option value="5000" selected="selected">5sec</option>
    <option value="10000">10sec</option>
    <option value="30000">30sec</option>
  </select>
  <input type="button" onclick="myLightbox.start(document.getElementById('slideshowStartLink')); slide=true; return false;" value="%s" />&#160;&#160;
  """
        return html %(_translations['slideshow'][self.language])
    
    def _getHelpButton(self, context):
        img_url = getattr(context, 'plus.gif').absolute_url()
        html = u"""<a class="nounderline" href="javascript:toggleElement('help')" title="%s"><img id="imghelp" src="%s" alt="plus" /></a> <a href="javascript:toggleElement('help')" title="%s"><span>%s</span></a><br />"""
        show_help = _translations['show_help'][self.language]
        return html %(show_help, img_url, show_help, _translations['help'][self.language])
    
    def _getHelpInfo(self, slide_show=0):
        language = self.language
        html = u"""<div id="txthelp" style="display:none" class="expandable tablemargin">%s</div>"""
        help = _translations['help_info_s2'][language]
        if slide_show:
            help = _translations['help_info_s1'][language]
        help += _translations['help_info_e'][language]
        if slide_show:
            help += _translations['help_info_s3'][language]
        return html %help
        
    def _getCaption(self, caption):
        lenCaption = 42
        if len(caption) < lenCaption:
            return caption
        return caption[:lenCaption-3] + '...'        
    