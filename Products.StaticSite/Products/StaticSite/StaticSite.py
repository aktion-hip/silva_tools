# -*- coding: utf-8 -*-
# Copyright (c) 2013 RelationWare. All rights reserved.
# See also LICENSE.txt
# $Revision: 4760 $

import os
from urllib import urlretrieve
from urllib2 import urlopen, HTTPError
from shutil import move
import re
import logging

logger = logging.getLogger('static.site')

from five import grok
from zope.interface import Interface
from zope.schema import TextLine
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

from OFS import SimpleItem

# Zope
from AccessControl import ClassSecurityInfo
from App.Common import package_home
from App.class_init import InitializeClass

# Silva
from Products.Silva.Publishable import NonPublishable
from Products.Silva import SilvaPermissions

from silva.core.conf import schema as silvaschema
from silva.core import conf as silvaconf
from silva.translations import translate as _
from zeam.form import silva as silvaforms

from Products.StaticSite.interfaces import IStaticSite


CONTAINERS = ['Silva Folder','Silva Publication']
CONTENT = ['Silva Document']
ASSETS = ['Silva File']
IMAGES = ['Silva Image']
extensions = ['pdf', 'doc', 'gif', 'png', 'jpg', 'jar', 'zip']

_file_encoding = 'utf8'
_content_type = '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
_base_pattern = re.compile('<base href=".*?"\s?/>', re.DOTALL | re.MULTILINE | re.IGNORECASE)
_href_pattern = re.compile('<a\s+?href=[\"\']((http|https)://localhost:.+?)[\"\'].*?>', re.DOTALL | re.MULTILINE | re.IGNORECASE)
_resource_pattern = re.compile('(((http|https)://localhost:.+?/\+\+static\+\+/).+?/.+)[\"\']')
#_resource_pattern = re.compile('(((http|https)://localhost:.+?\+\+resource\+\+.+?)/.+)[\"\']')
_css_resource_pattern = re.compile('url\([\"\']??(.+?)[\"\']??\)', re.DOTALL | re.MULTILINE | re.IGNORECASE)
_hires_pattern = re.compile('(href=".*?)\?hires"', re.DOTALL | re.MULTILINE | re.IGNORECASE)
_resourceFolderName = 'res'


class StaticSite(NonPublishable, SimpleItem.SimpleItem):
    """A helper object to create a static site (i.e. static html pages) 
    of the silva tree starting from the actual directory in the ZODB.
    """
    grok.implements(IStaticSite)
    
    meta_type = "Static Site"
    
    security = ClassSecurityInfo()

    # register priority, icon and factory
    silvaconf.priority(7)
    silvaconf.icon('www/helper.gif')
    
    _directory = ''
    
    def __init__(self, id):
        super(StaticSite, self).__init__(id)
        self._helper = None
        
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_directory')    
    def get_directory(self):
        return self._directory

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_directory')    
    def set_directory(self, directory):
        self._directory = directory

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'execute')        
    def execute(self):
        self._stylesCounter = 0
        self._processed = []
        self._specialReplace = {}
        container = self.get_container()
        resourceUrl = self._exportResources(container)
        self._helper = ExportHelper(container, self._initContainerNames(container, []), resourceUrl, self._specialReplace)
        return self._recurse_in(container, self._directory)
    
    def _exportResources(self, top):
        '''
        @param top: the starting container
        @return: the resource url, e.g. 'http://localhost:8088/silva/++static++/'
        '''
        logger.info('Exporting resources from %s.' %top.absolute_url())
        html = self._readUrl(top.absolute_url())
        if not html:
            return ''
        targetPath = '%s/%s' %(self._directory, _resourceFolderName)
        if not os.path.exists(targetPath):
            os.makedirs(targetPath)
        base = ''
        for match in _resource_pattern.finditer(html):
            url = match.group(1)
            base = match.group(2)
            self._downloadResource(url, base)
        return base
        
    def _downloadResource(self, url, base):
        logger.info('Downloading resource %s.' %url)
        fileName = url.split("/")[-1]
        extension = url.split(".")[-1]
        extended = url[len(base):]
        dirs = extended.split("/")[:-1]
        specialReplace = ":" in extended
        if specialReplace:
            dirs = [part for part in dirs if not ":" in part]
        path = "/".join([self._directory, _resourceFolderName] + dirs)
        if not os.path.isdir(path):
            os.mkdir(path)
        if extension in ('css',):
            fileName = self._cleanCssName(fileName)
            if specialReplace:
                dirs.append(fileName)
                self._specialReplace[extended] = "/".join(dirs)
            self._processCss(url, '%s/%s' %(path, fileName), base)
        else:
            if specialReplace:
                dirs.append(fileName)
                self._specialReplace[extended] = "/".join(dirs)
            self._download(url, '%s/%s' %(path, fileName))
            
    def _cleanCssName(self, fileName):
        if ":" in fileName:
            out = self._stylesCounter and ('styles%i.css' %self._stylesCounter) or 'styles.css'
            self._stylesCounter += 1
            return out
        return fileName
            
    def _processCss(self, url, path, base):
        #downloading css and images referenced therein
        css = self._readUrl(url, readEncoding=0)
        if not css:
            return
        try:
            f = open(path, 'wb')
            f.write(css)
            f.close()
        except IOError, e:
            logger.error(e)

        baseUrl = "/".join(url.split("/")[:-1])
        hrefs = []
        for match in _css_resource_pattern.finditer(css):
            href = match.group(1)
            if (not href.startswith("http")) and (not href in hrefs):
                hrefs.append(href)
                url = '%s/%s' %(baseUrl, href)
                self._downloadResource(url, base)        
    
    def _initContainerNames(self, this_container, path, containerNames = []):
        path.append(this_container.getId())
        containerNames.append("/".join(path))
        for container in this_container.objectValues(CONTAINERS):
            self._initContainerNames(container, list(path), containerNames)
        return containerNames
    
    def _recurse_in(self, this_container, fs_path, level=0):
        error = self._processContainer(this_container, fs_path, level)
        if error:
            return error
        
        #recurse one further level
        level += 1
        for container in this_container.objectValues(CONTAINERS):
            subdir = '%s/%s' %(fs_path, container.getId())
            if not os.path.isdir(subdir):
                os.mkdir(subdir)
            error = self._recurse_in(container, subdir, level)
            if error:
                return error
        return ''
    
    def _processContainer(self, this_container, fs_path, level):
        for content in this_container.objectValues(CONTENT):
            error = self._processContent(content, fs_path, level)
            if error:
                return error
            self._processed.append(content.absolute_url())
        for asset in this_container.objectValues(ASSETS):
            self._processAsset(asset, fs_path)
        for image in this_container.objectValues(IMAGES):
            self._processImage(image, fs_path)
        logger.info('Downloaded folder /%s.' %this_container.getId())
        return ''
            
    def _processContent(self, resource, fs_path, level):
        html = self._readUrl(resource.absolute_url())
        if not html:
            return ''
        
        self._helper.setLevel(level)
        html = self._helper.process(html, resource.absolute_url().endswith('forum_admin/members'))

        path = '%s/%s.html' %(fs_path, resource.getId())
        try:
            f = open(path, 'w')
            f.write(html.encode(_file_encoding, 'replace'))
            f.close()
        except IOError, e:
            logger.error(e)
            return u"Error encountered while writing file '%s'!" %path
        return ''
    
    def _processAsset(self, asset, fs_path):
        self._download(asset.absolute_url(), '%s/%s' %(fs_path, asset.getId()))
        
    def _processImage(self, image, fs_path):
        imgName = image.getId()
        if not "." in imgName:
            imgName = "%s.%s" %(imgName, image.get_web_format().lower())
        self._download(image.absolute_url(), '%s/%s' %(fs_path, imgName))
        if image.get_web_scale() != "100%":
            imgName = "%s@hires" %imgName
            url = "%s?hires" %image.absolute_url()
            self._download(url, '%s/%s' %(fs_path, imgName))

    def _readUrl(self, url, readEncoding=1):
        try:
            response = urlopen(url)
            out = ''
            if readEncoding:
                encoding = response.headers['content-type'].split('charset=')[-1]
                out = unicode(response.read(), encoding)
            else:
                out = response.read()
            response.close()
            return out
        except HTTPError:
            return ''
        
    def _download(self, url, destination):
        local_temp, headers = urlretrieve(url)
        move(local_temp, destination)
    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_processed')        
    def get_processed(self):
        return self._processed

InitializeClass(StaticSite)

class ExportHelper(object):
    _ctIndicator = '"content-type"'
    
    def __init__(self, start_container, containerNames, resourceUrl, specialReplace):
        self._replaceOld = start_container.absolute_url()
        self._level = 0
        self._containerBase = start_container.aq_parent.absolute_url()
        self._containerNames = containerNames
        self._resourceOld = resourceUrl
        self._specialReplace = specialReplace
        
    def setLevel(self, level):
        self._level = level
        
    def process(self, html, doLogging):
        #delete <base href="." />
        html = _base_pattern.sub('', html)
        #add '.html' to some href
        html = self._adjustUrls(html, doLogging)
        #make localhost urls relative
        relPath = self._relPath()
        html = html.replace(self._replaceOld, relPath)
        #fix paths containing illegal characters like ':'
        for oldPath, newPath in self._specialReplace.iteritems():
            html = html.replace(oldPath, newPath)
        #adjust references to web resources (e.g. css)
        html = html.replace(self._resourceOld, '%s/%s/' %(relPath, _resourceFolderName))
        #adjust href to hires images
        #html = html.replace('?hires"', '@hires"')
        html = _hires_pattern.sub(r'\g<1>@hires"', html)
        #add <meta http-equiv="content-type" content="text/html; charset=UTF-8"> to head
        if not ExportHelper._ctIndicator in html:
            html = html.replace('<head>', '<head>'+_content_type)
        return html
    
    def _adjustUrls(self, html, doLogging):
        urls = {}
        for match in _href_pattern.finditer(html):
            url = match.group(1)
            if doLogging: logger.info('>>> url: ' + url)
            indicator = url[len(self._containerBase)+1:]
            if indicator and (not indicator in self._containerNames) and (not url.endswith('#')) and (not '?' in url):
                extension = url.split(".")[-1].lower()
                if not extension in extensions:
                    urls[url] = '%s.html' %url
        for old, new in urls.iteritems():
            if doLogging: logger.info('>>> html.replace(%s, %s)'%(old, new))
            html = html.replace(old, new)
        return html
        
    def _relPath(self):
        return self._level and '/'.join(['..' for el in range(self._level)]) or '.'
