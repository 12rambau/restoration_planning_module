import ipyvuetify as v
from traitlets import observe, HasTraits, Unicode
import json

from sepal_ui import sepalwidgets as sw

from .. import message as ms 
from .. import parameter as pm

class lessMore(v.Switch):
    
    def __init__(self, **kwarg):
        
        self.items = ['less than', 'more than']
        
        super().__init__(
            v_model = False,
            label = self.items[0]
        )
        
    @observe('v_model')
    def __on_change(self, change):
        # boolean value are transformed into 0 and 1 for the list
        self.label = self.items[change['new']]
        
    
        
class Criteria (v.Row, HasTraits):
    
    # create custom_v_model as a traitlet
    # the traitlet List cannot be listened to so we were force to use Unicode json instead
    custom_v_model = Unicode('').tag(sync=True)

    def __init__(self, name = 'name', default_value = None, **kwarg):
        
        self.name = name
        self.less_more = lessMore()
        self.number = v.TextField(type="number", v_model = default_value)
        
        # v_model discribe as a list with [name, active (as bool), lt or gt (0-1), value]
        self.custom_v_model = json.dumps([name, False, False, default_value])
        super().__init__(
            children = [
                v.Flex(
                    class_ = 'align-center', 
                    xs2 = True, 
                    children = [
                        v.Html(class_ = 'align-center', tag = 'h4', children = [name])
                    ]
                ),
                v.Flex(xs2 = True, children = [self.less_more]),
                v.Flex(xs1 = True, children = [self.number])
            ],
            **kwarg
        )
        
        self.class_ = self.class_ + ' pa-5' if self.class_ else 'pa-5'
        
        
        # listen to modification 
        self.less_more.observe(self.__on_switch, 'v_model')
        self.number.observe(self.__on_value, 'v_model')
            
    def __on_switch(self, change):
        tmp = json.loads(self.custom_v_model)
        tmp[2] = change['new']
        self.custom_v_model = json.dumps(tmp)
        
    def __on_value(self, change):
        tmp = json.loads(self.custom_v_model)
        tmp[3] = int(change['new'])
        self.custom_v_model = json.dumps(tmp)
        
    def activate(self):
        tmp = json.loads(self.custom_v_model)
        tmp[1] = True
        self.custom_v_model = json.dumps(tmp)
        su.show_component(self)
        
    def deactivate(self):
        tmp = json.loads(self.custom_v_model)
        tmp[1] = False
        self.custom_v_model = json.dumps(tmp)
        su.hide_component(self)
        
from sepal_ui.scripts import utils as su

class ConstraintTile(sw.Tile, HasTraits):
    
    # create custom_v_model as a traitlet
    # the traitlet List cannot be listened to so we were force to use Unicode json instead
    
    # build as such : 
    # { 'criteria_name' : [active (as bool), lt or gt (0-1), value], ...}
    custom_v_model = Unicode('').tag(sync=True)
    
    def __init__(self, **kwargs):
        
        # name the tile 
        title = "Constraints" 
        id_= 'nested_widget'
        
        # write a quick explaination 
        tile_txt = sw.Markdown(ms.CONSTRAINT_TXT)
        
        # select widget to select the actives criterias
        self.critera_select = v.Select(
            v_model  = None,
            items    = pm.criterias,
            label    = ms.CRITERIA_LABEL,
            multiple = True
        )
        
        # criteria widget that will be used to change the impact of each criteria and hide them
        self.criterias_values = [Criteria(name=name, class_='d-none') for name in pm.criterias]
        
        # default custom_v_model
        self.custom_v_model = json.dumps({c.name: json.loads(c.custom_v_model)[1:] for c in self.criterias_values})
        
        # cration of the tile 
        super().__init__(
            id_, 
            title, 
            inputs = [
                #tree_cover_switch, 
                tile_txt, 
                self.critera_select
            ] + self.criterias_values, 
            **kwargs
        )
        
        # hide the tile border
        self.children[0].elevation = 0
        
        # link the visibility of each criteria to the select widget
        self.critera_select.observe(self.__on_select, 'v_model')
        self.__link_criterias()
        
    def __on_select(self, change):
            
        for criteria in self.criterias_values:
            # change the visibility and activation process
            if criteria.name in change['new']: 
                criteria.activate()
            else:
                criteria.deactivate()
        
        return 
    
    def __link_criterias(self):
        
        # link all the criterias to custom_v_model
        for criteria in self.criterias_values:
            criteria.observe(self.__on_change, 'custom_v_model')
        
    
    def __on_change(self, change):
        
        # get the value from json custom_v_model
        val = json.loads(change['new'])
        
        # insert the new values in custom_v_model
        tmp = json.loads(self.custom_v_model)
        tmp[val[0]] = val[1:]
        self.custom_v_model = json.dumps(tmp)
        
        
       