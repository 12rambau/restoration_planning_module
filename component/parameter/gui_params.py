# list of the available constraint criteria
# None for binary inputs 
# dict for dropdonw 
# integer for the max  of a range input
# 'header' for headers
criterias = {
    'Land use constraints': 'header',
    'Bare land': None,
    'Shrub land': None,
    'Agricultural land': None,
    'Biophysical constraints': 'header',
    'Annual rainfall': [
        {'text': 'high precipitaion',    'value': 10},
        {'text': 'medium precipitaion', 'value': 5},
        {'text': 'low precipitaion',    'value': 0},
    ],
    'Elevation': [
        {'text': 'high altitude',    'value': 1000},
        {'text': 'medium altitude', 'value': 500},
        {'text': 'low altitude',    'value': 0},
    ],
    'Slope' : [
        {'text': 'high slope',    'value': 100},
        {'text': 'medium slope', 'value': 50},
        {'text': 'low slope',    'value': 10},
    ],
    'Socio-economic constraints': 'header',
    'Population': [
        {'text': 'high populated',    'value': 10e6},
        {'text': 'medium populated', 'value': 10e3},
        {'text': 'low populated',    'value': 10},
    ],
    'Protected area': None,
    'Opportunity cost': [
        {'text': 'cost a lot',    'value': 100},
        {'text': 'medium cost', 'value': 50},
        {'text': 'low cost',    'value': 10},
    ],
    'Tree cover constraints within land cover classes': 'header',
    "Agriculture": 100,
    "Rangeland": 100,
    "Grassland": 100,
    "settlements": 100
}

# list of the available priorities for the priority tile
priorities = [
    'Local livelihoods',
    'Wood production',
    'Non-timber tree benefits',
    'Water quality'
]