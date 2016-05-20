'''
Created on 2016-04-30

@author: Sun Tianchen
'''
from django.shortcuts    import render_to_response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import nltk.data

import json
import calendar
from math import pow

from newspaper import Article
#from lib.buildcalais import calais_api # originated from python/infoextract/buildcalais.py
#from lib.recommender import recommender
#from lib.wikicat import sparqlquerier
import sys
from django.contrib.sessions.models import Session
from django.template.context_processors import request

sys.path.append("../infoextract/")
from recommender import recommender
from wikicat import sparqlquerier
from buildcalais import calais_api
from ontologystatistics import ontstats
from thememap import mapdict
from calaisstats import calais_stats

rec = recommender()
print("load recommender...")
rec.load_db()
print("done")
print("load ontology...")
stat = ontstats()
stat.load()
print("done")
mapdict = mapdict()
cs = calais_stats()
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')


def index(request):
	return render_to_response("index.html")

def parse(request):
	if "input" in request.GET and request.GET["input"]:
		url = request.GET["input"]
		print(url)
	article = {}
	(article['title'], text, pdate, article['image']) = extract(url)
	if (pdate != None):
		article["date"] = str(pdate.day) + ' ' + calendar.month_abbr[pdate.month] + ', ' + str(pdate.year)
	else:
		article["date"] = ""
	article['text'] = text.replace('\n','<br>')
	request.session['url'] = url
	request.session['content'] = text
	response = HttpResponse(json.dumps(article, ensure_ascii = False),"application/json");
	'''	
	info = calais_info(text)
	(w_list, lc_list, en_list, tp_list) = rec_news(content,info)
	maps = gen_map(info)
	'''
	return response

def calcinfo(request):
	print("query calais info...")
	info = calais_info(request.session['content'])
	print("done")
	request.session['info'] = info
	response = HttpResponse(json.dumps({}, ensure_ascii = False),"application/json");
	return response
	
@csrf_exempt
def recommend(request):
	if "type" in request.POST and request.POST["type"]:
		type = request.POST["type"]
		print(type)
	#print(request.session['content'])
	l = rec_news(request.session['url'],request.session['info'],type)
	response = HttpResponse(json.dumps(l, ensure_ascii = False),"application/json");
	return response

def basicmap(request):
	markers = {}
	style = "<span style = 'color:#EF0FFF'>"
	style_end = "</span>"
	for item in request.session['info']['location']:
		if item['type'] == 'City' or item['type'] == 'ProvinceOrState':
			try:
				markers[item['name']] = {}
				markers[item['name']]['position'] = [item['latitude'],item['longitude']]
				markers[item['name']]['description'] = []
			except Exception as e:
				markers.pop(item['name'])
				continue
	sentences = tokenizer.tokenize(request.session['content'])
	for key in markers:
		for s in sentences:
			if key in s:
				markers[key]['description'].append(s.replace(key,style + key + style_end))
		markers[key]['description'] = "<br><br>".join(markers[key]['description'])
	response = HttpResponse(json.dumps(markers, ensure_ascii = False),"application/json");
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

def wordcloud(request):
	entity_tfidf = {}
	tag_weight = {}
	words = []
	print("counting word weight")
	for item in request.session['info']['socialTag']:
		if 'importance' in item:
			tag_weight[item['name']] = int(item['importance'])
		else:
			tag_weight[item['name']] = 2
	for item in request.session['info']['entity']:
		entity_tfidf[item['name']] = request.session['content'].lower().count(item['name'].lower())
		if entity_tfidf[item['name']] == 0:
			entity_tfidf[item['name']] = 1
	for key in entity_tfidf:
		if key in cs.entity_idf:
			entity_tfidf[key] = cs.entity_idf[key] * entity_tfidf[key]
		else:
			entity_tfidf[key] = cs.entity_idf['DEFAULT'] * entity_tfidf[key]
	print("done")
	e_weight = [(key,entity_tfidf[key]) for key in entity_tfidf]
	print("sorting")
	e_weight.sort(key=lambda k: k[1], reverse=True)
	maxw = e_weight[0][1]
	minw = e_weight[len(e_weight)-1][1]
	midw = e_weight[int(len(e_weight)/2)][1]
	for tag in tag_weight:
		if tag_weight[tag] == 1:
			entity_tfidf.setdefault(tag,maxw)
		elif tag_weight[tag] == 2:
			entity_tfidf.setdefault(tag,midw)
		elif tag_weight[tag] == 3:
			entity_tfidf.setdefault(tag,minw)
	for item in request.session['info']['topic']:
		entity_tfidf.setdefault(item['name'].replace('_',' '),midw)
	for key in entity_tfidf:
		words.append({'text':key, 'weight':pow(entity_tfidf[key],0.3)})
	words.sort(key=lambda k: k['weight'], reverse=True)
	print("done")
	response = HttpResponse(json.dumps(words, ensure_ascii = False),"application/json");
	return response

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

def thememap(request):
	tmaps = gen_map(request.session['info'])
	response = HttpResponse(json.dumps(tmaps, ensure_ascii = False),"application/json");
	return response

def gen_map(cinfo,fetch=2):
	maps = {}
	wn_stat = {} # (tf,[wikicats,...])
	spa = sparqlquerier()
	st = st_importance(cinfo)
	print("query wikicat...")
	wcdict = spa.wikicat(list(st.keys())) # wcdict[i["valueOrObject"]["value"]].append(tag) # each wikicat maps a list of socialTag
	print("done")
	wcset = set(wcdict.keys())
	for item in wcset:
		if item in mapdict.maps:
			maps[item] = mapdict.maps[item]
			maps[item]["score"] = []
			maps[item]["score"].append(1) # wikicat level
			maps[item]["score"].append(-1) # tfidf, wikicat does not have tfidf yet...
			maps[item]["score"].append(max([int(st[tag]) for tag in wcdict[item]])) # importance
			if item in stat.ontology:
				maps[item]["score"].append(stat.ontology[item]) # appearance count from corpus
		if item in stat.taxonomy:
			wn_stat.setdefault(stat.taxonomy[item],[0,[]])
			wn_stat[stat.taxonomy[item]][0] += 1
			wn_stat[stat.taxonomy[item]][1] += wcdict[item]
	for item in wn_stat:
		if item in mapdict.maps:
			maps[item] = mapdict.maps[item]
			maps[item]["score"] = []
			maps[item]["score"].append(0) # wikicat level
			if item in stat.wn_idf: # tfidf
				maps[item]["score"].append(wn_stat[item][0] * stat.wn_idf[item])
			else:
				maps[item]["score"].append(wn_stat[item][0] * stat.wn_idf["DEFAULT"])
			maps[item]["score"].append(max([int(st[tag]) for tag in wn_stat[item][1]])) # importance
			maps[item]["score"].append(-1) # appearance count, not needed with tf-idf
	to_rank = [maps[item] for item in maps]
	to_rank.sort(key=lambda k:(k["score"][0],k["score"][1],k["score"][2],k["score"][3]),reverse=True)
	return to_rank[:fetch]

def st_importance(info):
	st = {}
	for tag in info["socialTag"]:
		st[tag["name"]] = tag["importance"] # {"Obama Campaign 2012":2,...}
	return st