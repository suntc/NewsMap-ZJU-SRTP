'''
Created on 2016-04-30

@author: Sun Tianchen
'''
from django.shortcuts    import render_to_response
from django.http import HttpResponse
import json
from newspaper import Article
#from lib.buildcalais import calais_api # originated from python/infoextract/buildcalais.py
#from lib.recommender import recommender
#from lib.wikicat import sparqlquerier
import sys
sys.path.append("../infoextract/")
from recommender import recommender
from wikicat import sparqlquerier
from buildcalais import calais_api
from ontologystatistics import ontstats
from thememap import mapdict

rec = recommender()
rec.load_db()
stat = ontstats()
stat.load()
mapdict = mapdict()


def index(request):
	return render_to_response("index.html")

def parse(request):
	if "input" in request.GET and request.GET["input"]:
		content = request.GET["input"]
		print(content)
	(title, text, date, image) = extract(content)
	info = calais_info(text)
	(w_list, lc_list, en_list, tp_list) = rec_news(content,info)
	response = HttpResponse(json.dumps({"hehe":123}, ensure_ascii = False),"application/json");
	maps = gen_map(info)
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

def rec_news(url,cinfo):
	rec.prepare(url,cinfo)
	g_w = {"location":1,"entity":0.8,"social_tag":1.2,"topic":1}
	lc_w = {"location":1,"entity":0,"social_tag":0,"topic":0}
	en_w = {"location":0,"entity":1,"social_tag":0,"topic":0}
	tp_w = {"location":0,"entity":0,"social_tag":0.5,"topic":1}
	w_list = rec.recommend(g_w)
	lc_list = rec.recommend(lc_w)
	en_list = rec.recommend(en_w)
	tp_list = rec.recommend(tp_w)
	return w_list, lc_list, en_list, tp_list


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