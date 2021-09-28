from model import *
from My_Planet import MyPlanet
from tools import distance, find_closest_planet_by_type, all_types_of_planets

"""
TODO:

- Сделать свою систему перемещиний
- Более эффективно определять кол-во юнитов для отправки
- Отправлять более одного отряда за тик
- Учитывать прилетающих юнитов при отправке
"""


class MyStrategy:
    def __init__(self):
        self.planets = {}
        self.important_planets = {}
        self.game = None
        self.starter_planet_idx = 0

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

        avg_pos = ((self.planets[self.important_planets['ore']].x + self.planets[self.important_planets['sand']].x +
                    self.planets[self.important_planets['organics']].x) / 3,
                   (self.planets[self.important_planets['ore']].y + self.planets[self.important_planets['sand']].y +
                    self.planets[self.important_planets['organics']].y) / 3)

        for tool in ['replicator', 'accumulator', 'chip', 'metal', 'plastic', 'silicon']:
            planet_idx = find_closest_planet_by_type(avg_pos, 'free', self.planets)
            self.important_planets[tool] = planet_idx
            self.planets[planet_idx].mission = tool

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

        if game.current_tick == 0: self.initialize()
        else: self.update()

        my_planets = {tool: self.planets[self.important_planets[tool]] for tool in all_types_of_planets}

        if game.current_tick > 950:
            for idx, planet in self.planets.items():
                moves.append(MoveAction(idx, my_planets['replicator'].idx, planet.my_workers, None))
            return Action(moves, builds)

        for idx, planet in self.planets.items():
            if planet.my_workers > 0:

                if planet.mission == 'stone':
                    if planet.resources[Resource.STONE] > 0:
                        if my_planets['ore'].my_workers + my_planets['ore'].workers_in_flight < 100 and my_planets['ore'].building is None:
                            moves.append(MoveAction(idx, my_planets['ore'].idx, min(planet.my_workers, planet.resources[Resource.STONE]), Resource.STONE))
                        elif my_planets['sand'].my_workers + my_planets['sand'].workers_in_flight < 100 and my_planets['sand'].building is None:
                            moves.append(MoveAction(idx, my_planets['sand'].idx, min(planet.my_workers, planet.resources[Resource.STONE]), Resource.STONE))
                        elif my_planets['organics'].my_workers + my_planets['organics'].workers_in_flight < 100 and my_planets['organics'].building is None:
                            moves.append(MoveAction(idx, my_planets['organics'].idx, min(planet.my_workers, planet.resources[Resource.STONE]), Resource.STONE))
                        elif my_planets['metal'].my_workers + my_planets['metal'].workers_in_flight < 100 and my_planets['metal'].building is None:
                            moves.append(MoveAction(idx, my_planets['metal'].idx, min(planet.my_workers, planet.resources[Resource.STONE]), Resource.STONE))
                        elif my_planets['plastic'].my_workers + my_planets['plastic'].workers_in_flight < 100 and my_planets['plastic'].building is None:
                            moves.append(MoveAction(idx, my_planets['plastic'].idx, min(planet.my_workers, planet.resources[Resource.STONE]), Resource.STONE))
                        elif my_planets['silicon'].my_workers + my_planets['silicon'].workers_in_flight < 100 and my_planets['silicon'].building is None:
                            moves.append(MoveAction(idx, my_planets['silicon'].idx, min(planet.my_workers, planet.resources[Resource.STONE]), Resource.STONE))
                        elif my_planets['accumulator'].my_workers + my_planets['accumulator'].workers_in_flight < 100 and my_planets['accumulator'].building is None:
                            moves.append(MoveAction(idx, my_planets['accumulator'].idx, min(planet.my_workers, planet.resources[Resource.STONE]), Resource.STONE))
                        elif my_planets['chip'].my_workers + my_planets['chip'].workers_in_flight < 100 and my_planets['chip'].building is None:
                            moves.append(MoveAction(idx, my_planets['chip'].idx, min(planet.my_workers, planet.resources[Resource.STONE]), Resource.STONE))
                        elif my_planets['replicator'].building is None:
                            moves.append(MoveAction(idx, my_planets['replicator'].idx, min(planet.my_workers, planet.resources[Resource.STONE]), Resource.STONE))

                elif planet.mission == 'ore':
                    free_workers = planet.my_workers - game.max_builders
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.MINES))
                    elif planet.resources[Resource.ORE] > planet.my_workers:
                        moves.append(MoveAction(idx, my_planets['metal'].idx, planet.my_workers, Resource.ORE))
                    elif free_workers > 0:
                        moves.append(MoveAction(idx, my_planets['metal'].idx, min(free_workers, planet.resources[Resource.ORE]), Resource.ORE))

                elif planet.mission == 'sand':
                    free_workers = planet.my_workers - game.max_builders
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CAREER))
                    elif planet.resources[Resource.SAND] > planet.my_workers:
                        moves.append(MoveAction(idx, my_planets['silicon'].idx, planet.my_workers, Resource.SAND))
                    elif free_workers > 0:
                        moves.append(MoveAction(idx, my_planets['silicon'].idx, min(free_workers, planet.resources[Resource.SAND]), Resource.SAND))

                elif planet.mission == 'organics':
                    free_workers = planet.my_workers - game.max_builders
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FARM))
                    elif planet.resources[Resource.ORGANICS] > planet.my_workers:
                        moves.append(MoveAction(idx, my_planets['plastic'].idx, planet.my_workers, Resource.ORGANICS))
                    elif free_workers > 0:
                        moves.append(MoveAction(idx, my_planets['plastic'].idx, min(free_workers, planet.resources[Resource.ORGANICS]), Resource.ORGANICS))

                elif planet.mission == 'metal':
                    need_ore = planet.resources[Resource.ORE] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FOUNDRY))
                    elif planet.resources[Resource.METAL] > 5 and (need_ore or planet.resources[Resource.METAL] > 200):
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.METAL])
                        need_replicator = my_planets['replicator'].resources[Resource.METAL] < 100
                        need_accum = my_planets['replicator'].resources[Resource.ACCUMULATOR] < 50
                        if need_replicator and need_accum:
                            moves.append(MoveAction(idx, my_planets['accumulator'].idx, num_workers_to_send // 3, Resource.METAL))
                            moves.append(MoveAction(idx, my_planets['chip'].idx, num_workers_to_send // 3, Resource.METAL))
                            moves.append(MoveAction(idx, my_planets['replicator'].idx, num_workers_to_send // 3, Resource.METAL))
                        elif need_accum:
                            moves.append(MoveAction(idx, my_planets['accumulator'].idx, num_workers_to_send // 2, Resource.METAL))
                            moves.append(MoveAction(idx, my_planets['chip'].idx, num_workers_to_send // 2, Resource.METAL))
                        elif need_replicator:
                            moves.append(MoveAction(idx, my_planets['replicator'].idx, num_workers_to_send // 2, Resource.METAL))
                            moves.append(MoveAction(idx, my_planets['chip'].idx, num_workers_to_send // 2, Resource.METAL))
                        else:
                            moves.append(MoveAction(idx, my_planets['chip'].idx, num_workers_to_send, Resource.METAL))
                    elif need_ore:
                        moves.append(MoveAction(idx, my_planets['ore'].idx, planet.my_workers, None))

                elif planet.mission == 'silicon':
                    need_sand = planet.resources[Resource.SAND] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.FURNACE))
                    elif planet.resources[Resource.SILICON] > 0 and need_sand:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.SILICON])
                        moves.append(MoveAction(idx, my_planets['chip'].idx, num_workers_to_send, Resource.SILICON))
                    elif need_sand:
                        moves.append(MoveAction(idx, my_planets['sand'].idx, planet.my_workers, None))

                elif planet.mission == 'plastic':
                    need_organics = planet.resources[Resource.ORGANICS] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.BIOREACTOR))
                    elif planet.resources[Resource.PLASTIC] > 0 and need_organics:
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.PLASTIC])
                        moves.append(MoveAction(idx, my_planets['accumulator'].idx, num_workers_to_send, Resource.PLASTIC))
                    elif need_organics:
                        moves.append(MoveAction(idx, my_planets['organics'].idx, planet.my_workers, None))

                elif planet.mission == 'accumulator':
                    need_plastic = planet.resources[Resource.PLASTIC] <= 1
                    need_metal = planet.resources[Resource.METAL] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.ACCUMULATOR_FACTORY))
                    elif planet.resources[Resource.ACCUMULATOR] > 0 and (need_plastic or need_metal):
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.ACCUMULATOR])
                        moves.append(MoveAction(idx, my_planets['replicator'].idx, num_workers_to_send, Resource.ACCUMULATOR))
                    elif need_plastic and need_metal:
                        moves.append(MoveAction(idx, my_planets['plastic'].idx, planet.my_workers//2, None))
                        moves.append(MoveAction(idx, my_planets['metal'].idx, planet.my_workers//2, None))
                    elif need_plastic:
                        moves.append(MoveAction(idx, my_planets['plastic'].idx, planet.my_workers, None))
                    elif need_metal:
                        moves.append(MoveAction(idx, my_planets['metal'].idx, planet.my_workers, None))

                elif planet.mission == 'chip':
                    need_silicon = planet.resources[Resource.SILICON] <= 1
                    need_metal = planet.resources[Resource.METAL] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.CHIP_FACTORY))
                    elif planet.resources[Resource.CHIP] > 0 and (need_silicon or need_metal):
                        num_workers_to_send = min(planet.my_workers, planet.resources[Resource.CHIP])
                        moves.append(MoveAction(idx, my_planets['replicator'].idx, num_workers_to_send, Resource.CHIP))
                    elif need_silicon and need_metal:
                        moves.append(MoveAction(idx, my_planets['silicon'].idx, planet.my_workers // 2, None))
                        moves.append(MoveAction(idx, my_planets['metal'].idx, planet.my_workers // 2, None))
                    elif need_silicon:
                        moves.append(MoveAction(idx, my_planets['silicon'].idx, planet.my_workers, None))
                    elif need_metal:
                        moves.append(MoveAction(idx, my_planets['metal'].idx, planet.my_workers, None))

                elif planet.mission == 'replicator':
                    need_chip = planet.resources[Resource.CHIP] <= 1
                    need_metal = planet.resources[Resource.METAL] <= 1
                    need_accumulator = planet.resources[Resource.ACCUMULATOR] <= 1
                    if planet.building is None:
                        builds.append(BuildingAction(planet.idx, BuildingType.REPLICATOR))
                    elif need_chip or need_metal or need_accumulator:
                        if planet.resources[Resource.ACCUMULATOR] > 50:
                            moves.append(MoveAction(idx, my_planets['sand'].idx, planet.my_workers // 2, None))
                            moves.append(MoveAction(idx, my_planets['metal'].idx, planet.my_workers // 2, None))
                        else:
                            moves.append(MoveAction(idx, my_planets['organics'].idx, planet.my_workers // 3, None))
                            moves.append(MoveAction(idx, my_planets['sand'].idx, planet.my_workers // 3, None))
                            moves.append(MoveAction(idx, my_planets['ore'].idx, planet.my_workers // 3, None))

        return Action(moves, builds)
