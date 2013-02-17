import sys
from multiprocessing import Pool
"""
If a token has been identified to contain
non-alphanumeric characters, such as punctuation,
assume it is leading or trailing punctuation
and trim them off. Other internal punctuation
is left intact.
"""
def sanitize(w):

  # Strip punctuation from the front
  while len(w) > 0 and not w[0].isalnum():
    w = w[1:]

  # String punctuation from the back
  while len(w) > 0 and not w[-1].isalnum():
    w = w[:-1]

  return w
"""
Load the contents the file at the given
path into a big string and return it.
"""
def load(path):

  word_list = []
  f = open(path, "r")
  for line in f:
    word_list.append (line)

  # Efficiently concatenate Python string objects
  return (''.join(word_list)).split ()

"""
A generator function for chopping up a given list into chunks of
length n.
"""
def chunks(l, n):
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

"""
Sort tuples by term frequency, and then alphabetically.
"""
def tuple_sort (a, b):
  if a[1] < b[1]:
    return 1
  elif a[1] > b[1]:
    return -1
  else:
    return cmp(a[0], b[0])

if __name__ == '__main__':

  if (len(sys.argv) != 2):
    print "Program requires path to file for reading!"
    sys.exit(1)

  # Load file, stuff it into a string
  text = load (sys.argv[1])

  # Build a pool of 8 processes
  pool = Pool(processes=8,)

  # Fragment the string data into 8 chunks
  partitioned_text = list(chunks(text, len(text) / 8))

  # Generate count tuples for title-cased tokens
  single_count_tuples = pool.map(Map, partitioned_text)

  # Organize the count tuples; lists of tuples by token key
  token_to_tuples = Partition(single_count_tuples)

  # Collapse the lists of tuples into total term frequencies
  term_frequencies = pool.map(Reduce, token_to_tuples.items())

  # Sort the term frequencies in nonincreasing order
  term_frequencies.sort (tuple_sort)

  for pair in term_frequencies[:20]:
    print pair[0], ":", pair[1]
