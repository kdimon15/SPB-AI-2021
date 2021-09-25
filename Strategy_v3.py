from model import *
import math


def find_distance(pt1, pt2):  # Найти расстояние между точками
    return abs(pt1.x - pt2.x) + abs(pt1.y - pt2.y)


class My_Planet:
    def __init__(self, planet: Planet, idx, my_index):
        self.idx = idx
        self.resource = planet.harvestable_resource
        self.resources_in_flight = {}
        self.x = planet.x
        self.y = planet.y
        self.planet = planet
        self.my_workers = 0
        self.enemy_workers = 0
        self.workers_in_flight = 0
        self.my_index = my_index
        self.count_workers()

        if self.resource == Resource.STONE:
            self.planet_mission = 'stone'
        elif self.resource == Resource.ORE:
            self.planet_mission = 'ore'
        elif self.resource == Resource.SAND:
            self.planet_mission = 'sand'
        elif self.resource == Resource.ORGANICS:
            self.planet_mission = 'organics'
        else:
            self.planet_mission = 'free'

    def count_workers(self):  # Посчитать кол-во рабочих на планете
        for work_gr in self.planet.worker_groups:
            if work_gr.player_index == self.my_index:
                self.my_workers += work_gr.number
            else:
                self.enemy_workers += work_gr.number

    def update(self, planet):
        self.my_workers = 0
        self.enemy_workers = 0
        self.resources_in_flight = {}
        self.workers_in_flight = 0
        self.planet = planet
        self.count_workers()

    def __str__(self):  # Что будет, если сделать str(My_Planet) (для print)
        return f"{self.x} {self.y}"


class MyStrategy:
    def __init__(self):
        self.planets = {}
        self.special_planets = {'stone': [], 'ore': [], 'sand': [], 'organics': [], 'free': []}
        self.idx_starter_planet = 0

    def initialize(self, game):  # Делаем инициализацию планет
        self.idx_starter_planet = None
        for idx, planet in enumerate(game.planets):
            self.planets[idx] = My_Planet(planet, idx, game.my_index)
            self.special_planets[self.planets[idx].planet_mission].append(idx)
            if self.planets[idx].my_workers > 0:
                self.idx_starter_planet = idx
        for tool in ['plastic', 'metal', 'silicon', 'accumulator', 'chip', 'replicator']:
            dist, closest_free_planet = self.find_closest_planet(self.planets[self.idx_starter_planet], 'free')
            self.planets[closest_free_planet.idx].planet_mission = tool
            self.special_planets[tool] = [closest_free_planet.idx]

    def update(self, game):
        for idx, planet in enumerate(game.planets):
            self.planets[idx].update(planet)

        for fly_group in game.flying_worker_groups:
            if fly_group.player_index == game.my_index:
                self.planets[fly_group.target_planet].workers_in_flight += fly_group.number
                if fly_group.resource in self.planets[fly_group.target_planet].resources_in_flight:
                    self.planets[fly_group.target_planet].resources_in_flight[fly_group.resource] += fly_group.number
                else:
                    self.planets[fly_group.target_planet].resources_in_flight[fly_group.resource] = fly_group.number

    def find_closest_planet(self, pl, type_of_planet):
        closest_dist, close_planet = math.inf, None
        for planet_idx, planet in self.planets.items():
            if not planet.enemy_workers and planet.planet_mission == type_of_planet:
                dist = find_distance(planet, pl)
                if dist < closest_dist:
                    closest_dist = dist
                    close_planet = planet
        return closest_dist, close_planet

    def find_planet_from_list(self, pl, list_of_planets_idxs):
        closest_dist, close_planet = math.inf, None
        for idx, planet in self.planets.items():
            if planet.idx in list_of_planets_idxs:
                dist = find_distance(planet, pl)
                if dist < closest_dist:
                    closest_dist = dist
                    close_planet = planet
        return close_planet

    def get_action(self, game: Game) -> Action:
        if game.current_tick == 0:
            self.initialize(game)
        else:
            self.update(game)
        moves, builds = [], []

        stone_planet = self.planets[self.idx_starter_planet]
        ore_planet = self.find_planet_from_list(self.planets[self.idx_starter_planet], self.special_planets['ore'])
        sand_planet = self.find_planet_from_list(self.planets[self.idx_starter_planet], self.special_planets['sand'])
        organics_planet = self.find_planet_from_list(self.planets[self.idx_starter_planet], self.special_planets['organics'])
        metal_planet = self.find_planet_from_list(self.planets[self.idx_starter_planet], self.special_planets['metal'])
        plastic_planet = self.find_planet_from_list(self.planets[self.idx_starter_planet], self.special_planets['plastic'])
        silicon_planet = self.find_planet_from_list(self.planets[self.idx_starter_planet], self.special_planets['silicon'])
        accumulator_planet = self.find_planet_from_list(self.planets[self.idx_starter_planet], self.special_planets['accumulator'])
        chip_planet = self.find_planet_from_list(self.planets[self.idx_starter_planet], self.special_planets['chip'])
        replicator_planet = self.find_planet_from_list(self.planets[self.idx_starter_planet], self.special_planets['replicator'])

        if game.current_tick > 900:
            for idx, planet in self.planets.items():
                moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))
            return Action(moves, builds)

        for idx, planet in self.planets.items():
            if planet.my_workers >= 0:

                if planet.planet_mission == 'stone':
                    if planet.my_workers > game.max_builders or Resource.STONE in planet.planet.resources:
                        if ore_planet.my_workers + ore_planet.workers_in_flight < 150 and ore_planet.planet.building is None:
                            moves.append(MoveAction(idx, ore_planet.idx, 100, Resource.STONE))
                        elif sand_planet.my_workers + sand_planet.workers_in_flight < 150 and sand_planet.planet.building is None:
                            moves.append(MoveAction(idx, sand_planet.idx, 100, Resource.STONE))
                        elif organics_planet.my_workers + organics_planet.workers_in_flight < 150 and organics_planet.planet.building is None:
                            moves.append(MoveAction(idx, organics_planet.idx, 100, Resource.STONE))
                        elif metal_planet.my_workers + metal_planet.workers_in_flight < 100 and metal_planet.planet.building is None:
                            moves.append(MoveAction(idx, metal_planet.idx, 100, Resource.STONE))
                        elif plastic_planet.my_workers + plastic_planet.workers_in_flight < 100 and plastic_planet.planet.building is None:
                            moves.append(MoveAction(idx, plastic_planet.idx, 100, Resource.STONE))
                        elif silicon_planet.my_workers + silicon_planet.workers_in_flight < 100 and silicon_planet.planet.building is None:
                            moves.append(MoveAction(idx, silicon_planet.idx, 100, Resource.STONE))
                        elif accumulator_planet.my_workers + accumulator_planet.workers_in_flight < 100 and accumulator_planet.planet.building is None:
                            moves.append(MoveAction(idx, accumulator_planet.idx, 100, Resource.STONE))
                        elif chip_planet.my_workers + chip_planet.workers_in_flight < 100 and chip_planet.planet.building is None:
                            moves.append(MoveAction(idx, chip_planet.idx, 100, Resource.STONE))
                        elif replicator_planet.my_workers + replicator_planet.workers_in_flight < 200 and replicator_planet.planet.building is None:
                            moves.append(MoveAction(idx, replicator_planet.idx, 100, Resource.STONE))
                        else:
                            moves.append(MoveAction(idx, ore_planet.idx, 50, None))

                elif planet.planet_mission == 'ore':
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.MINES))
                    elif Resource.ORE in planet.planet.resources and planet.planet.resources[Resource.ORE] > 100:
                        num_workers_to_send = min(planet.my_workers, 100)
                        moves.append(MoveAction(idx, metal_planet.idx, num_workers_to_send, Resource.ORE))
                    elif planet.workers_in_flight == 0 and planet.planet.building is None:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

                elif planet.planet_mission == 'sand':
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CAREER))
                    elif Resource.SAND in planet.planet.resources and planet.planet.resources[Resource.SAND] >= 100:
                        num_workers_to_send = min(planet.my_workers, 100)
                        moves.append(MoveAction(idx, silicon_planet.idx, num_workers_to_send, Resource.SAND))
                    elif planet.workers_in_flight == 0 and planet.planet.building is None:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

                elif planet.planet_mission == 'organics':
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FARM))
                    elif Resource.ORGANICS in planet.planet.resources and planet.planet.resources[Resource.ORGANICS] >= 100:
                        num_workers_to_send = min(planet.planet.resources[Resource.ORGANICS], 100)
                        moves.append(MoveAction(idx, plastic_planet.idx, num_workers_to_send, Resource.ORGANICS))
                    elif planet.workers_in_flight == 0 and planet.planet.building is None:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

                elif planet.planet_mission == 'metal':
                    need_ore = Resource.ORE not in planet.planet.resources or planet.planet.resources[Resource.ORE] == 1
                    if planet.my_workers and planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FOUNDRY))
                    elif (Resource.METAL in planet.planet.resources and planet.planet.resources[Resource.METAL] > 5) and (need_ore or planet.planet.resources[Resource.METAL] > 200):
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.METAL], 150)
                        if Resource.METAL in replicator_planet.planet.resources and replicator_planet.planet.resources[Resource.METAL] > 100:
                            moves.append(MoveAction(idx, accumulator_planet.idx, num_workers_to_send // 2, Resource.METAL))
                            moves.append(MoveAction(idx, chip_planet.idx, num_workers_to_send // 2, Resource.METAL))
                        else:
                            moves.append(MoveAction(idx, accumulator_planet.idx, num_workers_to_send // 3, Resource.METAL))
                            moves.append(MoveAction(idx, chip_planet.idx, num_workers_to_send // 3, Resource.METAL))
                            moves.append(MoveAction(idx, replicator_planet.idx, num_workers_to_send // 3, Resource.METAL))
                    elif planet.my_workers > 0 and (Resource.ORE not in planet.planet.resources or planet.planet.resources[Resource.ORE] == 1):
                        moves.append(MoveAction(idx, ore_planet.idx, planet.my_workers, None))
                    if (planet.planet.building is None and planet.my_workers >= 100) or replicator_planet.planet.building is None:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

                elif planet.planet_mission == 'silicon':
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FURNACE))
                    elif Resource.SILICON in planet.planet.resources and (Resource.SAND not in planet.planet.resources or planet.planet.resources[Resource.SAND] == 1):
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.SILICON], 50)
                        moves.append(MoveAction(idx, chip_planet.idx, num_workers_to_send, Resource.SILICON))
                    elif Resource.SAND not in planet.planet.resources or planet.planet.resources[Resource.SAND] == 1:
                        moves.append(MoveAction(idx, sand_planet.idx, planet.my_workers, None))
                    if planet.planet.building is None and planet.my_workers >= 100:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

                elif planet.planet_mission == 'plastic':
                    need_organics = Resource.ORGANICS not in planet.planet.resources or planet.planet.resources[Resource.ORGANICS] == 1
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.BIOREACTOR))
                    elif Resource.PLASTIC in planet.planet.resources and need_organics:
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.PLASTIC], 50)
                        moves.append(MoveAction(idx, accumulator_planet.idx, num_workers_to_send, Resource.PLASTIC))
                    elif need_organics:
                        moves.append(MoveAction(idx, organics_planet.idx, planet.my_workers, None))

                    if planet.planet.building is None and planet.my_workers >= 100:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

                elif planet.planet_mission == 'accumulator':
                    need_plastic = Resource.PLASTIC not in planet.planet.resources or planet.planet.resources[Resource.PLASTIC] == 1
                    need_metal = Resource.METAL not in planet.planet.resources or planet.planet.resources[Resource.METAL] == 1
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.ACCUMULATOR_FACTORY))
                    elif Resource.ACCUMULATOR in planet.planet.resources and (need_plastic or need_metal):
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.ACCUMULATOR], 50)
                        moves.append(MoveAction(idx, replicator_planet.idx, num_workers_to_send, Resource.ACCUMULATOR))
                    elif need_plastic and need_metal:
                        moves.append(MoveAction(idx, plastic_planet.idx, planet.my_workers//2, None))
                        moves.append(MoveAction(idx, metal_planet.idx, planet.my_workers//2, None))
                    elif need_plastic:
                        moves.append(MoveAction(idx, plastic_planet.idx, planet.my_workers, None))
                    elif need_metal:
                        moves.append(MoveAction(idx, metal_planet.idx, planet.my_workers, None))

                elif planet.planet_mission == 'chip':
                    need_silicon = Resource.SILICON not in planet.planet.resources or planet.planet.resources[Resource.SILICON] == 1
                    need_metal = Resource.METAL not in planet.planet.resources or planet.planet.resources[Resource.METAL] == 1
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CHIP_FACTORY))
                    elif Resource.CHIP in planet.planet.resources and (need_silicon or need_metal):
                        num_workers_to_send = min(planet.my_workers, planet.planet.resources[Resource.CHIP], 50)
                        moves.append(MoveAction(idx, replicator_planet.idx, num_workers_to_send, Resource.CHIP))
                    elif need_silicon and need_metal:
                        moves.append(MoveAction(idx, silicon_planet.idx, planet.my_workers // 2, None))
                        moves.append(MoveAction(idx, metal_planet.idx, planet.my_workers // 2, None))
                    elif need_silicon:
                        moves.append(MoveAction(idx, silicon_planet.idx, min(planet.my_workers, 50), None))
                    elif need_metal:
                        moves.append(MoveAction(idx, metal_planet.idx, min(planet.my_workers, 50), None))

                    if planet.planet.building is None and planet.my_workers >= 200:
                        moves.append(MoveAction(idx, stone_planet.idx, planet.my_workers, None))

                elif planet.planet_mission == 'replicator':
                    need_chip = Resource.CHIP not in planet.planet.resources or planet.planet.resources[Resource.CHIP] == 1
                    need_metal = Resource.METAL not in planet.planet.resources or planet.planet.resources[Resource.METAL] == 1
                    need_accumulator = Resource.ACCUMULATOR not in planet.planet.resources or planet.planet.resources[Resource.ACCUMULATOR] == 1
                    if planet.planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.REPLICATOR))
                    elif need_chip or need_metal or need_accumulator:
                        if Resource.ACCUMULATOR in planet.planet.resources and planet.planet.resources[Resource.ACCUMULATOR] > 100:
                            moves.append(MoveAction(idx, sand_planet.idx, planet.my_workers // 2, None))
                            moves.append(MoveAction(idx, chip_planet.idx, planet.my_workers // 2, None))
                        else:
                            moves.append(MoveAction(idx, organics_planet.idx, planet.my_workers // 3, None))
                            moves.append(MoveAction(idx, sand_planet.idx, planet.my_workers // 3, None))
                            moves.append(MoveAction(idx, ore_planet.idx, planet.my_workers // 3, None))

        return Action(moves, builds)