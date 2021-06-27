#!/bin/python3
import json
import meep as mp
import numpy as np
import meep_csg as msg

# corner1 = msg.Sphere(mp.Vector3(-1,1,0),1)
# corner2 = msg.Sphere(mp.Vector3(1,1,0),1)
# corner3 = msg.Sphere(mp.Vector3(-1,-1,0),1)
# corner4 = msg.Sphere(mp.Vector3(1,-1,0),1)
# body1 = msg.Box(mp.Vector3(4,2,mp.inf),mp.Vector3())
# body2 = msg.Box(mp.Vector3(2,4,mp.inf),mp.Vector3())
# hole = msg.Sphere(mp.Vector3(0.75,0.5,0),0.75)

# shape = msg.Union(corner1, corner2, corner3, corner4, body1, body2).subtract(hole)
# with open("shape.json", "w") as file:
#     json.dump(shape.encode(), file)

with open("shape.json", "r") as file:
    data = json.load(file)
    shape = msg.decode_json(data)

shape = msg.Sphere(mp.Vector3(0, 0, 0), 1)

cell = mp.Vector3(2, 2, 2)

sources = [
    mp.Source(
        mp.ContinuousSource(frequency=0.15), component=mp.Ez, center=mp.Vector3(-7, 0)
    )
]

pml_layers = [mp.PML(1.0)]

resolution = 10

sim = mp.Simulation(
    cell_size=cell,
    # boundary_layers=pml_layers,
    material_function=msg.material_function(shape, mp.Medium(index=3.5)),
    # sources=sources,
    resolution=resolution,
)


sim.run(mp.at_beginning(mp.output_epsilon()), until=1)
