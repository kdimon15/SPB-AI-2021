from model import *
from My_Planet import MyPlanet
from tools import distance, all_types_of_planets
from Route import Route, Map

"""
TODO:
- Баг со зданиями
- Ресурсы не долетают

- Не добывать лишние ресурсы
- Переработать систему пойстройки
- Искать самую близкую планету, от нескольких планет сразу, а не от одной
- Строить здание по пути, а не самое близкое
- Переработать систему отправки юнитов
- Улучшить систему выбора планет
"""


class MyStrategy:
    def __init__(self):
        self.planets = {}
        self.important_planets = {planet: [-1, -1] for planet in all_types_of_planets}
        self.game = None
        self.starter_planet_idx = 0
        self.routes = []
        self.map = None
        self.moves = []
        self.stage = 0
        self.need_resources_for_building = {}

    def initialize(self):
        for idx, planet in enumerate(self.game.planets):
            self.planets[idx] = MyPlanet(planet, idx, self.game.my_index)
            if self.planets[idx].my_workers > 0:
                self.important_planets['stone'] = idx
                self.starter_planet_idx = idx
                self.planets[idx].mission = 'stone'

        self.map = Map(self.planets, self.game)
        self.initialize_planets()

    def initialize_planets(self):
        self.important_planets['ore'] = self.map.find_closest_planet(self.starter_planet_idx, Resource.ORE)
        self.important_planets['sand'] = self.map.find_closest_planet(self.starter_planet_idx, Resource.SAND)
        self.important_planets['organics'] = self.map.find_closest_planet(self.starter_planet_idx, Resource.ORGANICS)
        self.planets[self.important_planets['ore']].mission = 'ore'
        self.planets[self.important_planets['sand']].mission = 'sand'
        self.planets[self.important_planets['organics']].mission = 'organics'

        occupied_planets = [self.starter_planet_idx, self.important_planets['ore'], self.important_planets['sand'], self.important_planets['organics']]

        self.important_planets['metal'][0] = self.map.find_closest_free_planet(self.important_planets['ore'], occupied_planets)
        self.planets[self.important_planets['metal'][0]].mission = 'metal'
        occupied_planets.append(self.important_planets['metal'][0])
        self.important_planets['metal'][1] = self.map.find_closest_free_planet(self.important_planets['ore'], occupied_planets)
        self.planets[self.important_planets['metal'][1]].mission = 'metal'
        occupied_planets.append(self.important_planets['metal'][1])

        self.important_planets['plastic'] = self.map.find_closest_free_planet(self.important_planets['organics'], occupied_planets)
        occupied_planets.append(self.important_planets['plastic'])
        self.planets[self.important_planets['plastic']].mission = 'plastic'

        self.important_planets['silicon'] = self.map.find_closest_free_planet(self.important_planets['sand'], occupied_planets)
        occupied_planets.append(self.important_planets['silicon'])
        self.planets[self.important_planets['silicon']].mission = 'silicon'

        self.important_planets['replicator'] = self.map.find_closest_free_planet(self.important_planets['metal'][0], occupied_planets)
        occupied_planets.append(self.important_planets['replicator'])
        self.planets[self.important_planets['replicator']].mission = 'replicator'

        self.important_planets['accumulator'] = self.map.find_closest_free_planet(self.important_planets['replicator'], occupied_planets)
        occupied_planets.append(self.important_planets['accumulator'])
        self.planets[self.important_planets['accumulator']].mission = 'accumulator'

        self.important_planets['chip'] = self.map.find_closest_free_planet(self.important_planets['replicator'], occupied_planets)
        occupied_planets.append(self.important_planets['chip'])
        self.planets[self.important_planets['chip']].mission = 'chip'

    def update(self):
        for idx, planet in enumerate(self.game.planets): self.planets[idx].update(planet)

        for route in self.routes:
            if route.current_tick == self.game.current_tick:
                self.planets[route.path[0]].my_workers -= route.number
                if route.resource is not None: self.planets[route.path[0]].resources[route.resource] -= route.number
            if route.resource is not None:
                self.planets[route.path[-1]].resources_in_flight[route.resource] += route.number

        self.need_resources_for_building = {}

        for type, planets in self.important_planets.items():
            if type == 'stone': pass
            elif type in ['ore', 'sand', 'organics']:
                if self.planets[planets].building is None and self.planets[planets].resources[Resource.STONE] + self.planets[planets].resources_in_flight[Resource.STONE] < 50:
                    self.need_resources_for_building[planets] = 50 - self.planets[planets].resources[Resource.STONE] - self.planets[planets].resources_in_flight[Resource.STONE]
            elif type in ['silicon', 'plastic', 'chip', 'accumulator']:
                if self.planets[planets].building is None and self.planets[planets].resources[Resource.STONE] + self.planets[planets].resources_in_flight[Resource.STONE] < 100:
                    self.need_resources_for_building[planets] = 100 - self.planets[planets].resources[Resource.STONE] - self.planets[planets].resources_in_flight[Resource.STONE]
            elif type == 'replicator':
                if self.planets[planets].building is None and self.planets[planets].resources[Resource.STONE] + self.planets[planets].resources_in_flight[Resource.STONE] < 200:
                    self.need_resources_for_building[planets] = 200 - self.planets[planets].resources[Resource.STONE] - self.planets[planets].resources_in_flight[Resource.STONE]
            else:
                for pl in planets:
                    if self.planets[pl].building is None and self.planets[pl].resources[Resource.STONE] + self.planets[pl].resources_in_flight[Resource.STONE] < 100:
                        self.need_resources_for_building[pl] = 100 - self.planets[pl].resources[Resource.STONE] - self.planets[pl].resources_in_flight[Resource.STONE]

    def update_routes(self):
        for i in range(len(self.routes) - 1, -1, -1):
            route = self.routes[i]

            if route.current_tick == self.game.current_tick and route.number > 0:
                if self.planets[route.path[0]].enemy_workers == 0:
                    if route.number > 0: self.moves.append(MoveAction(route.path[0], route.path[1], route.number, route.resource))

                    self.routes[i].current_tick += distance(self.planets[self.routes[i].path[0]].pos, self.planets[self.routes[i].path[1]].pos)
                    self.routes[i].path = self.routes[i].path[1:]
                    if len(self.routes[i].path) < 2 or self.routes[i].number == 0: del self.routes[i]  # self.routes[i].current_tick = -1
                else: route.current_tick += 1

    def get_my_planets(self):
        my_planets = {}
        for tool in all_types_of_planets:
            if tool != 'metal': my_planets[tool] = self.planets[self.important_planets[tool]]
            else: my_planets[tool] = [self.planets[self.important_planets[tool][0]], self.planets[self.important_planets[tool][1]]]
        return my_planets

    def get_action(self, game: Game) -> Action:
        self.game = game
        self.moves, builds = [], []

        if game.current_tick == 0: self.initialize()
        else: self.update()

        my_planets = self.get_my_planets()

        if game.current_tick > 950:
            for idx, planet in self.planets.items():
                if idx != my_planets['replicator'].idx and planet.my_workers:
                    self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'].idx), game.current_tick, planet.my_workers, None))
            self.update_routes()
            return Action(self.moves, builds)

        for idx, planet in self.planets.items():
            if planet.my_workers > 0:

                if planet.mission == 'stone':
                    if len(self.need_resources_for_building) == 0 and game.current_tick != 0:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, planet.my_workers // 3, None))
                        self.routes.append(Route(self.map.find_route(idx, my_planets['sand'].idx), game.current_tick, planet.my_workers // 3, None))
                        self.routes.append(Route(self.map.find_route(idx, my_planets['organics'].idx), game.current_tick, planet.my_workers - planet.my_workers // 3 * 2, None))
                    elif planet.resources[Resource.STONE] > 0:
                        for planet_idx, num_resources in self.need_resources_for_building.items():
                            if planet.my_workers >= num_resources and planet.resources[Resource.STONE] >= num_resources:
                                self.routes.append(Route(self.map.find_route(idx, planet_idx), game.current_tick, num_resources, Resource.STONE))
                                planet.my_workers -= num_resources
                                planet.resources[Resource.STONE] -= num_resources

                elif planet.mission == 'ore':
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.MINES))
                        if planet.resources[Resource.STONE] >= 50 and len(self.need_resources_for_building):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    if planet.resources[Resource.ORE] < 800: planet.my_workers -= 60
                    if planet.resources[Resource.ORE] > 0 and planet.my_workers > 0:
                        num_workers_to_send = min(planet.resources[Resource.ORE], planet.my_workers)
                        self.routes.append(Route(self.map.find_route(idx, my_planets['metal'][0].idx), game.current_tick, num_workers_to_send // 2, Resource.ORE))
                        self.routes.append(Route(self.map.find_route(idx, my_planets['metal'][1].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 2, Resource.ORE))

                elif planet.mission == 'sand':
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CAREER))
                        if planet.resources[Resource.STONE] >= 50 and len(self.need_resources_for_building):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    if planet.resources[Resource.SAND] < 500: planet.my_workers -= 14
                    if planet.resources[Resource.SAND] > 0 and planet.my_workers > 0:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['silicon'].idx), game.current_tick, min(planet.my_workers, planet.resources[Resource.SAND]), Resource.SAND))

                elif planet.mission == 'organics':
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FARM))
                        if planet.resources[Resource.STONE] >= 50 and len(self.need_resources_for_building):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    if planet.resources[Resource.ORGANICS] < 500: planet.my_workers -= 14
                    if planet.resources[Resource.ORGANICS] > 0 and planet.my_workers > 0:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['plastic'].idx), game.current_tick, min(planet.my_workers, planet.resources[Resource.ORGANICS]), Resource.ORGANICS))

                elif planet.mission == 'metal':
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FOUNDRY))
                        if planet.resources[Resource.STONE] >= 100 and len(self.need_resources_for_building):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    free_workers = planet.my_workers - (planet.resources[Resource.METAL] + planet.resources[Resource.ORE] // 2)
                    need_ore = planet.resources[Resource.ORE] <= 1
                    need_replicator = my_planets['replicator'].resources[Resource.METAL] < 80
                    need_accum = my_planets['accumulator'].resources[Resource.ACCUMULATOR] < 50
                    if need_ore:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.METAL])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 0:
                            if need_replicator and need_accum:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'].idx), game.current_tick, num_workers_to_send // 3, Resource.METAL))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send // 3, Resource.METAL))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 3 * 2, Resource.METAL))
                            elif need_accum:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'].idx), game.current_tick, num_workers_to_send // 2, Resource.METAL))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 2, Resource.METAL))
                            elif need_replicator:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'].idx), game.current_tick, num_workers_to_send // 2, Resource.METAL))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 2, Resource.METAL))
                            else:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send, Resource.METAL))
                        if planet.my_workers > 0:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, planet.my_workers, None))
                        continue

                    if free_workers > 5:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, free_workers, None))
                        planet.my_workers -= free_workers
                    if planet.resources[Resource.METAL] > 0 and planet.my_workers > 0:
                        num_workers_to_send = min(planet.resources[Resource.METAL], planet.my_workers)
                        if num_workers_to_send > 10:
                            if need_replicator and need_accum:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'].idx), game.current_tick, num_workers_to_send // 3, Resource.METAL))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send // 3, Resource.METAL))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 3 * 2, Resource.METAL))
                            elif need_accum:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'].idx), game.current_tick, num_workers_to_send // 2, Resource.METAL))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 2, Resource.METAL))
                            elif need_replicator:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'].idx), game.current_tick, num_workers_to_send // 2, Resource.METAL))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 2, Resource.METAL))
                            else:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send, Resource.METAL))

                elif planet.mission == 'silicon':
                    free_workers = planet.my_workers - (planet.resources[Resource.SILICON] + planet.resources[Resource.SAND] // 2)
                    need_sand = planet.resources[Resource.SAND] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FURNACE))
                        if planet.resources[Resource.STONE] >= 100 and len(self.need_resources_for_building):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'].idx), game.current_tick + 2, planet.my_workers, None))
                        continue

                    if need_sand:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.SILICON])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 0: self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send, Resource.SILICON))
                        if planet.my_workers > 0: self.routes.append(Route(self.map.find_route(idx, my_planets['sand'].idx), game.current_tick, planet.my_workers, None))
                        continue

                    if free_workers > 5:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['sand'].idx), game.current_tick, free_workers, None))
                        planet.my_workers -= free_workers
                    if planet.resources[Resource.SILICON] > 0 and planet.my_workers > 0:
                        num_workers_to_send = min(planet.resources[Resource.SILICON], planet.my_workers)
                        if num_workers_to_send > 10:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['chip'].idx), game.current_tick, num_workers_to_send, Resource.SILICON))

                elif planet.mission == 'plastic':
                    free_workers = planet.my_workers - (planet.resources[Resource.PLASTIC] + planet.resources[Resource.ORGANICS] // 2)
                    need_organics = planet.resources[Resource.ORGANICS] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.BIOREACTOR))
                        planet.my_workers += game.building_properties[BuildingType.FURNACE].max_workers
                        if planet.resources[Resource.STONE] >= 100 and len(self.need_resources_for_building):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'].idx), game.current_tick + 2, planet.my_workers, None))
                        continue

                    if need_organics:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.PLASTIC])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 0: self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'].idx), game.current_tick, num_workers_to_send, Resource.PLASTIC))
                        if planet.my_workers > 0: self.routes.append(Route(self.map.find_route(idx, my_planets['organics'].idx), game.current_tick, planet.my_workers, None))
                        continue

                    if free_workers > 5:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['organics'].idx), game.current_tick, free_workers, None))
                        planet.my_workers -= free_workers
                    if planet.my_workers > 0 and planet.resources[Resource.PLASTIC] > 0:
                        num_workers_to_send = min(planet.resources[Resource.PLASTIC], planet.my_workers)
                        if num_workers_to_send > 10:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'].idx), game.current_tick, num_workers_to_send, Resource.PLASTIC))

                elif planet.mission == 'accumulator':
                    free_workers = planet.my_workers - (planet.resources[Resource.ACCUMULATOR] + min(planet.resources[Resource.METAL] // 2, planet.resources[Resource.PLASTIC] // 2))
                    need_plastic = planet.resources[Resource.PLASTIC] <= 1
                    need_metal = planet.resources[Resource.METAL] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.ACCUMULATOR_FACTORY))
                        planet.my_workers += game.building_properties[BuildingType.ACCUMULATOR_FACTORY].max_workers
                        if planet.resources[Resource.STONE] >= 100 and len(self.need_resources_for_building):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'].idx), game.current_tick + 2, planet.my_workers, None))
                        continue

                    if need_plastic or need_metal:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.ACCUMULATOR])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 0: self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'].idx), game.current_tick, num_workers_to_send, Resource.ACCUMULATOR))
                        if planet.my_workers > 0:
                            if need_plastic and need_metal:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['plastic'].idx), game.current_tick, planet.my_workers // 2, None))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, planet.my_workers - planet.my_workers // 2, None))
                            elif need_plastic: self.routes.append(Route(self.map.find_route(idx, my_planets['plastic'].idx), game.current_tick, planet.my_workers, None))
                            else: self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, planet.my_workers, None))
                        continue

                    # if free_workers > 5:
                    #     if planet.resources[Resource.PLASTIC] < planet.resources[Resource.METAL]: self.routes.append(Route(self.map.find_route(idx, my_planets['organics'].idx), game.current_tick, free_workers, None))
                    #     else: self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, free_workers, None))
                    #     planet.my_workers -= free_workers
                    if planet.resources[Resource.ACCUMULATOR] > 0 and planet.my_workers > 0:
                        num_workers_to_send = min(planet.resources[Resource.ACCUMULATOR], planet.my_workers - 20)
                        if num_workers_to_send > 10:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'].idx), game.current_tick, num_workers_to_send, Resource.ACCUMULATOR))

                elif planet.mission == 'chip':
                    free_workers = planet.my_workers - (planet.resources[Resource.CHIP] + min(planet.resources[Resource.METAL] // 2, planet.resources[Resource.SILICON] // 2))
                    need_silicon = planet.resources[Resource.SILICON] <= 1
                    need_metal = planet.resources[Resource.METAL] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CHIP_FACTORY))
                        if planet.resources[Resource.STONE] >= 100 and len(self.need_resources_for_building):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    if need_silicon or need_metal:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.CHIP])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 0: self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'].idx), game.current_tick, num_workers_to_send, Resource.CHIP))
                        if planet.my_workers > 0:
                            if need_metal and need_silicon:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, planet.my_workers // 2, None))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['sand'].idx), game.current_tick, planet.my_workers - planet.my_workers // 2, None))
                            elif need_metal: self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, planet.my_workers, None))
                            else: self.routes.append(Route(self.map.find_route(idx, my_planets['sand'].idx), game.current_tick, planet.my_workers, None))
                        continue

                    # if free_workers > 0:
                    #     self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, free_workers // 2, None))
                    #     self.routes.append(Route(self.map.find_route(idx, my_planets['sand'].idx), game.current_tick, free_workers - free_workers//2, None))
                    if planet.resources[Resource.CHIP] > 0 and planet.my_workers > 0:
                        num_workers_to_send = min(planet.resources[Resource.CHIP], planet.my_workers - 20)
                        if num_workers_to_send > 10:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'].idx), game.current_tick, num_workers_to_send, Resource.CHIP))

                elif planet.mission == 'replicator':
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.REPLICATOR))
                        if planet.resources[Resource.STONE] >= 200 and len(self.need_resources_for_building):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    need_chip = planet.resources[Resource.CHIP] <= 1
                    need_metal = planet.resources[Resource.METAL] <= 1
                    need_accumulator = planet.resources[Resource.ACCUMULATOR] <= 1
                    planet.my_workers -= game.building_properties[BuildingType.REPLICATOR].max_workers
                    if need_chip or need_metal or need_accumulator or planet.my_workers > 0:
                        if planet.resources[Resource.ACCUMULATOR] > 50:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['sand'].idx), game.current_tick, planet.my_workers // 2, None))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, planet.my_workers - planet.my_workers // 2, None))
                        else:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['organics'].idx), game.current_tick, planet.my_workers // 3, None))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['sand'].idx), game.current_tick, planet.my_workers // 3, None))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, planet.my_workers - planet.my_workers // 3 * 2, None))

                elif planet.mission == 'free':
                    print(game.current_tick, planet.idx, len(game.flying_worker_groups))
                    self.routes.append(Route(self.map.find_route(idx, my_planets['ore'].idx), game.current_tick, planet.my_workers, None))

        self.update_routes()
        return Action(self.moves, builds)
