# -*- coding: utf-8 -*-
# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

import unittest
from DateTime import DateTime
from lxml import etree

from Products.RwLayout.tests import RwTestCase
from Products.RwCSCollection.code_source.SitemapCode import SitemapRenderingAdapter
from Products.RwCSCollection.code_source.sitemap import InfrastructureFilter
from io import StringIO

class SitemapTestCase(RwTestCase.RwTestCase):
    
    def afterSetUp(self):
        kw = {'policy_name':'Silva Document'}
        self.localSite = localSite = self.add_publication(self.root, 'localSite', 'Local Site', **kw)
        self.doc01 = doc01 = self.add_document(self.localSite, 'doc01', 'Document 1 in root')
        self.sub1 = sub1 = self.add_folder(self.localSite, 'sub1', 'Sub 1', **kw)
        self.doc11 = doc11 = self.add_document(self.sub1, 'doc11', 'Document 1 in Folder 1')
        self.doc12 = doc12 = self.add_document(self.sub1, 'doc12', 'Document 2 in Folder 1')
        self.sub2 = sub2 = self.add_folder(self.localSite, 'sub2', 'Sub 2', **kw)
        self.doc21 = doc21 = self.add_document(self.sub2, 'doc21', 'Document 1 in Folder 2')
        self.doc22 = doc22 = self.add_document(self.sub2, 'doc22', 'Document 2 in Folder 2')
        self.sub21 = sub21 = self.add_folder(self.sub2, 'sub21', 'SubSub 1 in Sub 2', **kw)
        self.doc21_1 = doc21_1 = self.add_document(self.sub21, 'doc21_1', 'Document 1 in Folder SubSub 1')
        self.doc02 = doc02 = self.add_document(self.localSite, 'doc02', 'Document 2 in root')
    
        for doc in [doc01, doc02, doc11, doc12, doc21, doc22, doc21_1, localSite.index, sub1.index, sub2.index, sub21.index]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

    def test_indent(self):
        adapter = SitemapRenderingAdapter(self.localSite, self.app.REQUEST)
        out = adapter.render(True)
        doc = etree.parse(StringIO(out))
        
        self.assertEquals(doc.xpath('/ul/li/h3')[0].text, 'Local Site')
        
        rootDocs = [el.text for el in doc.xpath('/ul/li/a')]
        self.assertEquals(len(rootDocs), 2)
        self.assertEquals(rootDocs[0], 'Document 1 in root')
        self.assertEquals(rootDocs[1], 'Document 2 in root')
        
        rootDocURLs = doc.xpath('/ul/li/a/@href')
        self.assertEquals(len(rootDocURLs), 2)
        self.assertEquals(rootDocURLs[0], 'http://localhost/root/localSite/doc01')
        self.assertEquals(rootDocURLs[1], 'http://localhost/root/localSite/doc02')
        
        chapters = [el.text for el in doc.xpath('/ul/li/h4/a')]
        self.assertEquals(len(chapters), 2)
        self.assertEquals(chapters[0], 'Sub 1')
        self.assertEquals(chapters[1], 'Sub 2')
        
        subDocs = [el.text for el in doc.xpath('/ul/li/ul/li/a')]
        self.assertEquals(len(subDocs), 5)
        self.assertEquals(subDocs[0], 'Document 1 in Folder 1')
        self.assertEquals(subDocs[1], 'Document 2 in Folder 1')
        self.assertEquals(subDocs[2], 'Document 1 in Folder 2')
        self.assertEquals(subDocs[3], 'Document 2 in Folder 2')
        self.assertEquals(subDocs[4], 'SubSub 1 in Sub 2')

        subsubDocs = [el.text for el in doc.xpath('/ul/li/ul/li/ul/li/a')]
        self.assertEquals(len(subsubDocs), 1)
        self.assertEquals(subsubDocs[0], 'Document 1 in Folder SubSub 1')


    def test_noIndent(self):
        adapter = SitemapRenderingAdapter(self.localSite, self.app.REQUEST)
        out = adapter.render(False)
        doc = etree.parse(StringIO(out))

        self.assertEquals(doc.xpath('/ul/li/h3')[0].text, 'Local Site')

        rootDocs = [el.text for el in doc.xpath('/ul/li/a')]
        self.assertEquals(len(rootDocs), 8)
        self.assertEquals(rootDocs[0], 'Document 1 in root')
        self.assertEquals(rootDocs[1], 'Document 1 in Folder 1')
        self.assertEquals(rootDocs[2], 'Document 2 in Folder 1')
        self.assertEquals(rootDocs[3], 'Document 1 in Folder 2')
        self.assertEquals(rootDocs[4], 'Document 2 in Folder 2')
        self.assertEquals(rootDocs[5], 'SubSub 1 in Sub 2')
        self.assertEquals(rootDocs[6], 'Document 1 in Folder SubSub 1')
        self.assertEquals(rootDocs[7], 'Document 2 in root')

        rootDocURLs = doc.xpath('/ul/li/a/@href')
        self.assertEquals(len(rootDocURLs), 8)
        self.assertEquals(rootDocURLs[0], 'http://localhost/root/localSite/doc01')
        self.assertEquals(rootDocURLs[1], 'http://localhost/root/localSite/sub1/doc11')
        self.assertEquals(rootDocURLs[2], 'http://localhost/root/localSite/sub1/doc12')
        self.assertEquals(rootDocURLs[3], 'http://localhost/root/localSite/sub2/doc21')
        self.assertEquals(rootDocURLs[4], 'http://localhost/root/localSite/sub2/doc22')
        self.assertEquals(rootDocURLs[5], 'http://localhost/root/localSite/sub2/sub21')
        self.assertEquals(rootDocURLs[6], 'http://localhost/root/localSite/sub2/sub21/doc21_1')
        self.assertEquals(rootDocURLs[7], 'http://localhost/root/localSite/doc02')
        
        chapters = [el.text for el in doc.xpath('/ul/li/h4/a')]
        self.assertEquals(len(chapters), 2)
        self.assertEquals(chapters[0], 'Sub 1')
        self.assertEquals(chapters[1], 'Sub 2')
        
class InfrastructerFilterTestCase(RwTestCase.RwTestCase):
    
    def afterSetUp(self):
        kw = {'policy_name':'Silva Document'}
        self.localSite = localSite = self.add_publication(self.root, 'localSite', 'Local Site', **kw)
        self.doc01 = doc01 = self.add_document(self.localSite, 'doc01', 'Document 1 in root')
        self.sub = sub = self.add_folder(self.localSite, 'sub', 'Sub', **kw)
        self.doc11 = doc11 = self.add_document(self.sub, 'doc11', 'Document in Folder')
        self.sitemap = sitemap = self.add_folder(self.localSite, 'sitemap', 'Sitemap', **kw)
        self.doc21 = doc21 = self.add_document(self.sitemap, 'doc21', 'Document in Sitemap')

        for doc in [doc01, doc11, doc21, localSite.index, sub.index, sitemap.index]:
            doc.set_unapproved_version_publication_datetime(DateTime() - 1)
            # should now be published
            doc.approve_version()

    def test_filter(self):
        filter = InfrastructureFilter(['sitemap'])
        self.assertFalse(filter.filter(self.doc01))
        self.assertFalse(filter.filter(self.sub))
        self.assertTrue(filter.filter(self.sitemap))
        
    def test_filtered(self):
        adapter = SitemapRenderingAdapter(self.localSite, self.app.REQUEST)
        adapter.set_filters((InfrastructureFilter(['sitemap']),))
        out = adapter.render(False)
        doc = etree.parse(StringIO(out))

        self.assertEquals(doc.xpath('/ul/li/h3')[0].text, 'Local Site')
        chapters = [el.text for el in doc.xpath('/ul/li/h4/a')]
        self.assertEquals(len(chapters), 1)
        self.assertEquals(chapters[0], 'Sub')
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SitemapTestCase))
    suite.addTest(unittest.makeSuite(InfrastructerFilterTestCase))
    return suite
