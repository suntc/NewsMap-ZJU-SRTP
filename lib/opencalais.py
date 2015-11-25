import sys
import requests
import os
from StringIO import StringIO
import ast
import re

calais_url = 'https://api.thomsonreuters.com/permid/calais'
access_token = 'hOtCOmaV48bRp2EIzm2LGbyhQb3X3UtS'
headers = {'X-AG-Access-Token' : access_token, 'Content-Type' : 'text/raw', 'outputformat' : 'application/json' , 'x-calais-language' : 'english'}

targetType = ('City',)
targetInfo = ('name','resolutions')

def opencalaisParse(text):
    files = {'file': StringIO(text)}
    response = requests.post(calais_url, files=files, headers=headers, timeout=80)
    print 'status code: %s' % response.status_code
    content = response.content
    #print 'Results received: %s' % content
    dic = ast.literal_eval(content)
    simpledic = {}
    longitude = latitude = ""
    for key in dic.keys():
        if '_type' in dic[key].keys() and dic[key]['_type'] in targetType:
            for k in dic[key].keys():
                print k,dic[key][k]
            try:
                descriptions = []
                exacts = []
                name = dic[key]['name']
                resolutions = dic[key]['resolutions'][0]
                instances = dic[key]['instances']
                longitude = resolutions['longitude']
                latitude = resolutions['latitude']
                for item in instances:
                    exact = item['exact']
                    des = item['detection'][1:-1]
                    des = re.sub('\]'+exact+'\[',r"<span style = 'color:#EF0FFF'>"+exact+r"</span>",des)
                    descriptions.append(des)
                    if exact not in exacts:
                        exacts.append(exact)
                description = "<br><br>".join(descriptions)
            except Exception,e:
                pass
            simpledic.setdefault(name,{})
            simpledic[name].setdefault('coordinates',[longitude,latitude])
            simpledic[name].setdefault('description',description)
            simpledic[name].setdefault('exacts',exacts)
            #for item in instances:
                #print item['detection'].replace('\n','').replace('[','').replace(']','').strip()
    return simpledic
