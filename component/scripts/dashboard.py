import ee
import json
from datetime import datetime as dt
# from component import utils
import os

import geemap

def _quintile(image, geometry, scale=100):
    """Computes standard quintiles of an image based on an aoi. returns feature collection with quintiles as propeties""" 
    
    quintile_collection = image.reduceRegion(
        geometry=geometry, 
        reducer=ee.Reducer.percentile(
            percentiles=[20,40,60,80],
            outputNames=['low','lowmed','highmed','high']
        ), 
        tileScale=2,
        scale=scale, 
        maxPixels=1e13
    )

    return quintile_collection

def count_quintiles(image, geometry, scale=100):
    
    histogram_quintile = image.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram().unweighted(),
        geometry=geometry,
        scale=scale, 
        # bestEffort=True, 
        maxPixels=1e13, 
        tileScale=2
    )
    
    return histogram_quintile

#def get_aoi_name(selected_info):
#    # i think this is useless as the aoi_io embed a get_aoi_name method
#    
#    if 'country_code' in selected_info:
#        selected_name = selected_info['country_code']
#    elif isinstance(selected_info,str):
#        selected_name = selected_info
#    else:
#        # TODO : add this to lang.json 
#        selected_name = 'Custom Area of Interest'
#        
#    return selected_name

def get_image_stats(image, geeio, name, mask, total, geom, scale=100):
    """ computes quintile breaks and count of pixels within input image. returns feature with quintiles and frequency count"""
    
    #aoi_as_fc = ee.FeatureCollection(geeio.aoi_io.get_aoi_ee())

    # should move quintile norm out of geeio at some point...along with all other utilities
    image_quin, bad_features = geeio.quintile_normalization(image,geeio.aoi_io.get_aoi_ee())
    image_quin = image_quin.where(mask.eq(0),6)
    quintile_frequency = count_quintiles(image_quin, geom)

    #selected_name = get_aoi_name(selected_info)
    list_values = ee.Dictionary(quintile_frequency.values().get(0)).values()

    out_dict = ee.Dictionary({
        'suitibility':{
            name:{
                'values':list_values,
                'total' : total,
                'geedic':quintile_frequency
            }
        }
    })
    
    return out_dict

def get_aoi_count(aoi, name):
    
    count_aoi = ee.Image.constant(1).rename(name).reduceRegion(
        reducer = ee.Reducer.count(), 
        geometry = aoi,
        scale = 100,
        maxPixels = 1e13
    )
    
    return count_aoi

def get_image_percent_cover(image, aoi, name):
    """ computes the percent coverage of a constraint in relation to the total aoi. returns dict name:{value:[],total:[]}"""
    
    count_img = image.Not().selfMask().reduceRegion(
        reducer = ee.Reducer.count(), 
        geometry = aoi,
        scale = 100,
        maxPixels = 1e13,
    )
    
    total_img = image.reduceRegion(
        reducer = ee.Reducer.count(), 
        geometry= aoi,
        scale = 100,
        maxPixels = 1e13,
    )
    
    total_val = ee.Number(total_img.values().get(0))
    count_val = ee.Number(count_img.values().get(0))

    percent = count_val.divide(total_val).multiply(100)
    
    value = ee.Dictionary({
        'values':[percent],
        'total':[total_val]
    })
    
    return ee.Dictionary({name:value})
    
def get_image_sum(image, aoi, name, mask):
    """computes the sum of image values not masked by constraints in relation to the total aoi. returns dict name:{value:[],total:[]}"""
     
    sum_img = image.updateMask(mask).reduceRegion(
        reducer = ee.Reducer.sum(), 
        geometry = aoi,
        scale = 100,
        maxPixels = 1e13,
    )
    
    total_img = image.reduceRegion(
        reducer = ee.Reducer.sum(), 
        geometry = aoi,
        scale = 100,
        maxPixels = 1e13,
    )

    value = ee.Dictionary({
        'values':sum_img.values(),
        'total':total_img.values()
    })
    
    return ee.Dictionary({name:value})

def get_summary_statistics(geeio, name, geom):
    """returns summarys for the dashboard.""" 

    count_aoi = get_aoi_count(geom, 'aoi_count')

    # restoration suitability
    wlc, benefits, constraints, costs = geeio.wlcoutputs
    mask = ee.ImageCollection(list(map(lambda i: ee.Image(i['eeimage']).rename('c').byte(), constraints))).min()

    # restoration pot. stats
    wlc_summary = get_image_stats(wlc, geeio, name, mask, count_aoi.values().get(0), geom)

    #try:
    layer_list = geeio.rp_layers_io.layer_list
    #except:
    #    layer_list = layerlist

    # benefits
    # remake benefits from layerlist as original output are in quintiles
    all_benefits_layers = [i for i in layer_list if i['theme'] == 'benefits']
    list(map(lambda i : i.update({'eeimage':ee.Image(i['layer']).unmask() }), all_benefits_layers))

    benefits_out = ee.Dictionary({'benefits':list(map(lambda i : get_image_sum(i['eeimage'],geom, i['name'], mask), all_benefits_layers))})

    # costs
    costs_out = ee.Dictionary({'costs':list(map(lambda i : get_image_sum(i['eeimage'],geom, i['name'], mask), costs))})

    #constraints
    constraints_out =ee.Dictionary({'constraints':list(map(lambda i : get_image_percent_cover(i['eeimage'],geom, i['name']), constraints))}) 

    #combine the result 
    result = wlc_summary.combine(benefits_out).combine(costs_out).combine(constraints_out)
    
    return ee.String.encodeJSON(result).getInfo()


def get_stats_as_feature_collection(wlcoutputs, geeio, selected_info,**kwargs):
    
    # get the aoi 
    if 'aoi' in kwargs:
        aoi = kwargs['aoi']
    else:
        aoi = geeio.aoi_io.get_aoi_ee()
    
    # compute the stats
    stats = get_summary_statistics(wlcoutputs, aoi, geeio, selected_info)
    geom = ee.Geometry.Point([0,0])
    feat = ee.Feature(geom).set(stats)
    fc = ee.FeatureCollection(feat)

    return fc

def get_stats_w_sub_aoi(wlcoutputs, geeio, selected_info, features):
    
    aoi_stats = get_stats_as_feature_collection(wlcoutputs, geeio, selected_info)
    
    ee_geom_list = [geemap.geojson_to_ee(feat).geometry() for feat in features['feature']]
    sub_stats = [get_stats_as_feature_collection(wlcoutputs, geeio, f'Sub region {i}',aoi=geom) for i, geom in enumerate(ee_geom_list)]
    
    sub_stats = ee.FeatureCollection(sub_stats).flatten()
    
    combined = aoi_stats.merge(sub_stats)
    
    return combined

def get_stats(geeio, aoi_io, features):
    
    # create a name list
    names = [aoi_io.get_aoi_name() if not i else f'Sub region {i}' for i in range(len(features['features']))]
    
    # create the final featureCollection 
    # the first one is the aoi and the rest are sub areas
    ee_aoi_list = [aoi_io.get_aoi_ee()]
    for feat in  features['features']:
        ee_aoi_list += geemap.geojson_to_ee(feat)
        
    # create the stats dictionnary
    #stats = [get_summary_statistics(geom, geeio, selected_info)
        
    stats = [get_summary_statistics(geeio, names[i], geom) for i, geom in enumerate(ee_aoi_list)]
    
    print(stats)
    
    return None, None

def export_stats(fc):
    
    suffix = dt.now().strftime("%Y%m%d%H%M%S")
    desc = f"restoration_dashboard_{suffix}"
    task = ee.batch.Export.table.toDrive(
        collection=fc, 
        description=desc,
        folder='restoration_dashboard',
        fileFormat='GeoJSON'
    )
    
    task.start()
    print(task.status())
    return desc

def getdownloadasurl(fc):
    
    # TODO update to send the files to the module_results folder 
    # urlretreive can be used to avoid the call to os.system
    
    # hacky way to download data until I can figure out downlading from drive
    suffix = dt.now().strftime("%Y%m%d%H%M%S")
    desc = f"restoration_dashboard_{suffix}"
    url = fc.getDownloadURL('GeoJSON', filename=desc)
    dest = r"."
    file = f'{dest}/{desc}.GEOjson'

    os.system(f'curl {url} -H "Accept: application/json" -H "Content-Type: application/json" -o {file}')

    with open(file) as f:
        json_features = json.load(f)
    os.remove(file)
    return json_features

if __name__ == "__main__":
    
    # TODO are you still using it ? 
    
    # dev
    from test_gee_compute_params import *
    from functions import *
    
    ee.Initialize()
    
    io = fake_io()
    io_default = fake_default_io()
    region = fake_aoi_io()
    layerlist = io.layer_list

    aoi = region.get_aoi_ee()
    geeio = gee_compute(region,io,io_default,io)
    wlcoutputs= geeio.wlc()
    wlc_out = wlcoutputs[0]
    selected_info = [None]
    # test getting as fc for export
    t7 = get_stats_as_feature_collection(wlcoutputs,geeio,selected_info)
    # print(t7.getInfo())
    f = getdownloadasurl(t7)
    print(f, type(f))

    # test wrapper
    # t0 = get_summary_statistics(wlcoutputs,geeio)
    # print(t0.getInfo())
    # get wlc quntiles  
    # t1 = get_image_stats(wlc_out, geeio, selected_info)
    # print(t1.getInfo())

    # get dict of quintile counts for wlc
    # print(type(wlc_out),wlc_out.bandNames().getInfo())
    # wlc_quintile, bad_features = geeio.quintile_normalization(wlc_out,ee.FeatureCollection(aoi))
    # t2 = count_quintiles(wlc_quintile, aoi)
    # print(ee.Dictionary(t2.get('constant')).values().getInfo())

    # test getting aoi count
    # count_aoi = get_aoi_count(aoi, 'aoi_count')
    # print(count_aoi.values().getInfo())
    
    # c = wlcoutputs[2]
    # # print(c)
    # cimg = ee.ImageCollection(list(map(lambda i : ee.Image(i['eeimage']).byte(), c))).min()
    # # print(cimg)

    # a = wlcoutputs[1][0]
    # # print(a)

    # # b = get_image_count(a['eeimage'],aoi, a['name'])
    # # # print(b.getInfo())
    # all_benefits_layers = [i for i in layerlist if i['theme'] == 'benefits']
    # list(map(lambda i : i.update({'eeimage':ee.Image(i['layer']).unmask() }), all_benefits_layers))

    # t = ee.Dictionary({'benefits':list(map(lambda i : get_image_sum(i['eeimage'],aoi, i['name'], cimg), all_benefits_layers))})
    # # # seemingly works... worried a bout total areas all being same, but might be aoi
    # print(t.getInfo())