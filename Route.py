import math
from model import *
from My_Planet import MyPlanet
from tools import distance, find_closest_planet_by_type, all_types_of_planets

"""
TODO:
- Сделать свою систему перемещиний
- Более эффективно определять кол-во юнитов для отправки
- Отправлять более одного отряда за тик
- Учитывать прилетающих юнитов при отправке
- Искать места для зданий, исходя из длины маршрутов, а не расстояния между планетами.
"""


class Map:
    def __init__(self, planets: dict, game: Game):
        self.game = game
        self.planets = planets
        self.max_distance = game.max_travel_distance
        self.connections = {planet: [] for planet in planets}

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

        was = {pl: math.inf for pl in self.planets}
        was[start_planet] = 0
        way = route(start_planet, final_planet)
        return way


class MyStrategy:
    def __init__(self):
        self.planets = {}
        self.important_planets = {}
        self.game = None
        self.starter_planet_idx = 0
        self.map = None

    def initialize(self):
        for idx, planet in enumerate(self.game.planets):
            self.planets[idx] = MyPlanet(planet, idx, self.game.my_index)
            if self.planets[idx].my_workers > 0:
                self.important_planets['starter'] = idx
                self.important_planets['stone'] = idx
                self.starter_planet_idx = idx
                self.planets[idx].mission = 'stone'

        for tool in ['ore', 'sand', 'organics']:
            planet_idx = find_closest_planet_by_type(self.planets[self.starter_planet_idx].pos, tool, self.planets)
            self.important_planets[tool] = planet_idx

        for tool in ['replicator', 'accumulator', 'chip', 'metal', 'plastic', 'silicon']:
            planet_idx = find_closest_planet_by_type(self.planets[self.starter_planet_idx].pos, 'free', self.planets)
            self.important_planets[tool] = planet_idx
            self.planets[planet_idx].mission = tool
        self.map = Map(self.planets, self.game)

    def update(self):
        for idx, planet in enumerate(self.game.planets): self.planets[idx].update(planet)

        for fly_group in self.game.flying_worker_groups:
            if fly_group.player_index == self.game.my_index:
                self.planets[fly_group.target_planet].workers_in_flight += fly_group.number
                if fly_group.resource is not None:
                    self.planets[fly_group.target_planet].resources_in_flight[fly_group.resource] += fly_group.number

    def get_action(self, game: Game) -> Action:
        self.game = game
        moves, builds = [], []

        if game.current_tick == 0:
            self.initialize()
        else:
            self.update()

        my_planets = {tool: self.planets[self.important_planets[tool]] for tool in all_types_of_planets}
        if game.current_tick == 10: print(self.map.find_route(my_planets['stone'].idx, my_planets['ore'].idx))
        return Action(moves, builds)
