'''
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
 
'''
import json 
from random import randint, shuffle

BACKLOG = 6

def map_generation(map_pool: dict, games: list, popularity = None) -> list:
    '''
    Generates a maplist.
    Params:
    - map_pool: map pool to work with as dictionary. Keys are "sz", "tc", "rm", "cb" preferably
    - games: list of ints. Each entry is one round of x maps.
    - popularity: popularity list, dict of [mode][map] -> votes 
    '''
    # get all modes 
    mode_list = list(map_pool.keys())
    mode_index = 0
    shuffle(mode_list) # for randomness 
    
    maplist = [] # will be returned 
    buckets = {} # see example above
    
    map_history = [] # used maps
    
    # for each round 
    for round in range(len(games)):
        # create a round maplist
        round_maplist = []
        # for each map to play 
        for game in range(games[round]):
            # if poopularity is empty
            if popularity is None:
                # then use the normal algorithm
                new_map = get_map(map_pool, mode_list[mode_index], buckets, map_history)
            else: 
                # otherwise the popularity one 
                new_map = get_map_poopular(map_pool, mode_list[mode_index], popularity, map_history)
                
            # add current map to history 
            map_history.append(new_map)
            # add map to round maplist
            round_maplist.append((mode_list[mode_index], new_map))
            # increase mode counter 
            mode_index = (mode_index + 1) % len(mode_list)
            
        # add round maplist to maplist 
        maplist.append(round_maplist)
        
    return maplist
    
def is_valid(map: str, map_history: list) -> bool:
    '''
    Returns true if map did not appear in the last BACKLOG chosen maps 
    '''
    return map not in map_history[-BACKLOG:]
    
def add_and_return_map(map: str, mode: str, buckets: dict, bucket_num: int) -> str:
    '''
    Adds map to bucket list and returns it 
    '''
    # if next bucket doesntr exists then create it  
    if bucket_num + 1 not in buckets:
        buckets[bucket_num + 1] = {}
    # if mode bucket doesnt exist then 
    if mode not in buckets[bucket_num + 1]:
        buckets[bucket_num + 1][mode] = []
        
    # add bucket to list 
    buckets[bucket_num][mode].remove(map)
    buckets[bucket_num + 1][mode].append(map)
    return map 
   
def random_map(popularity_list: list ) -> str:
    '''
    Returns a random map based on popularity count 
    '''
    # get max number 
    max_number = sum(popularity_list.values())
    # ger random number 
    rand_int = randint(0, max_number)
    counter = 0
    # get the map that is in the number interval 
    for map, votes in popularity_list.items():
        counter += votes
        if counter >= rand_int:
            return map
    
    return map

   
def get_map_poopular(map_pool: dict, mode: str, popularity: dict, map_history: list) -> str:
    '''
    returns a map based on popularity probability.
    '''
    popularity_map_pool = {mapname: votes for mapname, votes in popularity[mode].items() if mapname in map_pool[mode]}
    map = random_map(popularity_map_pool)
    # while not a good map, repeat 
    while not is_valid(map, map_history):
        map = random_map(popularity_map_pool)
    return map
   
def get_map(map_pool: dict, mode: str, buckets: dict, map_history: list) ->str:
    '''
    returns the earliest map that fits "is valid"
    '''
    # initiate buckets 
    if len(buckets) == 0:
        buckets[0] = map_pool.copy()

    # iterate through all buckets to find one unused ones 
    for bucket_num in range(len(buckets.keys())):
        shuffle(buckets[bucket_num][mode])
        for map in buckets[bucket_num][mode]:
            if is_valid(map, map_history):
                return add_and_return_map(map, mode, buckets, bucket_num)

if __name__ == "__main__":  
    xrank_pool = json.load(open("xrank.json"))
    popularity = json.load(open("popularity.json")) 
    BACKLOG = min([len(pool) for pool in xrank_pool])
    sets = [4, 4, 4, 4, 4, 4, 5, 5, 7]

    maplist = map_generation(xrank_pool, sets, popularity)
    i = 0
    mode_names = {"sz": "Splat Zones", "tc": "Tower Control", "rm": "Rainmaker", "cb": "Clam Blitz"}
    for game in maplist:
        i += 1
        print(f"Match {i}")
        k = 0
        for mode, map in game:
            k += 1
            print (f"Game {k}:", mode_names[mode], "on", map)                   