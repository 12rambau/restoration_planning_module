import json
from traitlets import Any

from sepal_ui import sepalwidgets as sw
import ipyvuetify as v
import pandas as pd

from component import parameter as cp
from .edit_dialog import EditDialog

class LayerTable(v.DataTable, sw.SepalWidget):
    
    # unicode value to notify a change
    change_model = Any().tag(sync=True)
    
    def __init__(self):
        
        self.headers = [
          {'text': 'Theme'     , 'value': 'theme'},
          {'text': 'Sub theme' , 'value': 'subtheme'},
          {'text': 'Layer name', 'value': 'name'},
          {'text': 'Weight'    , 'value': 'weight'},
          {'text': 'Layer'     , 'value': 'layer'},
          {'text': 'Action'    , 'value': 'action'},
        ]
        
        self.items = [
            {
                'theme'   : row.theme,
                'subtheme': row.subtheme,
                'name'    : row.layer_name,
                'weight'  : 0,
                'layer'   : row.gee_asset
            } for i, row in pd.read_csv(cp.layer_list).fillna('').iterrows()
        ]
        
        self.search_field = v.TextField(
            v_model=None,
            label = 'Search',
            clearable = True,
            append_icon = 'mdi-magnify'
        )
        
        self.edit_icon = v.Icon(small=True, children=['mdi-pencil'])
        
        self.dialog_edit = EditDialog()
        
        super().__init__(
            change_model = 0,
            v_model = [],
            show_select = True, 
            single_select = True,
            item_key = 'name',
            headers = self.headers,
            items = self.items,
            search = '',
            v_slots = [
                { # the search slot 
                    'name': 'top',
                    'variable': 'data-table',
                    'children': self.search_field
                },
                { # the pencil for modification
                    'name': 'item.action',
                    'variable': 'item',
                    'children': self.edit_icon
                },
                { # the dialog as a footer
                    'name': 'footer',
                    'children': self.dialog_edit
                }
            ]
        )
        
        # link the search textField 
        self.search_field.on_event('blur', self._on_search)
        self.edit_icon.on_event('click', self._on_click)
        self.dialog_edit.observe(self._on_dialog_change, 'custom_v_model')
        
        
    def _on_search(self, widget, data, event):    
        self.search = widget.v_model
        
        return 
        
    def _on_click(self, widget, data, event):
        
        self.dialog_edit.set_dialog(self.v_model)
        self.dialog_edit.value = True
        
        return
    
    def _on_dialog_change(self, change):
        
        data = json.loads(change['new'])
        
        # we need to change the full items traitlet to trigger a change 
        tmp = self.items.copy()
        
        # search for the item to modify 
        for item in tmp:
            if item['name'] == data['name']:
                item['weight'] = data['weight']
                item['layer'] = data['layer']
        
        # reply the modyfied items 
        self.items = tmp
        
        # notify the change to the rest of the app 
        self.change_model += 1
        
        return