'''
Created on 18th April
@Sun Tianchen
'''

import requests
from io import StringIO
import ast
import psycopg2
from queue import Queue
from threading import Thread
import logging

'''
tokens:
hOtCOmaV48bRp2EIzm2LGbyhQb3X3UtS
vtIqbK0R5RAxVattP4B9Z5vs3D9jdG9y
lmBG3iqtVxnsKFpoWTXGazCBhofMvggm
xQQhddvfbUH29MxoiqJAL5LtFm3ZFbpG
DeRzIdMG3119PIL6ZfzC5gzSpDxVkiNs
E8uWJ7Llhmm3cejGKlhdvtuP4WuZtgo2
GljSaVOJRvGhYqAN33R5OIhX51CDM2xw
AzZQGXvFTF3rFY2z21X7C5yOj0pKNpw3
PVxlx1hGkue44shPPWFHTKRzTeJeHqGK
1J0aaL7GqSJtBbU5o5iKSXBntvR8kn6r
3nn2FzAVBEVkbYesSUNRAwtonRDeIG3C
3Sx7TpI9kDe6GWq86Bd9lBBVANgftbRV
iiAVGbGN4ujY4bMgtv55YbAg88XwMlxT
'''

api_keys = ("hOtCOmaV48bRp2EIzm2LGbyhQb3X3UtS","vtIqbK0R5RAxVattP4B9Z5vs3D9jdG9y","lmBG3iqtVxnsKFpoWTXGazCBhofMvggm",
	"xQQhddvfbUH29MxoiqJAL5LtFm3ZFbpG","DeRzIdMG3119PIL6ZfzC5gzSpDxVkiNs","E8uWJ7Llhmm3cejGKlhdvtuP4WuZtgo2",
	"GljSaVOJRvGhYqAN33R5OIhX51CDM2xw","AzZQGXvFTF3rFY2z21X7C5yOj0pKNpw3","PVxlx1hGkue44shPPWFHTKRzTeJeHqGK",
	"1J0aaL7GqSJtBbU5o5iKSXBntvR8kn6r","3nn2FzAVBEVkbYesSUNRAwtonRDeIG3C","3Sx7TpI9kDe6GWq86Bd9lBBVANgftbRV",
	"iiAVGbGN4ujY4bMgtv55YbAg88XwMlxT")

conn  = psycopg2.connect("dbname = newsCorpus user = postgres password = '123'");
cur   = conn.cursor();

class calais_api:
	def __init__(self):
		self.calais_url = 'https://api.thomsonreuters.com/permid/calais'
		self.set_token("hOtCOmaV48bRp2EIzm2LGbyhQb3X3UtS")
		self.proxy = {
		'http': 'http://127.0.0.1:8118',
		'https': 'http://127.0.0.1:8118',}

	def set_token(self,token):
		self.access_token = token
		self.headers = {'X-AG-Access-Token' : self.access_token, 'Content-Type' : 'text/raw',
		 'outputformat' : 'application/json' , 'x-calais-language' : 'english'}

	def query(self, content):
		files = {'file': StringIO(content)}
		response = requests.post(self.calais_url, files=files, headers=self.headers, timeout=80, proxies=self.proxy)
		#print 'status code: %s' % response.status_code
		json_result = response.json()
		return json_result

	def filter(self,jresult):
		'''
		the structure of tags and entities

		-socialTag
			-name (originalValue)
			-importance
		-topic
			-name
			-score
		-location
			-type
				-("City","ProvinceOrState","Country","Continent","Region")
			-name
			-relevance
			-latitude(?"City","ProvinceOrState","Country")
			-longitude(?"City","ProvinceOrState","Country")
			-containedbystate(?"City","ProvinceOrState")
			-containedbycountry(?"City","ProvinceOrState")
		-entity
			-type
				-("Company","Organization","Person")
			-name
			-relevance
			-nationality(?)
			-organizationtype(?)
			-persontype(?)
		-misc
			-type
				-("Currency","EmailAddress","FaxNumber","MarketIndex","NaturalFeature","PhoneNumber","URL")
			-name

		'''
		#_typeGroup = socialTag, entities
		info = {"socialTag":[], "topic":[], "entity":[], "location":[]}
		for key in jresult:
			if "_typeGroup" in jresult[key]:#tag or entity
				tgroup = jresult[key]["_typeGroup"]
			else:
				continue
			if tgroup == "socialTag":
				st = {}
				st["name"] = jresult[key]["originalValue"] # use original value instead of name for later query
				st["importance"] = jresult[key]["importance"]
				info["socialTag"].append(st)
			elif tgroup == "entities":
				if jresult[key]["_type"] in ("City","Country","ProvinceOrState","Continent","Region"):
					lc = {}
					lc["type"] = jresult[key]["_type"]
					lc["name"] = jresult[key]["name"]
					lc["relevance"] = jresult[key]["relevance"]
					if "resolutions" in jresult[key].keys():
						#resolusions is a list containing only one object
						#print(jresult[key]["resolutions"])
						if "latitude" in jresult[key]["resolutions"][0] and "longitude" in jresult[key]["resolutions"][0]:
							lc["latitude"] = float(jresult[key]["resolutions"][0]["latitude"])
							lc["longitude"] = float(jresult[key]["resolutions"][0]["longitude"])
						if "containedbystate" in jresult[key]["resolutions"][0].keys():
							lc["containedbystate"] = jresult[key]["resolutions"][0]["containedbystate"]
						if "containedbycountry" in jresult[key]["resolutions"][0].keys():
							lc["containedbycountry"] = jresult[key]["resolutions"][0]["containedbycountry"]
					info["location"].append(lc)
				else:#not location, Organization:..., 
					ent = {}
					ent["type"] = jresult[key]["_type"]
					ent["name"] = jresult[key]["name"]
					ent["relevance"] = jresult[key]["relevance"]
					if "nationality" in jresult[key].keys():
						ent["nationality"] = jresult[key]["nationality"]
					if "organizationtype" in jresult[key].keys():
						ent["organizationtype"] = jresult[key]["organizationtype"]
					if "persontype" in jresult[key].keys():
						ent["persontype"] = jresult[key]["persontype"]						
					info["entity"].append(ent)
			elif tgroup == "topics":
				tp = {}
				tp["name"] = jresult[key]["name"]
				tp["score"] = jresult[key]["score"]
				info["topic"].append(tp)
		return info

def write_db(url,value):
	sql = """
		  update newspaper
		  set (calais)
		  = (%s)
		  where url = %s
		  and calais is null
	      """
	try:
		cur.execute(sql,(value,url))
		conn.commit()
	except Exception as e:
		print('write db failed: %s' % e)
		conn.rollback()
		return
	return

class thread_task(Thread):
	def __init__(self,queue):
		Thread.__init__(self)
		self.queue = queue
		self.cls = calais_api()
		#logging.basicConfig(filename='./log.txt',level=logging.DEBUG)

	def run(self):
		while True:
			uid, text, key = self.queue.get()
			#logging.debug("url = %s" % (uid))
			try:
				self.cls.set_token(key)
				result = self.cls.query(text)
				info = str(self.cls.filter(result))
				print("ok")
				#logging.debug("ok")
				#print(info)
			except Exception as e:
				print("query failed %s" % e)
				#logging.debug("query failed %s" % (e))
				continue
			write_db(uid,info)

def main():
	#logging.basicConfig(filename='./log.txt',level=logging.DEBUG)
	#logging.debug('start')
	multi_thread = 15
	queries = []
	sel = """
		  select url, text from newspaper
		  where (section = 'US news' or section = 'U.S.')
		  and calais is null
		  """
	cur.execute(sel)
	fetchRes = cur.fetchall()
	for i, item in enumerate(fetchRes):
		key=api_keys[i%len(api_keys)]
		queries.append((item[0],item[1],key))
	queue = Queue()
	for i in range(multi_thread):
		task = thread_task(queue)
		#task.daemon = True
		task.start()
	for p in queries:
		queue.put(p)
	queue.join()

if __name__ == '__main__':
	main()
	#ca = calais_api()
	#js = ca.query(text)
	#f = ca.filter(js)
	#print(f)