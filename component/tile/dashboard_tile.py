from random import random

from sepal_ui import sepalwidgets as sw
import pandas as pd
import ipyvuetify as v

from component.message import cm
from component import widget as cw
from component import parameter as cp

class DashThemeTile(sw.Tile):
    
    def __init__(self):
        
        txt = sw.Markdown(cm.dashboard.theme.txt)
        
        # create the tile 
        super().__init__(
            id_ = "dashboard_widget",
            title = cm.dashboard.theme.title,
        )


    def dev_set_summary(self, json_themes_values):
        benefits_layer = []
        constraints_layer = []
        costs_layer = []

        for k,val in json_themes_values.items():
            for layer in json_themes_values[k]:
                if k == 'name':
                    # have name column as it will be good to add this while displaying at some point
                    continue
                name = layer
                try:
                    if k == 'benefits':
                        benefits_layer.append(cw.LayerFull(name, json_themes_values[k][layer]['values'],  json_themes_values[k][layer]['total']))
                    elif k == 'costs':
                        costs_layer.append(cw.LayerFull(name, json_themes_values[k][layer]['values'],  json_themes_values[k][layer]['total']))
                    elif k == 'constraints':
                        constraints_layer.append(cw.LayerPercentage(name, json_themes_values[k][layer]['values']))

                except Exception as e:
                    print(name, 'not found',e)
                    continue
        
        benefits = v.Html(tag='h2', children= ['Benefits'])

        benefits_txt = sw.Markdown('  /n'.join(cm.dashboard.theme.benefit))
        costs = v.Html(tag='h2', children= ['Costs'])
            
        costs_txt = sw.Markdown('  /n'.join(cm.dashboard.theme.cost))
        constraints = v.Html(tag='h2', children=['Constraints'])
            
        constraints_txt = sw.Markdown('  /n'.join(cm.dashboard.theme.constraint))
        self.set_content(
               [benefits, benefits_txt] + benefits_layer \
               + [costs, costs_txt] + costs_layer \
               + [constraints, constraints_txt] + constraints_layer
            )
        
        return self
            

    def set_summary(self, json_themes_values=None):
        
        # if none create fake data 
        if json_themes_values == None:
            
            json_themes_values = {'benefits': {}, 'costs': {}, 'constraint': {}}
            
            layer_list = pd.read_csv(cp.layer_list).fillna('')
            
            for row in layer_list.iterrows():
                
                if row[1].theme in ['benefits', 'costs']:
                    
                    json_themes_values[row[1].theme][row[1].layer_name] = {
                        'values': [int(random()*100) for _ in range(6)],
                        'total': 100
                    }
                    
                elif row[1].theme == 'constraint': 
                    json_themes_values[row[1].theme][row[1].layer_name] = {
                        'values': [int(random()*100) for _ in range(6)]
                    }
                    
            benefits = v.Html(tag='h2', children= ['Benefits'])

            benefits_txt = sw.Markdown('  /n'.join(cm.dashboard.theme.benefit))
            
            benefits_layer = []
            for layer in json_themes_values['benefits']:
                benefits_layer.append(cw.LayerFull(layer, json_themes_values['benefits'][layer]['values'], json_themes_values['benefits'][layer]['total']))
                
            costs = v.Html(tag='h2', children= ['Costs'])
            
            costs_txt = sw.Markdown('  /n'.join(cm.dashboard.theme.cost))
            
            costs_layer= []
            for layer in json_themes_values['costs']:
                costs_layer.append(cw.LayerFull(layer, json_themes_values['costs'][layer]['values'], json_themes_values['costs'][layer]['total']))
                
            constraints = v.Html(tag='h2', children=['Constraints'])
            
            constraints_txt = sw.Markdown('  /n'.join(cm.dashboard.theme.constraint))
            
            constraints_layer = []
            for layer in json_themes_values['constraint']:
                constraints_layer.append(cw.LayerPercentage(layer, json_themes_values['constraint'][layer]['values']))
                                   
            self.set_content(
               [benefits, benefits_txt] + benefits_layer \
               + [costs, costs_txt] + costs_layer \
               + [constraints, constraints_txt] + constraints_layer
            )
        
        return self
            
class DashRegionTile(sw.Tile):
    
    def __init__(self):
        
        super().__init__(
            id_ = 'dashboard_widget',
            title = cm.dashboard.region.title
        )
        
    def set_summary(self, json_feature_values=None):
    
        # if none create fake data 
        if json_feature_values == None:
            
            json_feature_values = {
                "AOI": {
                    "values": [
                        int(random()*100), # very low 
                        int(random()*100), # low 
                        int(random()*100), # medium
                        int(random()*100), # high
                        int(random()*100), # very high
                        int(random()*100), # unsustainable land
                    ]
                }
            }
        feats = []
        for feat in json_feature_values:
            
            feats.append(cw.AreaSumUp(feat, json_feature_values[feat]['values']))
                         
        self.set_content(feats)
                         
        return self
                         
         