"""
VRep implementations for basic shapes
"""

import meep as mp


class GeometryDecoderError(Exception):
    pass


def decode_json(data: dict):
    try:
        if "type" in data:
            # Look for the type in the module dict instead of having to deal with a registry system
            return globals()[data["type"]].decode(data)
        else:
            raise GeometryDecoderError
    except KeyError:
        print("Unable to decode object of type {}".format(data["type"]))
    except GeometryDecoderError:
        print("There was an error decoding object of type {}".format(data["type"]))


class VolumeRepresentation:
    """
    Abstract class for a volume of space
    """

    def is_inside(self, pos: mp.Vector3) -> bool:
        """
        Abstract method for determining if a point is inside the object
        """
        raise NotImplementedError

    def intersect(self, *others):
        return Intersection(self, *others)

    def union(self, *others):
        return Union(self, *others)

    def subtract(self, *others):
        return Subtraction(self, *others)


def material_function(
    sdf: VolumeRepresentation, medium: mp.Medium, background: mp.Medium = mp.air
):
    return lambda x: medium if sdf.is_inside(x) else background


# ----------------------------------------------------------------
# CSG Operations
# ----------------------------------------------------------------
class VolumeOperation(VolumeRepresentation):
    def __init__(self, *children: list[VolumeRepresentation]):
        self.children = children

    def encode(self):
        return {
            "type": self.__class__.__name__,
            "children": [c.encode() for c in self.children],
        }

    @classmethod
    def decode(cls, data):
        if "children" in data:
            return cls(*[decode_json(c) for c in data["children"]])
        else:
            raise GeometryDecoderError


class Union(VolumeOperation):
    """
    Geometric union of two objects
    """

    def is_inside(self, pos: mp.Vector3) -> bool:
        return any([c.is_inside(pos) for c in self.children])


class Intersection(VolumeOperation):
    """
    Geometric intersection of two objects
    """

    def is_inside(self, pos: mp.Vector3) -> bool:
        return all([c.is_inside(pos) for c in self.children])


class Subtraction(VolumeOperation):
    """
    Geometric subtraction of one object from another
    """

    def is_inside(self, pos: mp.Vector3) -> bool:
        return self.children[0].is_inside(pos) and not any(
            [c.is_inside(pos) for c in self.children[1:]]
        )


# ----------------------------------------------------------------
# Geometry Primitives
# ----------------------------------------------------------------
class Sphere(VolumeRepresentation):
    def __init__(self, center: mp.Vector3, radius: float) -> None:
        self.center = center
        self.radius = radius

    def is_inside(self, pos: mp.Vector3) -> bool:
        return True if (pos - self.center).norm() - self.radius <= 0 else False

    def encode(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "center": [self.center.x, self.center.y, self.center.z],
            "radius": self.radius,
        }

    @staticmethod
    def decode(data: dict) -> VolumeRepresentation:
        if "center" in data and "radius" in data:
            return Sphere(mp.Vector3(*data["center"]), data["radius"])
        else:
            raise GeometryDecoderError


class Box(VolumeRepresentation):
    def __init__(self, axis: mp.Vector3, center: mp.Vector3) -> None:
        self.axis = axis
        self.center = center

    def is_inside(self, pos: mp.Vector3) -> bool:
        is_in_x = abs(pos.x - self.center.x) - self.axis.x / 2 < 0
        is_in_y = abs(pos.y - self.center.y) - self.axis.y / 2 < 0
        is_in_z = abs(pos.z - self.center.z) - self.axis.z / 2 < 0
        return is_in_x and is_in_y and is_in_z

    def encode(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "axis": [self.axis.x, self.axis.y, self.axis.z],
            "center": [self.center.x, self.center.y, self.center.z],
        }

    @staticmethod
    def decode(data: dict) -> VolumeRepresentation:
        if "axis" in data and "center" in data:
            axis = mp.Vector3(*data["axis"])
            if axis.z < 0:
                axis.z = mp.inf
            center = mp.Vector3(*data["center"])
            return Box(axis, center)
        else:
            raise GeometryDecoderError
