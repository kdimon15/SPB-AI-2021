from model import *
from My_Planet import MyPlanet
from tools import distance, all_types_of_planets
from Route import Route, Map


"""
TODO:
- Сделать систему защиты
- Отправлять юнитов, исходя из кол-ва ресурсов на планетах

- Переработать систему постройки
- Строить здание по пути, а не самое близкое
"""


class MyStrategy:
    def __init__(self):
        self.planets = {}
        self.important_planets = {planet: [] for planet in all_types_of_planets}
        self.game = None
        self.starter_planet_idx = 0
        self.routes = []
        self.map = None
        self.moves = []
        self.stage = 0
        self.need_resources_for_building = {}
        self.planets_resources = {}

    def initialize(self):
        for idx, planet in enumerate(self.game.planets):
            self.planets[idx] = MyPlanet(planet, idx, self.game.my_index)
            if self.planets[idx].my_workers > 0:
                self.important_planets['stone'].append(idx)
                self.starter_planet_idx = idx
                self.planets[idx].mission = 'stone'

        self.map = Map(self.planets, self.game)
        self.initialize_planets()

    def initialize_planets(self):
        self.important_planets['ore'].append(self.map.find_closest_planet([self.starter_planet_idx], Resource.ORE))
        self.important_planets['sand'].append(self.map.find_closest_planet([self.important_planets['ore'][0]], Resource.SAND))
        self.important_planets['organics'].append(self.map.find_closest_planet([self.important_planets['ore'][0],
                                                                                self.important_planets['sand'][0]], Resource.ORGANICS))
        self.planets[self.important_planets['ore'][0]].mission = 'ore'
        self.planets[self.important_planets['sand'][0]].mission = 'sand'
        self.planets[self.important_planets['organics'][0]].mission = 'organics'

        occupied_planets = [self.starter_planet_idx,
                            self.important_planets['ore'][0],
                            self.important_planets['sand'][0],
                            self.important_planets['organics'][0]]

        for i in range(3):
            self.important_planets['metal'].append(self.map.find_closest_free_planet_v2([self.important_planets['ore'][0]], occupied_planets))
            self.planets[self.important_planets['metal'][i]].mission = 'metal'
            occupied_planets.append(self.important_planets['metal'][i])

        for i in range(1):
            self.important_planets['replicator'].append(self.map.find_closest_free_planet_v2([self.important_planets['metal'][0],
                                                                                              self.important_planets['metal'][1],
                                                                                              self.important_planets['metal'][2]], occupied_planets))
            occupied_planets.append(self.important_planets['replicator'][i])
            self.planets[self.important_planets['replicator'][i]].mission = 'replicator'

        for i in range(2):
            self.important_planets['chip'].append(self.map.find_closest_free_planet_v2([self.important_planets['replicator'][0]], occupied_planets))
            occupied_planets.append(self.important_planets['chip'][i])
            self.planets[self.important_planets['chip'][i]].mission = 'chip'

        for i in range(1):
            self.important_planets['accumulator'].append(self.map.find_closest_free_planet_v2([self.important_planets['replicator'][0]], occupied_planets))
            occupied_planets.append(self.important_planets['accumulator'][i])
            self.planets[self.important_planets['accumulator'][i]].mission = 'accumulator'

        for i in range(1):
            self.important_planets['plastic'].append(self.map.find_closest_free_planet_v2([self.important_planets['organics'][0],
                                                                                           self.important_planets['accumulator'][0]], occupied_planets))
            occupied_planets.append(self.important_planets['plastic'][i])
            self.planets[self.important_planets['plastic'][i]].mission = 'plastic'

        for i in range(2):
            self.important_planets['silicon'].append(self.map.find_closest_free_planet_v2([self.important_planets['sand'][0],
                                                                                           self.important_planets['chip'][0],
                                                                                           self.important_planets['chip'][1]], occupied_planets))
            occupied_planets.append(self.important_planets['silicon'][i])
            self.planets[self.important_planets['silicon'][i]].mission = 'silicon'

    def update(self):
        for idx, planet in enumerate(self.game.planets): self.planets[idx].update(planet)

        for route in self.routes:
            if route.current_tick == self.game.current_tick:
                self.planets[route.path[0]].my_workers -= route.number
                if route.resource is not None: self.planets[route.path[0]].resources[route.resource] -= route.number
            if route.resource is not None:
                self.planets[route.path[-1]].resources_in_flight[route.resource] += route.number

        self.need_resources_for_building = {}
        self.planets_resources = {}

        for type, planets in self.important_planets.items():
            for pl in planets:
                if self.planets[pl].building is None:
                    if type == 'stone': pass
                    elif type in ['ore', 'sand', 'organics'] and self.planets[pl].resources[Resource.STONE] + self.planets[pl].resources_in_flight[Resource.STONE] < 50:
                        self.need_resources_for_building[pl] = 50 - self.planets[pl].resources[Resource.STONE] - self.planets[pl].resources_in_flight[Resource.STONE]
                    elif type in ['silicon', 'plastic', 'chip', 'accumulator', 'metal'] and self.planets[pl].resources[Resource.STONE] + self.planets[pl].resources_in_flight[Resource.STONE] < 100:
                        self.need_resources_for_building[pl] = 100 - self.planets[pl].resources[Resource.STONE] - self.planets[pl].resources_in_flight[Resource.STONE]
                    elif type == 'replicator' and self.planets[pl].resources[Resource.STONE] + self.planets[pl].resources_in_flight[Resource.STONE] < 200:
                        self.need_resources_for_building[pl] = 200 - self.planets[pl].resources[Resource.STONE] - self.planets[pl].resources_in_flight[Resource.STONE]

        for type, planets in self.important_planets.items():
            for pl in planets:
                if type in ['metal', 'silicon', 'chip']:
                    if type in self.planets_resources: self.planets_resources[type][pl] = self.planets[pl].resources
                    else: self.planets_resources[type] = {pl: self.planets[pl].resources}  # После складывать с resources_in_flight

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
            for idx in self.important_planets[tool]:
                if tool in my_planets: my_planets[tool].append(self.planets[idx])
                else: my_planets[tool] = [self.planets[idx]]
        return my_planets

    def get_action(self, game: Game) -> Action:
        self.game = game
        self.moves, builds = [], []

        if game.current_tick == 0: self.initialize()
        else: self.update()

        my_planets = self.get_my_planets()

        if len(self.need_resources_for_building) > 0: print(game.current_tick, self.need_resources_for_building)
        print(len(game.flying_worker_groups), len(self.routes))

        for idx, planet in self.planets.items():
            if planet.my_workers > 0:

                if planet.mission == 'stone':
                    if len(self.need_resources_for_building) == 0 and game.current_tick != 0:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, planet.my_workers // 3, None))
                        self.routes.append(Route(self.map.find_route(idx, my_planets['sand'][0].idx), game.current_tick, planet.my_workers // 3, None))
                        self.routes.append(Route(self.map.find_route(idx, my_planets['organics'][0].idx), game.current_tick, planet.my_workers - planet.my_workers // 3 * 2, None))
                    elif planet.resources[Resource.STONE] > 0:
                        for planet_idx, num_resources in self.need_resources_for_building.items():
                            if planet.my_workers > 0 and planet.resources[Resource.STONE] > 0:
                                num_workers_to_send = min(planet.my_workers, planet.resources[Resource.STONE], num_resources)
                                self.routes.append(Route(self.map.find_route(idx, planet_idx), game.current_tick, num_workers_to_send, Resource.STONE))
                                planet.my_workers -= num_workers_to_send
                                planet.resources[Resource.STONE] -= num_workers_to_send

                elif planet.mission == 'ore':
                    if planet.building is not None and planet.building.building_type != BuildingType.MINES:
                        builds.append(BuildingAction(planet.idx, None))
                        continue
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.MINES))
                        if (len(self.need_resources_for_building) > 0 and planet.resources[Resource.STONE] >= 50) or (planet.resources[Resource.STONE] < 50 and planet.resources_in_flight[Resource.STONE] == 0):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick + 1, planet.my_workers, None))
                        continue
                    if len(self.need_resources_for_building) > 0:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick, planet.my_workers, None))
                        continue

                    if planet.resources[Resource.ORE] < 1000: planet.my_workers -= 70
                    if planet.resources[Resource.ORE] > 0 and planet.my_workers > 0:
                        num_workers_to_send = min(planet.resources[Resource.ORE], planet.my_workers)
                        if num_workers_to_send > 50:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['metal'][0].idx), game.current_tick, num_workers_to_send // 3, Resource.ORE))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['metal'][1].idx), game.current_tick, num_workers_to_send // 3, Resource.ORE))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['metal'][2].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 3 * 2, Resource.ORE))

                elif planet.mission == 'sand':
                    if planet.building is not None and planet.building.building_type != BuildingType.CAREER:
                        builds.append(BuildingAction(planet.idx, None))
                        continue
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CAREER))
                        if (len(self.need_resources_for_building) > 0 and planet.resources[Resource.STONE] >= 50) or (planet.resources[Resource.STONE] < 50 and planet.resources_in_flight[Resource.STONE] == 0):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    if planet.resources[Resource.SAND] < 500: planet.my_workers -= 30
                    if planet.resources[Resource.SAND] > 0 and planet.my_workers > 0:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.SAND])
                        if num_workers_to_send > 40:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['silicon'][0].idx), game.current_tick, num_workers_to_send // 2, Resource.SAND))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['silicon'][1].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 2, Resource.SAND))

                elif planet.mission == 'organics':
                    if planet.building is not None and planet.building.building_type != BuildingType.FARM: builds.append(BuildingAction(planet.idx, None))
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FARM))
                        if (len(self.need_resources_for_building) > 0 and planet.resources[Resource.STONE] >= 50) or (planet.resources[Resource.STONE] < 50 and planet.resources_in_flight[Resource.STONE] == 0):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    if planet.resources[Resource.ORGANICS] < 500: planet.my_workers -= 10
                    if planet.resources[Resource.ORGANICS] > 0 and planet.my_workers > 0:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.ORGANICS])
                        if num_workers_to_send > 25:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['plastic'][0].idx), game.current_tick, num_workers_to_send, Resource.ORGANICS))

                elif planet.mission == 'metal':
                    if planet.building is not None and planet.building.building_type != BuildingType.FOUNDRY:
                        builds.append(BuildingAction(planet.idx, None))
                        continue
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FOUNDRY))
                        if (len(self.need_resources_for_building) > 0 and planet.resources[Resource.STONE] >= 100) or (planet.resources[Resource.STONE] < 100 and planet.resources_in_flight[Resource.STONE] == 0):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    free_workers = planet.my_workers - (planet.resources[Resource.METAL] + planet.resources[Resource.ORE] // 2)
                    need_ore = planet.resources[Resource.ORE] <= 1
                    if need_ore:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.METAL])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 20:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'][0].idx), game.current_tick, num_workers_to_send // 4, Resource.METAL))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['chip'][0].idx), game.current_tick, num_workers_to_send // 4, Resource.METAL))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['chip'][1].idx), game.current_tick, num_workers_to_send // 4, Resource.METAL))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'][0].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 4 * 3, Resource.METAL))
                        if planet.my_workers > 5:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, planet.my_workers, None))
                        continue

                    if free_workers > 100 and len(self.routes) < 60:  # Мои рабочие группы
                        self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, free_workers, None))
                        planet.my_workers -= free_workers
                    if planet.resources[Resource.METAL] > 0 and planet.my_workers > 0 and len(self.routes) < 65:
                        num_workers_to_send = min(planet.resources[Resource.METAL], planet.my_workers - game.building_properties[BuildingType.FOUNDRY].max_workers)
                        if num_workers_to_send > 40:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'][0].idx), game.current_tick, num_workers_to_send // 4, Resource.METAL))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['chip'][0].idx), game.current_tick, num_workers_to_send // 4, Resource.METAL))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['chip'][1].idx), game.current_tick, num_workers_to_send // 4, Resource.METAL))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'][0].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 4 * 3, Resource.METAL))

                elif planet.mission == 'silicon':
                    if planet.building is not None and planet.building.building_type != BuildingType.FURNACE:
                        builds.append(BuildingAction(planet.idx, None))
                        continue
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FURNACE))
                        if (len(self.need_resources_for_building) > 0 and planet.resources[Resource.STONE] >= 100) or (planet.resources[Resource.STONE] < 100 and planet.resources_in_flight[Resource.STONE] == 0):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick + 2, planet.my_workers, None))
                        continue

                    free_workers = planet.my_workers - (planet.resources[Resource.SILICON] + planet.resources[Resource.SAND] // 2)
                    need_sand = planet.resources[Resource.SAND] <= 1
                    if need_sand:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.SILICON])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 20:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['chip'][0].idx), game.current_tick, num_workers_to_send // 2, Resource.SILICON))
                            self.routes.append(Route(self.map.find_route(idx, my_planets['chip'][1].idx), game.current_tick, num_workers_to_send - num_workers_to_send // 2, Resource.SILICON))
                        if planet.my_workers > 5: self.routes.append(Route(self.map.find_route(idx, my_planets['sand'][0].idx), game.current_tick, planet.my_workers, None))
                        continue

                    if free_workers > 100 and len(self.routes) < 60:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['sand'][0].idx), game.current_tick, free_workers, None))
                        planet.my_workers -= free_workers
                    if planet.resources[Resource.SILICON] > 0 and planet.my_workers > 0 and len(self.routes) < 60:
                        num_workers_to_send = min(planet.resources[Resource.SILICON], planet.my_workers - game.building_properties[BuildingType.FURNACE].max_workers)
                        if num_workers_to_send > 100:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['chip'][0].idx), game.current_tick, num_workers_to_send, Resource.SILICON))

                elif planet.mission == 'plastic':
                    if planet.building is not None and planet.building.building_type != BuildingType.BIOREACTOR:
                        builds.append(BuildingAction(planet.idx, None))
                        continue
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.BIOREACTOR))
                        if (len(self.need_resources_for_building) > 0 and planet.resources[Resource.STONE] >= 100) or (planet.resources[Resource.STONE] < 100 and planet.resources_in_flight[Resource.STONE] == 0):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick+1, planet.my_workers, None))
                        continue

                    free_workers = planet.my_workers - (planet.resources[Resource.PLASTIC] + planet.resources[Resource.ORGANICS] // 2)
                    need_organics = planet.resources[Resource.ORGANICS] <= 1
                    if need_organics:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.PLASTIC])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 20: self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'][0].idx), game.current_tick, num_workers_to_send, Resource.PLASTIC))
                        if planet.my_workers > 5: self.routes.append(Route(self.map.find_route(idx, my_planets['organics'][0].idx), game.current_tick, planet.my_workers, None))
                        continue

                    if free_workers > 100 and len(self.routes) < 60:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['organics'][0].idx), game.current_tick, free_workers, None))
                        planet.my_workers -= free_workers
                    if planet.my_workers > 0 and planet.resources[Resource.PLASTIC] > 0 and len(self.routes) < 60:
                        num_workers_to_send = min(planet.resources[Resource.PLASTIC], planet.my_workers - game.building_properties[BuildingType.BIOREACTOR].max_workers)
                        if num_workers_to_send > 100:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['accumulator'][0].idx), game.current_tick, num_workers_to_send, Resource.PLASTIC))

                elif planet.mission == 'accumulator':
                    if planet.building is not None and planet.building.building_type != BuildingType.ACCUMULATOR_FACTORY:
                        builds.append(BuildingAction(planet.idx, None))
                        continue
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.ACCUMULATOR_FACTORY))
                        if (len(self.need_resources_for_building) > 0 and planet.resources[Resource.STONE] >= 100) or (planet.resources[Resource.STONE] < 100 and planet.resources_in_flight[Resource.STONE] == 0):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick + 2, planet.my_workers, None))
                        continue

                    free_workers = planet.my_workers - (planet.resources[Resource.ACCUMULATOR] + min(planet.resources[Resource.METAL] // 2, planet.resources[Resource.PLASTIC] // 2))
                    need_plastic = planet.resources[Resource.PLASTIC] <= 1
                    need_metal = planet.resources[Resource.METAL] <= 1
                    if need_plastic or need_metal:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.ACCUMULATOR])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 0: self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'][0].idx), game.current_tick, num_workers_to_send, Resource.ACCUMULATOR))
                        if planet.my_workers > 0:
                            if need_plastic and need_metal:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['plastic'][0].idx), game.current_tick, planet.my_workers // 2, None))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, planet.my_workers - planet.my_workers // 2, None))
                            elif need_plastic: self.routes.append(Route(self.map.find_route(idx, my_planets['plastic'][0].idx), game.current_tick, planet.my_workers, None))
                            else: self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, planet.my_workers, None))
                        continue

                    if free_workers > 100 and len(self.routes) < 60:
                        if planet.resources[Resource.PLASTIC] < planet.resources[Resource.METAL]: self.routes.append(Route(self.map.find_route(idx, my_planets['organics'][0].idx), game.current_tick, free_workers, None))
                        else: self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, free_workers, None))
                        planet.my_workers -= free_workers
                    if planet.resources[Resource.ACCUMULATOR] > 0 and planet.my_workers > 0 and len(self.routes) < 65:
                        num_workers_to_send = min(planet.resources[Resource.ACCUMULATOR], planet.my_workers - 20)
                        if num_workers_to_send > 50:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'][0].idx), game.current_tick, num_workers_to_send, Resource.ACCUMULATOR))

                elif planet.mission == 'chip':
                    if planet.building is not None and planet.building.building_type != BuildingType.CHIP_FACTORY:
                        builds.append(BuildingAction(planet.idx, None))
                        continue
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CHIP_FACTORY))
                        if (len(self.need_resources_for_building) > 0 and planet.resources[Resource.STONE] >= 100) or (planet.resources[Resource.STONE] < 100 and planet.resources_in_flight[Resource.STONE] == 0):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    free_workers = planet.my_workers - (planet.resources[Resource.CHIP] + min(planet.resources[Resource.METAL] // 2, planet.resources[Resource.SILICON] // 2))
                    need_silicon = planet.resources[Resource.SILICON] <= 1
                    need_metal = planet.resources[Resource.METAL] <= 1
                    if need_silicon or need_metal:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.CHIP])
                        planet.my_workers -= num_workers_to_send
                        if num_workers_to_send > 0: self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'][0].idx), game.current_tick, num_workers_to_send, Resource.CHIP))
                        if planet.my_workers > 0:
                            if need_metal and need_silicon:
                                self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, planet.my_workers // 2, None))
                                self.routes.append(Route(self.map.find_route(idx, my_planets['sand'][0].idx), game.current_tick, planet.my_workers - planet.my_workers // 2, None))
                            elif need_metal: self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, planet.my_workers, None))
                            else: self.routes.append(Route(self.map.find_route(idx, my_planets['sand'][0].idx), game.current_tick, planet.my_workers, None))
                        continue

                    if free_workers > 50 and len(self.routes) < 65:
                        self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, free_workers // 2, None))
                        self.routes.append(Route(self.map.find_route(idx, my_planets['sand'][0].idx), game.current_tick, free_workers - free_workers//2, None))
                    if planet.resources[Resource.CHIP] > 0 and planet.my_workers > 0 and len(self.routes) < 65:
                        num_workers_to_send = min(planet.resources[Resource.CHIP], planet.my_workers - 20)
                        if num_workers_to_send > 50:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['replicator'][0].idx), game.current_tick, num_workers_to_send, Resource.CHIP))

                elif planet.mission == 'replicator':
                    if planet.building is not None and planet.building.building_type != BuildingType.REPLICATOR:
                        builds.append(BuildingAction(planet.idx, None))
                        continue
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.REPLICATOR))
                        if (len(self.need_resources_for_building) > 0 and planet.resources[Resource.STONE] >= 200) or (planet.resources[Resource.STONE] < 200 and planet.resources_in_flight[Resource.STONE] == 0):
                            self.routes.append(Route(self.map.find_route(idx, my_planets['stone'][0].idx), game.current_tick + 1, planet.my_workers, None))
                        continue

                    planet.my_workers -= game.building_properties[BuildingType.REPLICATOR].max_workers
                    if planet.my_workers > 10:
                        if planet.resources[Resource.ACCUMULATOR] > 50:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['sand'][0].idx), game.current_tick, planet.my_workers // 2, None))
                            planet.my_workers -= planet.my_workers // 2
                            self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, planet.my_workers, None))
                        else:
                            self.routes.append(Route(self.map.find_route(idx, my_planets['organics'][0].idx), game.current_tick, planet.my_workers // 3, None))
                            planet.my_workers -= planet.my_workers // 3
                            self.routes.append(Route(self.map.find_route(idx, my_planets['sand'][0].idx), game.current_tick, planet.my_workers // 2, None))
                            planet.my_workers -= planet.my_workers // 2
                            self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, planet.my_workers, None))

                elif planet.mission == 'free':
                    print(game.current_tick, planet.idx, len(game.flying_worker_groups))
                    self.routes.append(Route(self.map.find_route(idx, my_planets['ore'][0].idx), game.current_tick, planet.my_workers, None))

        self.update_routes()
        return Action(self.moves, builds)
