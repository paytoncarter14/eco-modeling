import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import pathlib
import imageio
import glob

scenarios = [
    {
        'name': 'default',
        'num_rivers': 3,
        'num_lakes': 8,
        'num_species': 10,
        'lentic_min_flight_radius': 5,
        'lentic_max_flight_radius': 20,
        'lotic_min_flight_radius': 5,
        'lotic_max_flight_radius': 50
    },
    {
        'name': 'lots_of_water',
        'num_rivers': 8,
        'num_lakes': 20,
        'num_species': 10,
        'lentic_min_flight_radius': 5,
        'lentic_max_flight_radius': 20,
        'lotic_min_flight_radius': 5,
        'lotic_max_flight_radius': 50
    },
    {
        'name': 'little_water',
        'num_rivers': 1,
        'num_lakes': 5,
        'num_species': 10,
        'lentic_min_flight_radius': 5,
        'lentic_max_flight_radius': 20,
        'lotic_min_flight_radius': 5,
        'lotic_max_flight_radius': 50
    },
    {
        'name': 'far_flight_radius',
        'num_rivers': 3,
        'num_lakes': 8,
        'num_species': 10,
        'lentic_min_flight_radius': 10,
        'lentic_max_flight_radius': 80,
        'lotic_min_flight_radius': 20,
        'lotic_max_flight_radius': 90
    },
    {
        'name': 'near_flight_radius',
        'num_rivers': 3,
        'num_lakes': 8,
        'num_species': 10,
        'lentic_min_flight_radius': 2,
        'lentic_max_flight_radius': 10,
        'lotic_min_flight_radius': 5,
        'lotic_max_flight_radius': 20
    },
    {
        'name': 'many_species',
        'num_rivers': 3,
        'num_lakes': 8,
        'num_species': 30,
        'lentic_min_flight_radius': 5,
        'lentic_max_flight_radius': 20,
        'lotic_min_flight_radius': 5,
        'lotic_max_flight_radius': 50
    },
    {
        'name': 'few_species',
        'num_rivers': 3,
        'num_lakes': 8,
        'num_species': 3,
        'lentic_min_flight_radius': 5,
        'lentic_max_flight_radius': 20,
        'lotic_min_flight_radius': 5,
        'lotic_max_flight_radius': 50
    },
]

for scenario in scenarios:

    print(f'Doing scenario {scenario["name"]}')

    # parameters
    world_size = 200
    num_rivers = scenario['num_rivers']
    min_river_width = 2
    max_river_width = 10
    num_lakes = scenario['num_lakes']
    min_lake_radius = 5
    max_lake_radius = 20
    num_species = scenario['num_species']
    lentic_min_flight_radius = scenario['lentic_min_flight_radius']
    lentic_max_flight_radius = scenario['lentic_max_flight_radius']
    lotic_min_flight_radius = scenario['lotic_min_flight_radius']
    lotic_max_flight_radius = scenario['lotic_max_flight_radius']
    ticks = 20
    
    # initialize empty world
    # 0 = land, 1 = lotic (river), 2 = lentic (lake)
    world = np.zeros((world_size, world_size), dtype=int)
    
    # make rivers
    for i in range(num_rivers):
        coord = random.randint(0, world_size-1)
        width = random.randint(min_river_width, max_river_width)
        coord_min = coord-width
        coord_max = coord+width
        if random.randint(0,1) == 0:
            world[coord_min:coord_max] = 1
        else:
            world[:, coord_min:coord_max] = 1
    # make lakes
    for i in range(num_lakes):
        radius = random.randint(min_lake_radius, max_lake_radius)
        origin_x = random.randint(0, world_size-1)
        origin_y = random.randint(0, world_size-1)
        x_min = origin_x - radius
        x_max = origin_x + radius
        y_min = origin_y - radius
        y_max = origin_y + radius
        world[y_min:y_max, x_min:x_max] = 2
    
    # plot world
    fig, ax = plt.subplots()
    im = ax.imshow(world)
    
    # populate world with species
    
    def populate(world_value):
        species = [np.zeros((world_size, world_size), dtype=int) for i in range(num_species)]
        valid = np.where(world == world_value)
        for i in range(num_species):
            seed_index = random.randint(0, len(valid[0]))
            seed = (valid[0][seed_index], valid[1][seed_index])
            species[i][seed[0], seed[1]] = 1
        return species
    
    lotic = populate(1)
    lentic = populate(2)
    
    lentic_flight_radii = [random.randint(lentic_min_flight_radius, lentic_max_flight_radius) for x in range(num_species)]
    lotic_flight_radii = [random.randint(lotic_min_flight_radius, lotic_max_flight_radius) for x in range(num_species)]
    
    fig, ax = plt.subplots()
    im = ax.imshow(world + sum(lentic) + sum(lotic))
    
    # main dispersal cycle
    
    pathlib.Path(f'{scenario["name"]}/output_images').mkdir(exist_ok=True, parents=True)
    
    pct_water_tiles_occupied = []
    pct_world_covered = []
    
    def disperse(species, flight_radii, world_value):
        for j in range(num_species):
            species_coords = np.where(species[j] == 1)
            for k in range(len(species_coords[0])):
                random_flight_coord_x = random.randint(species_coords[1][k]-flight_radii[j], species_coords[1][k]+flight_radii[j])
                random_flight_coord_y = random.randint(species_coords[0][k]-flight_radii[j], species_coords[0][k]+flight_radii[j])
    
                if random_flight_coord_x <= 0:
                    random_flight_coord_x = 0
                if random_flight_coord_y <= 0:
                    random_flight_coord_y = 0
                if random_flight_coord_x >= world_size:
                    random_flight_coord_x = world_size-1
                if random_flight_coord_y >= world_size:
                    random_flight_coord_y = world_size-1
    
                world_coord_value = world[random_flight_coord_y, random_flight_coord_x]
                if world_coord_value == world_value:
                    species[j][random_flight_coord_y, random_flight_coord_x] = 1
    
    for i in range(ticks):
        disperse(lotic, lotic_flight_radii, 1)
        disperse(lentic, lentic_flight_radii, 2)
        
        fig, ax = plt.subplots()
        im = ax.imshow(world + sum(lentic) + sum(lotic))
        plt.savefig(f'{scenario["name"]}/output_images/{i}.png')
    
        # reporting
        # pct of all water tiles occupied
        all_water_tiles = np.where(world > 0)[0]
        occupied_water_tiles = np.where(sum(lentic)+sum(lotic) > 0)
        pct_water_tiles_occupied.append(len(occupied_water_tiles[0]) / len(all_water_tiles))
        # pct of world covered (square distance)
        min_x = min(occupied_water_tiles[1])
        max_x = max(occupied_water_tiles[1])
        min_y = min(occupied_water_tiles[0])
        max_y = max(occupied_water_tiles[0])
        occupied_area = (max_x - min_x) * (max_y - min_y)
        pct_world_covered.append(occupied_area / (world_size ** 2))
    
    fig, ax = plt.subplots()
    ax.set_xlim(0, ticks)
    ax.set_ylim(0, 1)
    plt.xticks(range(0, ticks, 2))
    plt.ylabel('% water tiles occupied')
    plt.xlabel('Tick #')
    ax.plot(pct_water_tiles_occupied)
    plt.savefig(f'{scenario["name"]}/pct_water_tiles_occupied.png')
    
    fig, ax = plt.subplots()
    ax.set_xlim(0, ticks)
    ax.set_ylim(0, 1)
    plt.xticks(range(0, ticks, 2))
    plt.ylabel('% of world occupied')
    plt.xlabel('Tick #')
    ax.plot(pct_world_covered)
    plt.savefig(f'{scenario["name"]}/pct_world_occupied.png')
    
    filenames = [f'{scenario["name"]}/output_images/{i}.png' for i in range(ticks)]
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(f'{scenario["name"]}/output.gif', images, loop=0)