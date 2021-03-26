import ee
import json

# dev
from test_gee_compute_params import *
from functions import *
def _quintile(image, featurecollection, scale=100):
    quintile_collection = image.reduceRegions(collection=featurecollection, 
    reducer=ee.Reducer.percentile(percentiles=[20,40,60,80],outputNames=['low','lowmed','highmed','high']), 
    tileScale=2,scale=scale)

    return quintile_collection

def get_wlc_stats(wlc, aoi):
    aoi_as_fc = ee.FeatureCollection(aoi)
    wlc_quintile = _quintile(wlc, aoi_as_fc)

    return wlc_quintile


def get_summary_statistics(wlc, aoi, benefits, costs, constraints):
    # returns summarys for the dashboard. 
    # restoration sutibuility
    wlc_summary = get_wlc_stats(wlc,aoi)

    # benefits
    all_benefits = get_benefit_stats(benefits, aoi)

    # costs
    all_costs = get_cost_stats(costs, aoi)

    #cconstraints
    all_constraints = get_constraint_status(constraints, aoi)

    return wlc_summary.merge(all_benefits).merge(all_costs).merge(all_constraints)

if __name__ == "__main__":
    ee.Initialize()
    io = fake_io()
    region = fake_aoi_io()
    layerlist = io.layer_list

    aoi = region.get_aoi_ee()

    wlc_out, benefits_layers, constraints_layers = gee_compute(region,io,io).wlc()
    
    # get wlc quintile 
    t1 = get_wlc_stats(wlc_out, aoi)
    print(t1.getInfo())