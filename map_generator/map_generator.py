"""
VOD: https://www.twitch.tv/videos/422999828
Notes:
Map Generator
- Gathering input data (map pool, how many matches/sets/games, popularity?)
- map generation 
- - for each game [choose x maps]
- print maps

bucket = {
    0: { # 0 times used 
    "sz": [Moray, Shellendorf]
    },
    1: { # 1 times used
    "sz": [MakoMart, Goby]
    }
}
 
"""

import json
from random import randint, shuffle


class Maplist:
    """Represent Splatoon 2 Maplist object."""

    def __init__(self, brackets: dict):
        """ Create a list of sets given the list of brackets

        :param dict brackets:
            keys: The name of the phase.
            values: A list, where the len is the number of sets.
                int values: The number of games in the set.
            e.g: {"Preliminaries": [3, 3, 3], "Finals": [5, 5]}
        """
        with open("pool.json") as file:
            self.pool = json.load(file)
        with open("popularity.json") as file:
            self.popularity = json.load(file)
        self.BACKLOG = min([len(subpool) for subpool in self.pool])
        self.sets = [s for g in brackets.values() for s in g]

    def generate(self) -> list:
        """Generates a maplist."""
        mode_list = list(self.pool.keys())
        shuffle(mode_list)
        mode_index = 0

        maplist = []
        buckets = {}
        map_history = []

        for maplist_round in range(len(self.sets)):
            round_maplist = []
            for _ in range(self.sets[maplist_round]):
                new_map = self.get_map(mode_list[mode_index], buckets, map_history)

                map_history.append(new_map)
                round_maplist.append((mode_list[mode_index], new_map))
                mode_index = (mode_index + 1) % len(mode_list)

            maplist.append(round_maplist)
        return maplist

    def get_map(self, mode: str, buckets: dict, map_history: list) -> str:
        """Return a map based on probability."""
        if self.popularity is None:
            if len(buckets) == 0:
                buckets[0] = self.pool.copy()

            if unused := self.unused_buckets(mode, buckets, map_history):
                return self.add_map(unused[0], mode, buckets, unused[1])

        else:
            popularity_pool = {mapname: votes for mapname, votes in self.popularity[mode].items() if mapname in self.pool[mode]}
            stage = self.random_map(popularity_pool)
            while not self.is_valid(stage, map_history):
                stage = self.random_map(popularity_pool)
            return stage

    def unused_buckets(self, mode: str, buckets: dict, map_history: list):
        """Iterate through all buckets to find one unused ones."""
        for num in range(len(buckets.keys())):
            shuffle(buckets[num][mode])
            for stage in buckets[num][mode]:
                if self.is_valid(stage, map_history):
                    return stage, num

    def is_valid(self, stage: str, map_history: list) -> bool:
        """Return true if map did not appear in the last BACKLOG chosen maps."""
        return stage not in map_history[-self.BACKLOG:]

    @staticmethod
    def add_map(stage: str, mode: str, buckets: dict, num: int) -> str:
        """Add map to bucket list and returns it."""
        if num + 1 not in buckets:
            buckets[num + 1] = {}
        if mode not in buckets[num + 1]:
            buckets[num + 1][mode] = []

        buckets[num][mode].remove(stage)
        buckets[num + 1][mode].append(stage)
        return stage

    @staticmethod
    def random_map(popularity_pool: dict) -> str:
        """Return a random map based on self.popularity count."""
        max_number = sum(popularity_pool.values())
        rand_number = randint(0, max_number)
        counter = 0

        for stage, votes in popularity_pool.items():
            counter += votes
            if counter >= rand_number:
                return stage

        return stage


def main():
    # Dictionary of all the phases
    brackets = {
        "Phase 1": [4, 4, 4, 4, 4, 4],
        "Phase 2": [5, 5],
        "Phase 3": [7]
    }
    # Create maplist object
    maplist = Maplist(brackets)
    # Set public versions of mode names
    mode_names = {
        "sz": "Splat Zones",
        "tc": "Tower Control",
        "rm": "Rainmaker",
        "cb": "Clam Blitz"
    }
    # Get the round names for each set
    round_names = []
    for name, games in brackets.items():
        for _ in range(len(games)):
            round_names.append(name)
    # Create message
    message = []
    for (i, game), round_name in zip(enumerate(maplist.generate()), round_names):
        message.append(f"\n{round_name} Round {i+1}:")
        for mode, stage in game:
            message.append(f"{mode_names[mode]}: {stage}")
    # Print message
    print("\n".join(message))


if __name__ == "__main__":
    main()
