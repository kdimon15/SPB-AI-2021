from model import *

all_types_of_planets = ['stone', 'metal', 'ore', 'sand',
                        'chip', 'accumulator', 'organics', 'silicon', 'plastic', 'replicator']

all_resources = [Resource.METAL, Resource.STONE, Resource.ORE,
                 Resource.SAND, Resource.ACCUMULATOR, Resource.ORGANICS,
                 Resource.CHIP, Resource.SILICON, Resource.PLASTIC]

def distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
