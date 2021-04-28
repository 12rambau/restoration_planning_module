from sepal_ui import sepalwidgets as sw 
from sepal_ui import mapping as sm
import ipyvuetify as v

from component.message import cm
from component import parameter as cp

class MapTile(sw.Tile):
    
    def __init__(self):
        
        # add the explanation
        mkd = sw.Markdown('  \n'.join(cm.map.txt))
        
        # create the map 
        self.m = sm.SepalMap()
        self.m.add_colorbar(colors=cp.red_to_green, vmin=0, vmax=5)
        self.m.set_drawing_controls(add=True)
        
        # create a layout with 2 btn 
        self.to_asset = sw.Btn(cm.map.to_asset, class_='ma-2', disabled=True)
        self.to_sepal = sw.Btn(cm.map.to_sepal, class_='ma-2', disabled=True)
        self.draw_custom_area = sw.Btn(cm.map.draw_custom_area, class_='ma-2', disabled=False)
        
        self.draw_custom_area.on_event('click',self._add_dc)
        
        # create the tile
        super().__init__(
            id_ = "map_widget",
            title = cm.map.title,
            inputs = [mkd, self.m],
            output = sw.Alert(),
            btn = v.Layout(children=[
                self.to_asset, 
                self.to_sepal,
                self.draw_custom_area,
            ])
        )
    
    def _add_dc(self, widget, data, event):
        self.m.show_dc()
        return self