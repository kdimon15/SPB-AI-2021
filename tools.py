import math
from model import *

all_types_of_planets = ['starter', 'stone', 'metal', 'ore', 'sand',
                        'chip', 'accumulator', 'organics', 'silicon', 'plastic', 'replicator']

all_resources = [Resource.METAL, Resource.STONE, Resource.ORE,
                 Resource.SAND, Resource.ACCUMULATOR, Resource.ORGANICS,
                 Resource.CHIP, Resource.SILICON, Resource.PLASTIC]

def distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def find_closest_planet_by_type(pos, type_of_planet: str, planets: dict):
    closest_dist, closest_planet = math.inf, None
    for planet_idx, planet in planets.items():
        if not planet.enemy_workers and planet.mission == type_of_planet:
            dist = distance(pos, planet.pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_planet = planet

    if closest_planet is None: return None
    else: return closest_planet.idx
