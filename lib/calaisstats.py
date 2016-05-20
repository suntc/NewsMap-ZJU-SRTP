'''
Created on 15 May 2016

@author Sun Tianchen
'''

'''
compute idf of socialTags, entity from corpus
build a dict as
{
	"tag1" : 12,
	"en1"	: 13,
	...
}
topic not included
'''
from math import log
import pickle
import psycopg2

class calais_stats:
	def __init__(self):
		try:
			inp = open("entity_idf.pickle","rb")
			self.entity_idf = pickle.load(inp)
			inp.close
		except FileNotFoundError as e:
			self.entity_idf = {}
		self.info = {}

	def load_db(self):
		conn = psycopg2.connect("dbname = newsCorpus user = postgres password = '123'")
		cur = conn.cursor()
		sql = """
			  select url,calais from newspaper
			  where (section = 'US news' or section = 'U.S.')
			  and calais is not null
			  """
		cur.execute(sql)
		fetchRes = cur.fetchall()
		for i in fetchRes:			
			self.info[i[0]] = eval(i[1])

	def calc_idf(self):
		for key in self.info:
			temp_set = []
			for item in self.info[key]["entity"]:
				temp_set.append(item["name"])
			for tag in set(temp_set):
				self.entity_idf.setdefault(tag,0)
				self.entity_idf[tag] += 1
		for key in self.entity_idf:
			self.entity_idf[key] = log(len(self.info) / (self.entity_idf[key] + 1),2)
		self.entity_idf["DEFAULT"] = log(len(self.info) / 2,2)

	def save(self):
		out = open("entity_idf.pickle","wb")
		pickle.dump(self.entity_idf,out)
		out.close()


if __name__ == '__main__':
	cs = calais_stats()
	cs.load_db()
	cs.calc_idf()
	cs.save()
	l = [(key,cs.entity_idf[key]) for key in cs.entity_idf]
	l.sort(key=lambda k:k[1], reverse=True)
	out = open("entityidf.txt","w")
	for i in l:
		print(i,file=out)
	out.close()