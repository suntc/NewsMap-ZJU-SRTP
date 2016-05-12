'''
Created on 26th April 2016
@Sun Tianchen
'''

'''
load structured information for sorting
get the sorted list of urls
'''

'''
select  *
where {
        <http://yago-knowledge.org/resource/Political_positions_of_Mitt_Romney> ?property ?valueOrObject .
        FILTER regex(str(?property ), "^http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
      } 
LIMIT 100
'''


import psycopg2
from similarity import infoSim

class recommender:
	def __init__(self):
		self.infodict_list = []
		self.ranks = {}
		self.target = {}
		self.prepared = False
		'''
		infodict_list contains dicts like {"url":,"calais_info":,"bog":,"location":,"entity":,"social_tag":,"topic":,...}
		'''
	def load_db(self):
		conn = psycopg2.connect("dbname = newsCorpus user = postgres password = '123'")
		cur = conn.cursor()
		sql = """
			  select url,calais from newspaper
			  where (section = 'US news' or section = 'U.S.')
			  and calais is not null
			  limit 8000
			  """
		cur.execute(sql)
		fetchRes = cur.fetchall()
		for i in fetchRes:
			info = {}
			info["url"] = i[0]
			info["calais_info"] = eval(i[1]) 
			self.infodict_list.append(info)
			self.ranks[info["url"]] = {}
		
	def load_target(self,target):
		self.target = target

	def score(self):
		'''
		calais information part
		'''
		simi = infoSim()
		for item in self.infodict_list:
			simi.load(self.target["calais_info"],item["calais_info"])
			item["location"] = simi.location()
			item["entity"] = simi.entity()
			item["social_tag"] = simi.social_tag()
			item["topic"] = simi.topic()

	def rank_by(self,key):
		self.infodict_list.sort(reverse=True,key=lambda k: k[key])
		rank = 0
		prevscore = -1
		for i, item in enumerate(self.infodict_list):
			if item[key] != prevscore:
				rank = i
				prevscore = item[key]
			self.ranks[item["url"]][key] = rank

	def general_rank(self,weight,fetch=None):
		'''
		weight should be a dict maps key to its weight
		{"entity":1,"topic":1,...}
		'''
		total_w = sum(weight.values())
		for url in self.ranks.keys():
			g_rank = 0
			for item in weight.keys():
				g_rank += float(self.ranks[url][item] * weight[item] / total_w)
			self.ranks[url]["general"] = g_rank
		rank_list = [(url,self.ranks[url]["general"]) for url in self.ranks.keys()]
		rank_list.sort(key=lambda k: k[1])
		if fetch is None:
			return rank_list
		else:
			return rank_list[:fetch]

	def prepare(self,url,calais_info):
		'''
		a generalized method, high coupling
		run once for each article
		'''
		t = {}
		t["url"] = url
		t["calais_info"] = calais_info
		self.load_target(t)
		self.score()
		self.rank_by("location")
		self.rank_by("entity")
		self.rank_by("social_tag")
		self.rank_by("topic")
		self.prepared = True

	def recommend(self,weight,fetch=20):
		'''
		a generalized method, high coupling
		should run self.prepare() first
		different results for different weight
		'''
		if not self.prepared:
			raise Exception("should run recommender.prepare(url,calais_info) first")
		import psycopg2
		import calendar
		res = self.general_rank(weight=weight,fetch=fetch) # tuples of (url,score)
		rec_urls = tuple([i[0] for i in res])
		rsql =	"""
			  	select url,calais,title,text,publish_date,source from newspaper
			  	where url in %s
			  	"""
		'''
		not enough!!!
		also require pub_date, title, (part) text...
		use split('\n') for cutting text?
		'''
		conn = psycopg2.connect("dbname = newsCorpus user = postgres password = '123'")
		cur = conn.cursor()
		cur.execute(rsql,(rec_urls,))
		fetchRes = cur.fetchall()
		rec_info = {}
		count = 0
		for item in fetchRes:
			url = item[0]
			calais_info = item[1]
			title = item[2]
			text = item[3]
			pub_date = item[4]
			source = item[5]
			rec_info[url] = {}
			rec_info[url]["calais_info"] = eval(calais_info)
			rec_info[url]["title"] = title
			rec_info[url]["text"] = ""
			text = text.split('\n')
			for p in text:
				if p != '':
					if count != 0:
						rec_info[url]["text"] += '\n'
					rec_info[url]["text"] += p
					count += 1
					if count == 3: # choose the first 3 paras as preview
						break
			if pub_date != None:
				rec_info[url]["pub_date"] = str(pub_date.date) + ' ' + calendar.month_abbr[pub_date.month] + ', ' + str(pub_date.year)
			if source != None:
				rec_info[url]["source"] = source
		rec_list = [rec_info[url] for url in rec_urls]
		return rec_list

def main():
	rec = recommender()
	rec.load_db()
	print("end load")
	t = {}
	t["url"] = "test"
	t["calais_info"] = {'socialTag': [{'name': '112th United States Congress', 'importance': '2'}, {'name': 'Fiscal conservatism', 'importance': '2'}, {'name': 'Bush tax cuts', 'importance': '2'}, {'name': 'Paul Ryan', 'importance': '1'}, {'name': 'Fiscal policy', 'importance': '1'}, {'name': 'The Path to Prosperity', 'importance': '1'}, {'name': 'United States House of Representatives', 'importance': '2'}, {'name': 'Presidency of Barack Obama', 'importance': '2'}, {'name': 'Republican Party', 'importance': '2'}, {'name': 'Mitt Romney', 'importance': '2'}, {'name': 'United States fiscal cliff', 'importance': '2'}], 'entity': [{'relevance': 0.2, 'type': 'Position', 'name': 'Republican House majority leader'}, {'relevance': 0.2, 'type': 'Person', 'name': 'Jay Carney', 'persontype': 'political', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'Position', 'name': 'unanimously rejected president'}, {'relevance': 0.2, 'type': 'Person', 'name': 'Barack Obama', 'persontype': 'political', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'Position', 'name': 'President'}, {'relevance': 0.2, 'type': 'Organization', 'name': 'Congress', 'organizationtype': 'governmental civilian', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'Organization', 'name': 'Medicare', 'organizationtype': 'governmental civilian', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'Person', 'name': 'Eric Cantor', 'persontype': 'N/A', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'Organization', 'name': 'House of Representatives', 'organizationtype': 'governmental civilian', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'Organization', 'name': 'Senate', 'organizationtype': 'governmental civilian', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'IndustryTerm', 'name': 'oil'}, {'relevance': 0.2, 'type': 'Person', 'name': 'Paul Ryan', 'persontype': 'N/A', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'Position', 'name': 'politician'}, {'relevance': 0.2, 'type': 'PoliticalEvent', 'name': 'House vote'}, {'relevance': 0.2, 'type': 'Position', 'name': 'press secretary'}, {'relevance': 0.2, 'type': 'Organization', 'name': 'White House', 'organizationtype': 'governmental civilian', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'Person', 'name': 'Mitt Romney', 'persontype': 'sports', 'nationality': 'N/A'}, {'relevance': 0.2, 'type': 'PoliticalEvent', 'name': 'congressional elections'}, {'relevance': 0.2, 'type': 'IndustryTerm', 'name': 'clean energy programmes'}], 'location': [{'relevance': 0.2, 'type': 'Country', 'longitude': -98.7372244786, 'name': 'United States', 'latitude': 40.4230003233}, {'relevance': 0.2, 'type': 'Continent', 'name': 'America'}, {'relevance': 0.2, 'type': 'City', 'longitude': -77.03, 'latitude': 38.89, 'name': 'Washington', 'containedbycountry': 'United States'}], 'topic': [{'name': 'Business_Finance', 'score': 0.907}, {'name': 'Politics', 'score': 1}, {'name': 'Social Issues', 'score': 0.987}]}
	rec.load_target(t)
	rec.score()
	rec.rank_by("location")
	rec.rank_by("entity")
	rec.rank_by("social_tag")
	rec.rank_by("topic")
	w = {"location":1,"entity":0.8,"social_tag":1.2,"topic":1}
	res = rec.general_rank(weight=w,fetch=100)
	print("ok")
	urls = tuple([i[0] for i in res])
	rsql = """
			  select url,calais from newspaper
			  where url in %s
			  """
	conn = psycopg2.connect("dbname = newsCorpus user = postgres password = '123'")
	cur = conn.cursor()
	cur.execute(rsql,(urls,))
	fetchRes = cur.fetchall()
	#for i in fetchRes:
		#print(i)
	
if __name__ == '__main__':
	pass
	#main()