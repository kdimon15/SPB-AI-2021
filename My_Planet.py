from model import *
from tools import all_resources

class MyPlanet:
    def __init__(self, planet: Planet, idx: int, my_index):
        self.building = planet.building
        self.idx = idx
        self.planet = planet
        self.harvestable_resource = planet.harvestable_resource
        self.x = planet.x
        self.y = planet.y
        self.pos = (planet.x, planet.y)
        self.my_workers = 0
        self.enemy_workers = 0
        self.resources_in_flight = {}
        self.workers_in_flight = 0
        self.my_index = my_index
        self.count_workers()

        self.resources = {res: 0 for res in all_resources}

        if self.harvestable_resource == Resource.STONE:
            self.mission = 'stone'
        elif self.harvestable_resource == Resource.ORE:
            self.mission = 'ore'
        elif self.harvestable_resource == Resource.SAND:
            self.mission = 'sand'
        elif self.harvestable_resource == Resource.ORGANICS:
            self.mission = 'organics'
        else:
            self.mission = 'free'

    def count_workers(self):
        self.my_workers, self.enemy_workers = 0, 0
        for work_gr in self.planet.worker_groups:
            if work_gr.player_index == self.my_index:
                self.my_workers += work_gr.number
            else:
                self.enemy_workers += work_gr.number

    def update(self, planet):
        self.resources_in_flight = {res: 0 for res in all_resources}
        self.resources = {res: 0 for res in all_resources}
        for res, amount in planet.resources.items():
            self.resources[res] += amount
        self.workers_in_flight = 0
        self.planet = planet
        self.building = planet.building
        self.count_workers()
