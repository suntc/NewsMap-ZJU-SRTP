'''
Created on 29th April
@Sun Tianchen
'''

from SPARQLWrapper import SPARQLWrapper, JSON
from queue import Queue
from threading import Thread
import multiprocessing
import logging
import psycopg2

conn = psycopg2.connect("dbname = newsCorpus user = postgres password = '123'")
cur = conn.cursor()

class sparqlquerier:
	def __init__(self):
		self.sparql = SPARQLWrapper("https://linkeddata1.calcul.u-psud.fr/sparql")
		self.sparql.setReturnFormat(JSON)
		self.baseq = '''
					select  *
					where {
					        <http://yago-knowledge.org/resource/%s> ?property ?valueOrObject .
					        FILTER regex(str(?property ), "^http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
					        FILTER regex(str(?valueOrObject ), "^http://yago-knowledge.org/resource/wikicat_")
					      } 
					LIMIT 100
					'''

	def query(self,name):
		name = "_".join(name.split())
		self.sparql.setQuery(self.baseq % (name))
		result = self.sparql.query().convert()
		return result

	def wikicat(self,socialtags):
		wcdict = {}
		for tag in socialtags:
			try:
				result = self.query(tag)
				result = result["results"]["bindings"]
			except Exception as e:
					print("query failed %s" % e)
					#logging.debug("query failed %s \n %s" % (e,result))
					continue
			for i in result:
				wcdict.setdefault(i["valueOrObject"]["value"],[])
				wcdict[i["valueOrObject"]["value"]].append(tag) # each wikicat maps a list of socialTag
		return wcdict

def write_db(url,item):
	seperator = '$@$'
	upd = '''
			update newspaper set wikicat = %s
			where url = %s
		  '''
	try:
		cur.execute(upd,(seperator.join(item),url))
		conn.commit()
	except Exception as e:
		print('write db failed: %s' % e)
		logging.debug('write db failed: %s' % e)
		conn.rollback()
		return
	return

def process_run(queue):
	spa = sparqlquerier()
	logging.basicConfig(filename='./log.txt',level=logging.DEBUG)
	while True:
			url, tags = queue.get()
			res = {}
			for name in tags:
				try:
					result = spa.query(name)
					result = result["results"]["bindings"]
				except Exception as e:
					print("query failed %s" % e)
					logging.debug("query failed %s \n %s" % (e,result))
					continue
				for i in result:
					res.setdefault(i["valueOrObject"]["value"],0)
					res[i["valueOrObject"]["value"]] += 1
			write_db(url,list(res.keys()))
			print("ok")


def main():
	processes = []
	queries = []
	queue = multiprocessing.Queue() #use multiprocessing's Queue() !!!
	sel = '''
			select url,calais from newspaper
			where calais is not null
		  '''
	cur.execute(sel)
	fetchRes = cur.fetchall()
	for item in fetchRes:
		url = item[0]
		social_tags = [item["name"] for item in eval(item[1])["socialTag"]]
		queue.put((url,social_tags))
	multi_process = 32
	for i in range(multi_process):
		process = multiprocessing.Process(target=process_run,args=(queue,)) 
		process.start()
		processes.append(process)
	for p in processes:
		p.join()

if __name__ == "__main__":
	main()