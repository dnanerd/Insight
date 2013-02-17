#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
import pickle
from mrjob.job import MRJob
import networkx as nx


class MRWordCounter(MRJob):

	G = pickle.load(open("defaultGFile.pickle"))
	recipeSizes = pickle.load(open("defaultRecipeLengths.pickle"))

	def mapper(self, key, ingr):
		recipes = MRWordCounter.G.neighbors(ingr)
		for i, recipe1 in enumerate(recipes):
			for j, recipe2 in enumerate(recipes):
				if i>=j: continue
				yield recipe1 + "," + recipe2, 1

	def reducer(self, recipepair, occurrences):
		(recipe1, recipe2) = recipepair.split(",")
		recipe1size = MRWordCounter.recipeSizes[recipe1]
		recipe2size = MRWordCounter.recipeSizes[recipe2]
		intersection = sum(occurrences)
		if (intersection>0):
			jaccard = float(intersection)/float(recipe1size+recipe2size-2*intersection)
			yield recipepair, jaccard
		else:
			yield recipepair, 0
#		yield recipepair, sum(occurrences)

if __name__ == '__main__':
	MRWordCounter.run()