# -*- coding: utf-8 -*-
# Copyright (c) 2013 RelationWare. All rights reserved.
# See also LICENSE.txt

from silva.core.interfaces import INonPublishable
from zeam.form.base.interfaces import IAction
    
class IStaticSite(INonPublishable):
    """The form to start the static content export.
    """
    def get_directory():
        '''Returns the configured target dirctory.
        '''
        
    def set_directory(**parameters):
        '''Sets the target directory to export the created static html pages.
        '''
        
    def execute():
        '''Executes the process, i.e. creates the static html pages.
        '''
        
    def get_processed():
        '''Returns the list of processed web pages.
        '''
        
class IExecuteAction(IAction):
    """The action to execute the export.
    """
