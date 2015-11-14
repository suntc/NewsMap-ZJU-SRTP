'''
Created on 2015-11-14

@author: sun
'''
from django.shortcuts    import render_to_response

from lib.NERchunk import chunk_stanfordNE

def index(request):
    return render_to_response("index.html")

def parse(request):
    if "content" in request.GET and request.GET["content"]:
        content = request.GET["content"]
        print chunk_stanfordNE(content)
    return render_to_response("index.html")