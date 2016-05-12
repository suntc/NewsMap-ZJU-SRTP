'''
Created on 2016-05-04

@Sun Tianchen
'''

import pickle

'''
define a standard(?) mapinfo type
{
	"type": "heat" / "sizedot" / "marker",
	"data": {
		"boundary": []
		"points": []	
	}
}

'''

class mapdict:
	'''
	create dict mapping wikicat/wncat with mapjson
	as a preparation for the news view program
	'''
	def __init__(self):
		self.taxonomy = {}
		try:
			inp = open("thememaps.pkl","rb")
			self.maps = pickle.load(inp)
			inp.close()
		except FileNotFoundError as e:
			self.maps = {}

	def load_tax(self):
		inp = open("taxonomy.pkl","rb")
		taxonomy = pickle.load(inp)
		inp.close()

	def add_cat(self,cat,minfo):
		self.maps[cat] = minfo

	def save(self):
		out = open("thememaps.pkl","wb")
		pickle.dump(self.maps,out)
		out.close()
		