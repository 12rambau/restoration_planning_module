from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su
import ipyvuetify as v
from .. import message as ms
from .. import parameter as pm
import json
from traitlets import HasTraits, Unicode

class PotentialTile(sw.Tile, HasTraits):
    
    # create custom_v_model as a traitlet
    # the traitlet List cannot be listened to so we were force to use Unicode json instead
    custom_v_model = Unicode('').tag(sync=True)
    
    def __init__(self, **kwargs):
        
        # name the tile 
        title = "Restoration potential and land use" 
        id_ = 'nested_widget'
        
        #default custom_v_model
        self.custom_v_model = json.dumps({label: -1 for label in  pm.land_use})
        
        # short description of the tile
        tile_txt = sw.Markdown(ms.POTENTIAL_TXT)
        
        # select the potential land use
        self.land_use = v.Select(
            chips    = True,
            v_model  = [], 
            label    = ms.LAND_USE_SELECT_LABEL,
            items    = pm.land_use,
            multiple = True
        )
        
        self.pcnt_treecover = [v.Slider(v_model=None, thumb_label=True, disabled=True, label=f'treecover in {label}') for label in pm.land_use]
        for slider in self.pcnt_treecover:
            su.hide_component(slider)

        # create the tile 
        super().__init__(
            id_, 
            title, 
            inputs = [tile_txt, self.land_use] + self.pcnt_treecover,
            **kwargs
        )
        
        # hide the border                           
        self.children[0].elevation = 0
        
        # link the widgets together 
        self.land_use.observe(self.__on_select, 'v_model')
        for slider in self.pcnt_treecover:
            slider.observe(self.__on_change_treecover, 'v_model')
        
    def __on_select(self, change):
        
        val = change['new']
        
        # load the custom_v_model
        tmp = json.loads(self.custom_v_model)
        
        for label, slider in zip(pm.land_use, self.pcnt_treecover):
            if label in val:
                tmp[label] = slider.v_model
                slider.disabled = False
                su.show_component(slider)
            else:
                tmp[label] = -1
                slider.disabled = True
                su.hide_component(slider)
        
        # save the new values 
        self.custom_v_model = json.dumps(tmp)
        
        return 
            
    def __on_change_treecover(self, change):
        
        # load the custom_v_model
        tmp = json.loads(self.custom_v_model)
        
        # get the slider 
        for label, slider in zip(pm.land_use, self.pcnt_treecover):
            if slider == change['owner']:
                tmp[label] = change['new']
        
        # save the value
        self.custom_v_model = json.dumps(tmp)
        
        return
                                     