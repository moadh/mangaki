from django.core.management.base import BaseCommand, CommandError

import os
import json
from mangaki.utils.values import tags_definition
from math import floor
import numpy as np
from mangaki.settings import DATA_DIR

posters = json.load(open(os.path.join(DATA_DIR, 'mangaki_i2v.json')))
nb_tags = len(tags_definition)
index_posters = [.0] * len(posters)
i = 0
for poster in posters:
	index = int(poster[:len(poster)-4])
	index_posters[i] = index
	i += 1
poster_tags = np.zeros((max(index_posters)+1, nb_tags))
for poster in posters:
	index = int(poster[:len(poster)-4])
	for tag, value in posters[poster]['general']:
		poster_tags[index][tags_definition[tag]] = value

def distance(a, b):
	dist = (b - a)
	return np.linalg.norm(dist)

def morphing(a, b, subdiv = 4):
	segment = poster_tags[b] - poster_tags[a]
	seg_norm = np.linalg.norm(segment)
	sub_middles = np.zeros((subdiv-1, nb_tags))
	subdiv_lenght = seg_norm/subdiv	
	for i in range(subdiv-1):
		sub_middles[i] = poster_tags[a] + segment * (i+1)/(subdiv)
	morphism = [0] * (subdiv+1)
	morphism[0] = a
	morphism[subdiv] = b
	nb_posters = poster_tags.shape[0]
	for i in range (nb_posters):
		# if the selected poster is in fact a poster and is neither the goal or the beginning
		if i!=a and i!=b and i in index_posters:
			current = poster_tags[i] - poster_tags[a]
			projection = np.dot(current, segment)/seg_norm
			# if the projection is contained in the segment [a,b] with a subdiv/2 offset for more diverse morphing
			if projection > subdiv_lenght/2 and projection < seg_norm-subdiv_lenght/2:
				# sub_in is the subdivision the selected poster is in
				sub_in = floor(((projection-subdiv_lenght/2)/seg_norm) * subdiv) + 1
				# if there is no point for the subdivision, or if selected poster is nearer than currently chosen poster
				if morphism[sub_in]==0 or distance(sub_middles[sub_in-1], poster_tags[i]) < distance(sub_middles[sub_in-1], poster_tags[morphism[sub_in]]):
					morphism[sub_in] = i
	return morphism

class Command(BaseCommand):
    args = ''
    help = 'Make morphing between 2 posters'

    def add_arguments(self, parser):
        parser.add_argument('myargs', nargs='+', type=str)

    def handle(self, *args, **options):
    	a = int(options['myargs'][0])
    	b = int(options['myargs'][1])
    	if len(options['myargs'])==2:
    		print(morphing(a, b))
    	else:
    		subdiv = int(options['myargs'][2])
    		print(morphing(a, b, subdiv))