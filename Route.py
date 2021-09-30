import math
from model import *
from tools import distance


class Map:
    def __init__(self, planets: dict, game: Game):
        self.game = game
        self.planets = planets
        self.max_distance = game.max_travel_distance
        self.connections = {planet: [] for planet in planets}
        self.planets_distance = {planet: {pl: math.inf for pl in planets if pl != planet} for planet in planets}
        self.planets_ways = {planet: {pl: None for pl in planets if pl != planet} for planet in planets}

        for idx1, planet_1 in planets.items():
            for idx2, planet_2 in enumerate(game.planets):
                dist = distance((planet_1.x, planet_1.y), (planet_2.x, planet_2.y))
                if dist and dist <= self.max_distance:
                    self.connections[idx1].append(idx2)

    def find_route(self, start_planet, final_planet):
        def route(idx1, idx2):
            way = None
            for pl in self.connections[idx1]:
                dist = distance(self.planets[idx1].pos, self.planets[pl].pos)
                if was[idx1] + dist < was[pl]: was[pl] = was[idx1] + dist
                else: continue

                if pl == idx2: return [idx2, idx1]

                cur_way = route(pl, idx2)
                if cur_way is not None:
                    cur_way.append(idx1)
                    way = cur_way
            return way

        if self.planets_ways[start_planet][final_planet] is not None:
            return self.planets_ways[start_planet][final_planet]

        was = {pl: math.inf for pl in self.planets}
        was[start_planet] = 0
        way = route(start_planet, final_planet)
        way.reverse()
        self.planets_ways[start_planet][final_planet] = way
        return way


class Route:
    def __init__(self, path, starter_tick, number, resource):
        self.path = path
        self.current_tick = starter_tick
        self.number = number
        self.resource = resource
