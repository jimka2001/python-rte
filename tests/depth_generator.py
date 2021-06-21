import random
import math

from genus.s_top import STop
from genus.s_empty import SEmpty
from genus.s_custom import SCustom
from genus.s_and import SAnd
from genus.s_or import SOr
from genus.s_not import SNot

class depth_generator(object):
	"""docstring for depth_generator"""

	depth_adders = ["SNot", "SAnd", "SOr"]
	leaves = ["SCustom", "STop", "SEmpty"]

	def __init__(self, k):
		if k < 1:
			raise ValueError("Depth has to be of at least 1")
		super(depth_generator, self).__init__()
		self.k = k

	def rand_lambda_str_generator(self):
		rand_k = random.randint(1, math.pow(2, self.k))
		return (lambda x : x % rand_k == 0, "mod"+str(rand_k))

	def _generate_tree(self, c):
		curr_depth = c - 1
		if curr_depth == 0:
			rand_choice = random.choice(self.leaves)
			if rand_choice == "SCustom":
				oracle, printable = self.rand_lambda_str_generator()
				return SCustom(oracle, printable)
			elif rand_choice == "STop":
				return STop.get_omega()
			else:
				return SEmpty.get_epsilon()
		else:
			rand_choice = random.choice(self.depth_adders)
			if rand_choice == "SNot":
				return SNot.create(self._generate_tree(curr_depth))
			else:
				rand_k = random.randint(0, 3)
				tds = [self._generate_tree(curr_depth) for i in range(rand_k)]
				return SAnd(tds) if rand_choice == "SAnd" else SOr(tds)

	def generate_tree(self):
		return self._generate_tree(self.k)
		
rand_lambda = depth_generator(2).rand_lambda_str_generator()
for i in range(10):
	print(rand_lambda[0](i))

tree = depth_generator(5).generate_tree()
print(tree)
