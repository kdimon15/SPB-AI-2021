import math
from model import *
from tools import distance


class Map:
    def __init__(self, planets: dict, game: Game, starter_planet_idx: int):
        self.game = game
        self.planets = planets
        self.max_distance = game.max_travel_distance
        self.connections = {planet: [] for planet in planets}
        self.planets_distance = {planet: {pl: math.inf for pl in planets} for planet in planets}
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

        # print(start_planet, final_planet)
        if self.planets_ways[start_planet][final_planet] is not None:
            return self.planets_ways[start_planet][final_planet]

        was = {pl: math.inf for pl in self.planets}
        was[start_planet] = 0
        way = route(start_planet, final_planet)
        way.reverse()
        self.planets_ways[start_planet][final_planet] = way
        self.planets_distance[start_planet] = was
        return way

    def find_closest_free_planet(self, start_planet, exception_list):
        if self.planets_distance[start_planet][start_planet] == math.inf:
            _ = self.find_route(start_planet, start_planet + 1)

        close_idx, close_dist = None, math.inf
        for idx, dist in self.planets_distance[start_planet].items():
            if idx != start_planet and idx not in exception_list and self.planets[idx].building is None and dist < close_dist:
                close_idx = idx
                close_dist = dist
        return close_idx

    def find_closest_planet(self, start_planet, res):
        # print(self.planets_distance[start_planet])
        if self.planets_distance[start_planet][start_planet] == math.inf:
            _ = self.find_route(start_planet, start_planet+1)

        close_idx, close_dist = None, math.inf
        for idx, dist in self.planets_distance[start_planet].items():
            if idx != start_planet and self.planets[idx].harvestable_resource == res and dist < close_dist:
                close_idx = idx
                close_dist = dist
        self.planets[close_idx].mission = 'using'
        return close_idx


class Route:
    def __init__(self, path, starter_tick, number, resource):
        self.path = path
        self.current_tick = starter_tick
        self.number = number
        self.resource = resource
