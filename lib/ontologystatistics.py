'''
Created on 2016-05-01
@Sun Tianchen
'''

from math import log
import psycopg2
import pickle
from wikicat import sparqlquerier
from buildcalais import calais_api

'''
count the most frequent wikicat and the leaf level of wordnet cat
ontology : dict that maps wikicat/wncat with count
'''

text = '''
Every minute of every day, usually without thinking, thousands of New Yorkers reach across the counter at shops and supermarkets and accept a disposable plastic bag. The city's sanitation department estimates 10 billion bags a year are tossed in the trash — roughly 19,000 per minute.
Now, city officials are poised to test whether a 5-cent charge can wean New Yorkers from the convenient but environmentally unfriendly sacks.
City Council approved a bill by a 28-20 vote Thursday afternoon that would require most merchants to charge customers at least a nickel for each bag, including those made of paper. Technically, the fee isn't a tax. Stores will get to keep the money they collect.
Mayor Bill de Blasio, who has a goal of sending zero waste to landfills by 2030, said he will sign the bill, which would take effect Oct. 1. He said the legislation "strikes the right balance, reducing reliance on single-use bags and incentivizing the use of reusable bags."
Supporters are hoping the extra charge will force New Yorkers to think twice about accepting a bag and perhaps start bringing their own. And that, they say, might help keep the bags from filling landfills and blowing into trees and waterways — as they do constantly in the city today.
Some New Yorkers interviewed as they ran errands this week said they weren't so sure how they would adapt, especially in a city where most people are shopping on foot rather than by car.
"A lot of times I leave work, if I'm on the way home, I don't have time to have a bag with me," said Pat Tomasso, 70, who has a neon sign business.
Todd Killinger, 47, who works in advertising, said it's a good idea.
"After a time I think people will switch and bring their own bags but initially not so much," he said.
New York City joins more than 150 other municipalities around the country that have passed ordinances either to ban single-use plastic bags or to charge a fee for them.
Puerto Rico's governor signed an order banning plastic bags last fall. There is now a 5-pence charge in Great Britain.
Officials from Washington, D.C., testified at a New York City Council hearing that their 5-cent bag fee, enacted in 2009, has led to a 60 percent drop in bag use.
Former New York Mayor Michael Bloomberg first proposed a plastic bag charge in 2008, but the idea failed to attract support from the City Council. The current bill was introduced in 2014 and has been amended to slash the per-bag fee from 10 cents to 5.
"Everyone knows that plastic bags are a problem," said Councilman Brad Lander, a Brooklyn Democrat and bill sponsor. "They blow everywhere. They never biodegrade. They're made of petroleum. And we don't need them."
Opponents say the fee essentially amounts to a new tax on a heavily taxed population.
"I'm tired of my constituents being nickeled-and-dimed all the time," said Councilman Steven Matteo, a Staten Island Republican who planned to vote against the bag fee. "It's going to give my constituents another reason to shop in New Jersey."
According to the Sanitation Department, New York City spends $12.5 million a year to send plastic bags to landfills and even more to clean them off beaches, parks and other public spaces.
Lee Califf, executive director of the American Progressive Bag Alliance, accused the City Council of "imposing a new, regressive grocery bag tax that will hurt seniors, working class and low-income New Yorkers while enriching grocers."
The law will go into effect Oct. 1.
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

	def text_static(self,text):
		cls = calais_api()
		result = cls.query(text)
		cinfo = cls.filter(result) # dict: info = {"socialTag":[], "topic":[], "entity":[], "location":[]}
		spa = sparqlquerier()
		st = self.st_importance(cinfo)
		wcdict = spa.wikicat(list(st.keys()))
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