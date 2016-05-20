'''
Created on 2016-05-01
@Sun Tianchen
'''

from math import log
import psycopg2
import pickle
from newspaper import Article
from wikicat import sparqlquerier
from buildcalais import calais_api

'''
count the most frequent wikicat and the leaf level of wordnet cat
ontology : dict that maps wikicat/wncat with count
'''

class ontstats:
	def __init__(self):
		self.wikicatdict = {}
		self.ontology = {}
		self.wn = {}
		self.taxonomy = None
		self.wn_idf = {}
		self.docsize = 0

	def load(self):
		
		conn = psycopg2.connect("dbname = newsCorpus user = postgres password = '123'")
		cur = conn.cursor()
		sql =	"""
			select wikicat from newspaper
			where wikicat is not null
			"""
		inp = open("taxonomy.pkl","rb")
		self.taxonomy = pickle.load(inp)
		inp.close()
		seperator = "$@$"
		cur.execute(sql)
		fetchRes = cur.fetchall()
		print("finish db")
		self.docsize = len(fetchRes)
		for item in fetchRes:
			for key in item[0].split(seperator):
				self.wikicatdict.setdefault(key,0)
				self.wikicatdict[key] += 1
			temp_wn = []
			for key in item[0].split(seperator):
				if key in self.taxonomy:
					temp_wn.append(self.taxonomy[key])
			for wn in set(temp_wn):
				self.wn_idf.setdefault(wn,0)
				self.wn_idf[wn] += 1
		for key in self.wn_idf:
			self.wn_idf[key] = log(self.docsize/(self.wn_idf[key]+1),2)
		self.wn_idf["DEFAULT"] = log(self.docsize,2)
		self.ontology = self.wikicatdict
		for key in self.ontology:
			if key in self.taxonomy:
				self.wn.setdefault(self.taxonomy[key],0)
				self.wn[self.taxonomy[key]] += 1
		self.ontology.update(self.wn)

	def has_person_parent(self,key):
		person = "http://yago-knowledge.org/resource/wordnet_person_100007846"
		area = "http://yago-knowledge.org/resource/wordnet_geographical_area_108574314"
		if key == person or key == area:
			return True
		if key in self.taxonomy:
			return has_person_parent(self.taxonomy[key])

	def st_importance(self,info):
		st = {}
		for tag in info["socialTag"]:
			st[tag["name"]] = tag["importance"] # {"Obama Campaign 2012":2,...}
		return st

	def text_static(self,url):
		article = Article(url)
		article.download()
		article.parse()
		#return (article.title,article.text,article.publish_date,article.top_image)
		cls = calais_api()
		result = cls.query(article.text)
		cinfo = cls.filter(result) # dict: info = {"socialTag":[], "topic":[], "entity":[], "location":[]}
		spa = sparqlquerier()
		st = self.st_importance(cinfo)
		wcdict = spa.wikicat(list(st.keys()))
		print(st.keys())
		wcrank_info = {}
		for cat in wcdict:
			if cat in self.ontology:
				wcrank_info[cat] = []
				wcrank_info[cat].append(1) # wikicat level
				wcrank_info[cat].append(max([st[tag] for tag in wcdict[cat]]))
				wcrank_info[cat].append(self.ontology[cat])
		to_rank = [[key,wcrank_info[key][0],wcrank_info[key][1],wcrank_info[key][2]] for key in wcrank_info]
		to_rank.sort(key=lambda k:(k[1],k[2],k[3]),reverse=True)
		for item in to_rank:
			print(item)
			print(wcdict[item[0]])
			if item[0] in self.taxonomy:
				print(self.taxonomy[item[0]])
			print("----------------------")



def main():
	stats = ontstats()
	stats.load()
	print(stats.wn_idf)
	wnidflist = [(stats.wn_idf[k],k) for k in stats.wn_idf]
	wnidflist.sort(key=lambda k:k[0],reverse=True)
	op = open("wnidflist.txt","w")
	for item in wnidflist:
		print(item,file=op)
	op.close()
	
	'''
	conn = psycopg2.connect("dbname = newsCorpus user = postgres password = '123'")
	cur = conn.cursor()
	sql =	"""
			select wikicat from newspaper
			where wikicat is not null
			"""
	seperator = "$@$"
	wikicatdict = {}
	wn = {}
	cur.execute(sql)
	fetchRes = cur.fetchall()
	print("finish db")
	for item in fetchRes:
		for key in item[0].split(seperator):
			wikicatdict.setdefault(key,0)
			wikicatdict[key] += 1
	inp = open("taxonomy.pkl","rb")
	taxonomy = pickle.load(inp)
	inp.close()
	ontology = wikicatdict
	for key in ontology:
		if key in taxonomy:
			wn.setdefault(taxonomy[key],0)
			wn[taxonomy[key]] += 1
	ontology.update(wn)
	clist = [(k,ontology[k]) for k in ontology]
	clist.sort(key=lambda k: k[1],reverse=True)
	wnlist = [(k,wn[k]) for k in wn]
	wnlist.sort(key=lambda k: k[1],reverse=True)
	
	text_static(text)
	'''

	'''
	count = 0
	many = []
	sons = {}
	output = open("statistics.txt","w")
	for item in wnlist:
		if not has_person_parent(item[0]):
			#print(item)
			many.append(item[0])
			count += 1
		if count > 30:
			break
	for key in ontology:
		if key in taxonomy and taxonomy[key] in many:
			sons.setdefault(taxonomy[key],[])
			sons[taxonomy[key]].append((key,ontology[key]))
	for w in many:
		sons[w].sort(key=lambda k: k[1],reverse=True)
		print((w + " " + str(wn[w])).encode('utf8'))
		print((w + " " + str(wn[w])).encode('utf8'),file=output)
		for item in sons[w]:# item is like (wikicatxxx,812)
			print(("    " + item[0] + " " + str(item[1])).encode('utf8'),file=output)

	'''

	'''
	for item in clist:
		if not has_person_parent(item[0]):
			print(item)
			count += 1
		if count > 100:
			break
	'''
if __name__ == '__main__':
	main()