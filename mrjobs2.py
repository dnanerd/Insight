#!/Users/apple/Desktop/Work/Scripts/Insight/venv/bin/python

#import pymongo #==2.4.2
from mrjob.job import MRJob


class MRWordCounter(MRJob):


	def mapper(self, key, line):
		(recipeLine1, recipeLine2) = line.split(" ; ")
		(rid1, ingredientLine1) = recipeLine1.split(" : ")
		(rid2, ingredientLine2) = recipeLine2.split(" : ")
		ingr1 = ingredientLine1.split(",")
		ingr2 = ingredientLine2.split(",")
		intersection = list(set(ingredientLine1) & set(ingredientLine2))
		union = list(set(ingredientLine1) | set(ingredientLine2))
		if (union):
			yield rid1+","+rid2, float(len(intersection))/float(len(union))

if __name__ == '__main__':
	MRWordCounter.run()