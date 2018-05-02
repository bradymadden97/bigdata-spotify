import pickle
import copy
import sys
import re
import random


def lyrics(g):
	ignore = ["\xc3","\x8e","\xc2","\xa4","\xad","\x8f","\x81","\xbc","\xb1","\xb7","\xb3","\xac","\x80","\xbd","\xb6","\xb5","\xb9","\x82"]
	if g == "pop":
		generator = pickle.load( open( "generators/pop.gen", "rb" ))
	elif g == "hiphop":
		generator = pickle.load( open( "generators/hiphop.gen", "rb" ))
	elif g == "metal":
		generator = pickle.load( open( "generators/metal.gen", "rb" ))
	elif g == "country":
		generator = pickle.load( open( "generators/country.gen", "rb" ))
	else:
		return None, 1
    
	while True:
		line = generator.generate(1, 'b', Generator.special + ignore, [])
		if len(line[0]) > 15:
			break
	return line[0], None
	

class Distribution(dict):
	"""a very simple class which represents a probability distribution
	   subclasses Dict, so can be used easily.

	   The count field is used by corpus to keep track of type counts."""
	def __init__(self, count=0.0, *dict_args):
		dict.__init__(self, *dict_args)
		self.count = count

		# include unknown token w/ count of 0
		self['<unk>'] = 0.0


	def add(self, key):
		if key not in self:
			self[key] = 1.0
		else:
			self[key] += 1

	def add(self, key, k):
		if key not in self:
			self[key] = 1.0 + k
		else:
			self[key] += 1


	def total_counts(self):
		return sum(self.values())

	def __iadd__(self, other):
		self.count += other
		return self

	@classmethod
	def from_dict(cls, d):
		""" create a Distribution from a dict """
		for k,v in d.items():
			assert type(v) == float, "Values in d must be ints"
			assert type(k) == str, "Keys in d must be strings"

		dist = Distribution()
		for key, value in d.items():
			dist[key] = value
		return dist


class Corpus(object):
	"""a class which represents unigrams and bigrams extracted from a corpus.
	   Consists of a dictionary whose keys are types, and whose values are
	   a Distribution of following (subsequent) types.
	   """
	def __init__(self, k = None):
		""" returns an empty corpus """
		self._types = {'<unk>': Distribution()}
		self.vocab_size = 0.0
		self.token_num = 0.0
		if k == None:
			self.k = 0.0055
		else:
			self.k = k


	def __len__(self):
		""" return the length of the vocabulary """
		return len(self._types)

	def __str__(self):
		""" pretty-printable representation """
		title = "Corpus with {} unique words:".format(len(self))
		title += ('\n' + len(title)*'-' + '\n')

		for word, dist in self._types.items():
			title += '{:<20}{:>4}|{}\n'.format(word, dist.count, dist)
		return title

	def unigram(self):
		return { word : dist.count for word, dist in self._types.items()}

	def bigram(self, token):
		""" returns the <unk> distribution if we haven't seen this token """
		token = token if token in self._types else '<unk>'
		return copy.deepcopy(self._types[token])

	def add_unigram(self, token):
		''' returns True if token is new, False otherwise '''
		self.token_num += 1

		if token not in self._types:
			# create an entry in self._types so we know we've seen it for next time
			self._types[token] = Distribution()
			self._types[token].count += 1.0 # increment count of token
			self.vocab_size += 1
			return False
		elif self._types[token].count > 1.0:
			self._types[token].count += 1.0
			return False
		elif self._types[token].count == 1.0:
			#treat as unknown if it is second occurence of token
			self._types['<unk>'].count += 1.0 # increment count of <unk>
			self._types[token].count += 0.000000000000001
			return True


	def add_bigram(self, token1, token2):
		''' add a bigram to the corpus.
			token1 is the first token in the bigram
			token2 is the second token '''
		# we should add token2 to <unk> if token1 is new, otherwise we can
		# add it to token1

		add_to = '<unk>' if self.add_unigram(token1) else token1

		if token2 in self._types and self._types[token2].count == 1.0:
			self._types[add_to].add('<unk>', self.k)
		else:
			self._types[add_to].add(token2, self.k)
		return

	@classmethod
	def from_file(cls, file_path, k = None):
		''' create a Corpus from a file '''
		if k == None:
			corpus = Corpus()
		else:
			corpus = Corpus(k)
		with open(file_path, 'r') as f:
			tokens = f.read().split() # spliting on any whitespace

			# subtract one so we skip the last token, which isn't a bigram
			# iterate over tokens with window of size 2
			for idx in range(len(tokens)-1): corpus.add_bigram(tokens[idx], tokens[idx+1])
		return corpus

	@classmethod
	def from_string(cls, s, k = None):
		if k == None:
			corpus = Corpus()
		else:
			corpus = Corpus(k)

		tokens = re.findall(r'\S+|\n',s) # spliting on any whitespace
		for idx in range(len(tokens)-1): corpus.add_bigram(tokens[idx], tokens[idx+1])
		return corpus	
	
class Generator(object): 
    
	# Class attribute
	punctuation = [".", ",", ";", ":", "?", "...", "!"]
	special = ["<unk>"]
	
	def __init__(self, s, line):
		self.end_tokens = [".", "!", "?", "<END>"]
		self.cps = Corpus.from_string(s)
		self.ug = self.cps.unigram()
		if line:
			self.end_tokens += "\n"
    
	def select_word(self, dist, ignore, n):
		""" Selects a word from a given distribution using its weight
		Arguments: 
		dist: the distribution as a dictionary
		ignore (optional): list of tokens to be ignored, leave empty if unused
		n: the sum of all non-ignored counts in the distribution, require n>0
		"""
		n = int(n)

		if n < 1:
			# Should fail here
			pass
		word = '<unk>'
		r = random.randint(1, n)
		for key in dist:
			if (not key in ignore):
				r -= dist[key]
				if r <= 0:
					return key
		return word
	
	
	def generate(self, n, mode, ignore, sentences):
		""" Arguments:
		n: The number of sentences to generate
		mode: either 'u' or 'b' for unigram or bigram based generation
		ignore (optional): a list of tokens to ignore
		sentences (optional): a list of sentence stems (e.g. ["The world was"]),
		if present, the generator will complete the sentence stems instead of
		generating new sentences. If the stems are the empty string or the list
		is empty, up to n completely new sentences will be generated instead
		Returns an array of randomly generated sentences 
		"""
		if n <= 0 or (mode != 'u' and mode != 'b'):
			return []
			
		for i in range(n):
			# Use the last word in the sentence stem to proceed with generation
			if len(sentences) > i and sentences[i] != "":
				word = sentences[i].split()[-1]
			# Or get the first word from the unigram distribution if no sentence stems available
			else:
				ugTotal = 0
			for key in self.ug:
				if not key in Generator.punctuation + ignore:    
					ugTotal += self.ug[key]
				word = self.select_word(self.ug, Generator.punctuation + ignore, ugTotal)
				if len(sentences) <= (i+1):
					sentences.append(word)
				else:
					sentences[i] = word
				
			# generate a sentence, using the end_tokens for termination
			while not word in self.end_tokens:
				if mode == 'u':
					#  Unigram generation
					word = self.select_word(self.ug, ignore, ugTotal)
				else:  
					# Get the bigram distribution and counts
					bg = self.cps.bigram(word)
					total = 0
					for key in bg:
						if not key in ignore:
							total += bg[key]
							
						# Terminate the sentence if there are no non-ignored tokens in the bigram
					if total == 0:
						sentences[i] += " . "
						break
					
					word = self.select_word(bg, ignore, total)
					
				sentences[i] += " " + word
			
		return sentences