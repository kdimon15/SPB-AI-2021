import math
from model import *
from tools import distance


class Map:
    def __init__(self, planets: dict, game: Game):
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

        if self.planets_ways[start_planet][final_planet] is not None: return self.planets_ways[start_planet][final_planet]

        was = {pl: math.inf for pl in self.planets}
        was[start_planet] = 0
        way = route(start_planet, final_planet)
        way.reverse()
        self.planets_ways[start_planet][final_planet] = way
        return way

    def find_closest_free_planet(self, start_planet, exception_list):
        if self.planets_distance[start_planet][start_planet] == math.inf: self.find_distances(start_planet)

        close_idx, close_dist = None, math.inf
        for idx, dist in self.planets_distance[start_planet].items():
            if idx != start_planet and idx not in exception_list and self.planets[idx].building is None and dist < close_dist:
                close_idx = idx
                close_dist = dist
        return close_idx

    def find_closest_free_planet_v2(self, list_of_planets, exception_list):
        for pl in list_of_planets:
            if self.planets_distance[pl][pl] == math.inf: self.find_distances(pl)

        all_dists = {}
        for pl in list_of_planets:
            for idx, dist in self.planets_distance[pl].items():
                if idx not in list_of_planets and idx not in exception_list and self.planets[idx].building is None:
                    if idx in all_dists: all_dists[idx] += dist
                    else: all_dists[idx] = dist

        min_dist, pl_idx = math.inf, None
        for idx, dist in all_dists.items():
            if dist < min_dist:
                min_dist = dist
                pl_idx = idx
        return pl_idx

    def find_closest_planet(self, list_of_planets, res):
        for pl in list_of_planets:
            if self.planets_distance[pl][pl] == math.inf: self.find_distances(pl)

        all_dists = {}
        for pl in list_of_planets:
            for idx, dist in self.planets_distance[pl].items():
                if idx not in list_of_planets and self.planets[idx].harvestable_resource == res:
                    if idx in all_dists: all_dists[idx] += dist
                    else: all_dists[idx] = dist

        min_dist, pl_idx = math.inf, None
        for idx, dist in all_dists.items():
            if dist < min_dist:
                min_dist = dist
                pl_idx = idx
        return pl_idx

    def find_distances(self, start_planet):
        def cons(cur_planet):
            for pl in self.connections[cur_planet]:
                dist = distance(self.planets[cur_planet].pos, self.planets[pl].pos)
                if dists[cur_planet] + dist < dists[pl]: dists[pl] = dists[cur_planet] + dist
                else: continue
                cons(pl)

        dists = {pl: math.inf for pl in self.planets}
        dists[start_planet] = 0
        cons(start_planet)
        self.planets_distance[start_planet] = dists

    def find_better_place(self):
        pass


class Route:
    def __init__(self, path, starter_tick, number, resource):
        self.path = path
        self.current_tick = starter_tick
        self.number = number
        self.resource = resource
