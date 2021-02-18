from sepal_ui import sepalwidgets as sw 
import ipyvuetify as v

from component import widget as cw
from component.message import cm
from component import io as cio
from component import scripts as cs
        
class CustomizeLayerTile(sw.Tile):
    
    def __init__(self, io, questionnaire_io, **kwargs):
        
        # link the ios to the tile
        self.io = io
        self.questionnaire_io = questionnaire_io
        
        # name the tile
        id_ = "manual_widget"
        title = "Customize layers input"
        
        # create the btns
        self.reset_to_questionnaire = sw.Btn(
            text   = 'Apply questionnaire answers', 
            icon   = 'mdi-file-question-outline',
            class_ = 'ml-5 mr-2'
        )
        self.reset_to_questionnaire.color = 'success'
        
        self.reset_to_default = sw.Btn(
            text   = 'Apply default parameters',
            icon   = 'mdi-restore', 
            class_ = 'ml-2'
        )
        self.reset_to_default.color = 'warning'
        
        self.btn_line = v.Row(
            class_   = 'mb-3',
            children = [self.reset_to_questionnaire, self.reset_to_default]
        )
        
        self.table = cw.LayerTable()
        
        # create the txt 
        self.txt = sw.Markdown(cm.questionnaire.custom_tile_txt)
        
        # build the tile 
        super().__init__(
            id_, 
            title,
            inputs = [
                self.txt,
                self.btn_line,
                self.table
            ],
            **kwargs
        )
        
        # js behaviours
        self.table.observe(self._on_item_change, 'change_model')
        self.reset_to_default.on_event('click', self._apply_default)
        self.reset_to_questionnaire.on_event('click', self._apply_questionnaire)
        
    def _on_item_change(self, change):
            
        # normally io and the table have the same indexing so I can take advantage of it 
        for i in range (len(self.io.layer_list)):
            io_item = self.io.layer_list[i]
            item = self.table.items[i]
            
            io_item['layer'] = item['layer']
            io_item['weight'] = item['weight']
            
        return self
        
    def apply_values(self, layers_values):
        """Apply the value that are in the layer values table. layer_values should have the exact same structure as the io define in this file"""
        
        # small check on the layer_value structure
        if len(layers_values) != len(self.io.layer_list):
            return
        
        # apply the modification to the widget (the io will follow with the observe methods)
        for i, dict_ in enumerate(layers_values):
            
            # apply them to the table
            if self.table.items[i]['name'] == dict_['name']:
                self.table.items[i].update(
                    layer  = dict_['layer'],
                    weight = dict_['weight']
                )
                
            # notify the change to rest of the app 
            self.table.change_model += 1
                     
        return self 
    
    def _apply_default(self, widget, data, event):
        """apply the default layer table to the layer_io"""
        
        # toggle the btns
        self.reset_to_default.toggle_loading()
        self.reset_to_questionnaire.toggle_loading()
    
        # load a default layer_io 
        self.apply_values(cio.default_layer_io.layer_list)
    
        # manually change the items
        # for no reason the display items doesn't upload programatically
        new_items = self.table.items.copy()
        self.table.items = new_items
    
        # toggle the btns
        self.reset_to_default.toggle_loading()
        self.reset_to_questionnaire.toggle_loading()
    
        return self 
    
    def _apply_questionnaire(self, widget, event, data):
        """apply the answer to the questionnaire to the datatable"""
        
        # toggle the btns
        self.reset_to_default.toggle_loading()
        self.reset_to_questionnaire.toggle_loading()
    
        # process the questionnaire to produce a layer list 
        layers_values = cs.compute_questionnaire(self.questionnaire_io)
        self.apply_values(layers_values)
    
        # manually change the items
        # for no reason the display items doesn't upload programatically
        new_items = self.table.items.copy()
        self.table.items = new_items
    
        # toggle the btns
        self.reset_to_default.toggle_loading()
        self.reset_to_questionnaire.toggle_loading()
    
        return self 
        
        