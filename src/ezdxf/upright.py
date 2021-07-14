# Copyright (c) 2021, Manfred Moitzi
# License: MIT License
from typing import Iterable
import math
from ezdxf.math import Z_AXIS, Vec3, OCS, Vertex
from ezdxf.entities import DXFGraphic, DXFNamespace
from ezdxf.lldxf import const

__all__ = ["upright", "upright_all"]


def upright(entity: DXFGraphic) -> None:
    """Flips an inverted :ref:`OCS` defined by extrusion vector (0, 0, -1) into
    a :ref:`WCS` aligned :ref:`OCS` defined by extrusion vector (0, 0, 1).
    DXF entities with other extrusion vectors and unsupported DXF entities will
    be silently ignored.

    .. warning::

        The WCS representation as :class:`~ezdxf.path.Path` objects is the same
        overall but not always 100% identical, the orientation or the starting
        points of curves can be different.

        E.g. arc angles are always counter-clockwise oriented around the
        extrusion vector, therefore flipping the extrusion vector creates a
        similar but not a 100% identical arc.

    Supported DXF entities:

    - CIRCLE
    - ARC
    - ELLIPSE (WCS entity, flips only the extrusion vector)
    - SOLID
    - TRACE

    """
    # A mirrored text represented by an extrusion vector (0, 0, -1) cannot
    # represented by an extrusion vector (0, 0, 1), therefore this CANNOT work
    # for text entities or entities including text:
    # TEXT, ATTRIB, ATTDEF, MTEXT, DIMENSION, LEADER, MLEADER
    if not (
        isinstance(entity, DXFGraphic)
        and entity.is_alive
        and entity.dxf.hasattr("extrusion")
    ):
        return
    extrusion = Vec3(entity.dxf.extrusion).normalize()
    if not extrusion.isclose(FLIPPED_Z_AXIS):
        return
    dxftype: str = entity.dxftype()
    simple_tool = SIMPLE_UPRIGHT_TOOLS.get(dxftype)
    if simple_tool:
        simple_tool(entity.dxf)
    else:
        complex_tool = COMPLEX_UPRIGHT_TOOLS.get(dxftype)
        if complex_tool:
            complex_tool(entity)


def upright_all(entities: Iterable[DXFGraphic]) -> None:
    """Call function :func:`upright` for all DXF entities in iterable
    `entities`::

        upright_all(doc.modelspace())

    """
    for e in entities:
        upright(e)


FLIPPED_Z_AXIS = -Z_AXIS
FLIPPED_OCS = OCS(FLIPPED_Z_AXIS)


def _flip_deg_angle(angle: float) -> float:
    return (180.0 if angle >= 0.0 else -180.0) - angle


def _flip_rad_angle(angle: float) -> float:
    return (math.pi if angle >= 0.0 else -math.pi) - angle


def _flip_vertex(vertex: Vertex) -> Vertex:
    return FLIPPED_OCS.to_wcs(vertex)


def _flip_existing_vertex(dxf: DXFNamespace, name: str) -> None:
    if dxf.hasattr(name):
        vertex = _flip_vertex(dxf.get(name))
        dxf.set(name, vertex)


def _flip_thickness(dxf: DXFNamespace) -> None:
    if dxf.hasattr("thickness"):
        dxf.thickness = -dxf.thickness


def _flip_circle(dxf: DXFNamespace) -> None:
    dxf.center = _flip_vertex(dxf.center)
    _flip_thickness(dxf)
    dxf.discard("extrusion")


def _flip_arc(dxf: DXFNamespace) -> None:
    _flip_circle(dxf)
    end_angle = dxf.end_angle
    dxf.end_angle = _flip_deg_angle(dxf.start_angle)
    dxf.start_angle = _flip_deg_angle(end_angle)


def _flip_solid(dxf: DXFNamespace) -> None:
    for name in const.VERTEXNAMES:
        _flip_existing_vertex(dxf, name)
    _flip_thickness(dxf)
    dxf.discard("extrusion")


def _flip_ellipse(dxf: DXFNamespace) -> None:
    # ELLIPSE is a WCS entity!
    # just process start- and end params
    end_param = -dxf.end_param
    dxf.end_param = -dxf.start_param
    dxf.start_param = end_param
    dxf.discard("extrusion")


# All properties stored as DXF attributes
SIMPLE_UPRIGHT_TOOLS = {
    "CIRCLE": _flip_circle,
    "ARC": _flip_arc,
    "SOLID": _flip_solid,
    "TRACE": _flip_solid,
    "ELLIPSE": _flip_ellipse,
}


def _flip_complex_entity(entity: DXFGraphic) -> None:
    pass


# Additional vertices or paths to transform
COMPLEX_UPRIGHT_TOOLS = {
    "LWPOLYLINE": _flip_complex_entity,
    "POLYLINE": None,  # only 2D POLYLINE
    "HATCH": None,
    "MPOLYGON": None,
    "INSERT": None,
}
