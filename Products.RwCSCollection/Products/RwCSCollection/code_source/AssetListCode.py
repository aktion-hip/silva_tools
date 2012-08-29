# Copyright (c) 2011 RelationWare, Benno Luthiger. All rights reserved.
# See also LICENSE.txt

class AssetListItem:
    """An asset item for the asset list.
    """
    def __init__(self, asset, category=""):
        self._asset = asset
        self.category = category
        self._has_size = 0
        
    def _getSizeFormatted(self):
        """Helper method: formats the size information.
        """
        file_size = 0
        try:
            file_size = self._asset.get_file_size()
        except:
            return ""
        
        self._has_size = 1
        mega = 1024.0
        size = (file_size / mega)
        if size < mega:
            return "%.0f kB" %size
        return "%.1f MB" %(size/mega)
    
    def sortField(self, get_id_strategy):
        sort = getattr(self._asset, get_id_strategy)()
        return self.category + sort

    def render(self, item_render_template, item_template, show_size=1):
        id = self._asset.get_title_or_id()
        size = self._getSizeFormatted()
        
        rendered = ""
        try:
            rendered = self._asset.render()
        except:
            size_display = ""
            if show_size and self._has_size:
                size_display = " (%s, %s)" %(self._asset.getId().split(".")[-1].upper(), size)
            rendered = item_render_template %(self._asset.absolute_url(), self._asset.meta_type, id, size, id, size_display) 
        return item_template %rendered 

class AssetList:
    """Helper for list of assets.
    """
    def __init__(self, assets, category_type=None):
        self._list = []
        self._anchor = ''
        for asset in assets:
            self.make_list_item(asset, category_type)

    def make_list_item(self, item, category_type=None):
        ''' Creates a list item.
            Subclasses may override this method to create the appropriate list item.
        '''
        self._list.append(AssetListItem(item))
    
    def get_compare(self, item):
        ''' Retrieves the appropriate value to test for the actual categroy.
            The value returned is passed to the method check_anchor().
            Subclasses may override this method to create the appropriate list item.
        '''
        return ""
    
    def check_anchor(self, compare, section_template):
        ''' Creates the anchor, i.e. the category title.
            Parameter: comparater value, result of the method get_compare().
            Subclasses may override this method to create the appropriate list item.
        '''
        if self._anchor <> compare:
            self._anchor = compare
            return section_template %self._anchor
        return ''

    def render(self, item_render_template, item_template, section_template, show_size=1, get_id_strategy=0):
        ''' Renders the whole list.
        '''
        self._list.sort(lambda x,y: cmp(x.sortField(get_id_strategy), y.sortField(get_id_strategy)))
        self._anchor = ''
        
        out = []
        for item in self._list:
            out.append(self.check_anchor(self.get_compare(item), section_template))
            out.append(item.render(item_render_template, item_template, show_size))
        return "\n".join(out)

class SortedListHelper:
    """Mixin class for sorted lists.
    """
    def eval_categories(self, item):
        ''' Evaluates the categories from the metadata set of this item.
            Parameter: item: Silva content object.
        '''
        try:
            cat_types = get_binding(item).get(ETHHelpers.id_meta_content, 'category_ass').split(";")
        except:
            cat_types = ''
        cat_dir = {}
        for type in cat_types:
            key_value = type.split("=")
            if len(key_value) > 1:
                cat_dir[key_value[0].strip()] = key_value[1].strip()
        return cat_dir
    