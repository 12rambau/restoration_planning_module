from traitlets import observe

import ipyvuetify as v

class WeightSlider(v.Slider):
        
    _colors = {
        0: 'red',
        1: 'orange',
        2: 'yellow accent-3',
        3: 'light-green',
        4: 'green',
        5: 'primary',
        6: 'primary'
    }
    
    def __init__(self, name, default_value = 0, **kwargs):
        
        self.name = name
        
        super().__init__(
            max         = 6,
            min         = 0,
            track_color = 'grey',
            thumb_label = 'always',
            color       = self._colors[default_value],
            v_model     = default_value,
            class_      = 'ml-5 mr-5'
        )
        
    @observe('v_model')
    def on_change(self, change):
        self.color = self._colors[change['new']]
        return 