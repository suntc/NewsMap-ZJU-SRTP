'''
Created on 2016-04-30

@author: Sun Tianchen
'''
from django.shortcuts    import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import calendar
from newspaper import Article
#from lib.buildcalais import calais_api # originated from python/infoextract/buildcalais.py
#from lib.recommender import recommender
#from lib.wikicat import sparqlquerier
import sys
from django.contrib.sessions.models import Session
sys.path.append("../infoextract/")
from recommender import recommender
from wikicat import sparqlquerier
from buildcalais import calais_api
from ontologystatistics import ontstats
from thememap import mapdict

rec = recommender()
print("load recommender...")
rec.load_db()
print("done")
stat = ontstats()
#stat.load()
mapdict = mapdict()


def index(request):
	return render_to_response("index.html")

def parse(request):
	if "input" in request.GET and request.GET["input"]:
		url = request.GET["input"]
		print(url)
	article = {}
	(article['title'], article['text'], pdate, article['image']) = extract(url)
	if (pdate != None):
		article["date"] = str(pdate.day) + ' ' + calendar.month_abbr[pdate.month] + ', ' + str(pdate.year)
	else:
		article["date"] = "null"
	request.session['url'] = url
	request.session['content'] = article['text']
	response = HttpResponse(json.dumps(article, ensure_ascii = False),"application/json");
	'''	
	info = calais_info(text)
	(w_list, lc_list, en_list, tp_list) = rec_news(content,info)
	maps = gen_map(info)
	'''
	return response

@csrf_exempt
def recommend(request):
	if "type" in request.POST and request.POST["type"]:
		type = request.POST["type"]
		print(type)
	#print(request.session['content'])
	print("query calais info...")
	info = calais_info(request.session['content'])
	print("done")
	request.session['info'] = info
	l = rec_news(request.session['url'],info,type)
	response = HttpResponse(json.dumps(l, ensure_ascii = False),"application/json");
	return response
	
	
def extract(u):
	article = Article(url=u)
	article.download()
	article.parse()
	return (article.title,article.text,article.publish_date,article.top_image)

def calais_info(text):
	'''
	require standard calais_info (for computing similarity)
	other usage: (socialTag, entity) --> word cloud
	'''
	cls = calais_api()
	result = cls.query(text)
	info = cls.filter(result) # dict: info = {"socialTag":[], "topic":[], "entity":[], "location":[]}
	return info

def rec_news(url,cinfo,type):
	print("recommend: 4 similarities and 4 sorts...")
	rec.prepare(url,cinfo)
	print("done")
	g_w = {"location":1,"entity":0.8,"social_tag":1.2,"topic":1}
	lc_w = {"location":1,"entity":0,"social_tag":0,"topic":0}
	en_w = {"location":0,"entity":1,"social_tag":0,"topic":0}
	tp_w = {"location":0,"entity":0,"social_tag":0.5,"topic":1}
	if type == "general":
		return rec.recommend(url,g_w,fetch=7)
	elif type == "location":
		return rec.recommend(url,lc_w,fetch=7)
	elif type == "entity":
		return rec.recommend(url,en_w,fetch=7)
	elif type == "topic":
		return rec.recommend(url,tp_w,fetch=7)


def gen_map(cinfo,fetch=5):
	maps = {}
	wn_stat = {} # (tf,[wikicats,...])
	spa = sparqlquerier()
	st = st_importance(cinfo)
	wcdict = spa.wikicat(list(st.keys())) # wcdict[i["valueOrObject"]["value"]].append(tag) # each wikicat maps a list of socialTag
	wcset = set(wcdict.keys())
	for item in wcset:
		if item in mapdict.maps:
			maps[item] = {}
			'''
			add other information: mapjson, title, description, numeric info...
			'''
			maps[item]["score"] = []
			maps[item]["score"].append(1) # wikicat level
			maps[item]["score"].append(-1) # tfidf, wikicat does not have tfidf yet...
			maps[item]["score"].append(max([st[tag] for tag in wcdict[item]])) # importance
			if item in stat.ontology:
				maps[item]["score"].append(stat.ontology[item]) # appearance count from corpus
		if item in stat.taxonomy:
			wn_stat.setdefault(stat.taxonomy[item],(0,[]))
			wn_stat[stat.taxonomy[item]][0] += 1
			wn_stat[stat.taxonomy[item]][1] += wcdict[item]
	for item in wn_stat:
		if item in mapdict.maps:
			maps[item] = {}
			'''
			add other information: mapjson, title, description, numeric info...
			'''
			maps[item]["score"] = []
			maps[item]["score"].append(0) # wikicat level
			if item in stat.wn_idf: # tfidf
				maps[item]["score"].append(wn_stat[item][0] * stat.wn_idf[item])
			else:
				maps[item]["score"].append(wn_stat[item][0] * stat.wn_idf["DEFAULT"])
			maps[item]["score"].append(max([st[tag] for tag in wn_stat[item][1]])) # importance
			maps[item]["score"].append(-1) # appearance count, not needed with tf-idf
	to_rank = [item for item in maps]
	to_rank.sort(key=lambda k:(k["score"][0],k["score"][1],k["score"][2],k["score"][3]),reverse=True)
	return to_rank[:fetch]

def st_importance(info):
	st = {}
	for tag in info["socialTag"]:
		st[tag["name"]] = tag["importance"] # {"Obama Campaign 2012":2,...}
	return st