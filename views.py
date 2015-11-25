'''
Created on 2015-11-14

@author: sun
'''
from django.shortcuts    import render_to_response
from django.http import HttpResponse
import json

from lib.NERchunk import chunk_stanfordNE
from lib.opencalais import opencalaisParse
def index(request):
    return render_to_response("index.html")

def parse(request):
    if "input" in request.GET and request.GET["input"]:
        content = request.GET["input"]
        opencalaisdic = opencalaisParse(content)
        geodic = {}
        geodic.setdefault('type','FeatureCollection')
        geodic.setdefault('features',[])
        for key in opencalaisdic.keys():
            if opencalaisdic[key]['coordinates'] == ["",""]:
                continue
            else:
                pass
            featuredic = {}
            featuredic.setdefault('type','Feature')
            featuredic.setdefault('properties',{})
            featuredic['properties']['title'] = key
            featuredic['properties']['marker-color'] = '#f86767'
            featuredic['properties']['marker-size'] = 'large'
            featuredic['properties']['description'] = opencalaisdic[key]['description']
            featuredic['properties']['exacts'] = opencalaisdic[key]['exacts']
            featuredic.setdefault('geometry',{})
            featuredic['geometry']['type'] = 'Point'
            featuredic['geometry']['coordinates'] = opencalaisdic[key]['coordinates']
            print featuredic
            geodic['features'].append(featuredic)
    #return render_to_response("index.html")
    response = HttpResponse(json.dumps(geodic, ensure_ascii = False),"application/json");
    return response