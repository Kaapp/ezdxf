# Created: 30.04.2014
# Copyright (c) 2014-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from array import array
from itertools import chain
from ..tools.c23 import ustr
TAG_STRING_FORMAT = '%3d\n%s\n'


class DXFTag(object):
    __slots__ = ['code', '_value']

    def __init__(self, code, value):
        self.code = code
        self._value = value

    def __str__(self):
        return str((self.code, self.value))

    def __repr__(self):
        return "DXFTag{}".format(str(self))


    @property
    def value(self):
        return self._value

    def __getitem__(self, item):
        return (self.code, self.value)[item]

    def __iter__(self):
        yield self.code
        yield self.value

    def __eq__(self, other):
        return (self.code, self.value) == other

    # for Python 2.7 required
    def __ne__(self, other):
        return (self.code, self.value) != other

    def dxfstr(self):
        return TAG_STRING_FORMAT % (self.code, self._value)

    def clone(self):
        return self.__class__(self.code, self._value)


NONE_TAG = DXFTag(None, None)


class DXFVertex(DXFTag):
    __slots__ = ['code', '_value']

    def __init__(self, code, value):
        super(DXFVertex, self).__init__(code, array('d', value))

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "DXFVertex({}, {})".format(self.code, str(self))

    @property
    def value(self):
        return tuple(self._value)

    def dxftags(self):
        c = self.code
        return ((code, value) for code, value in zip((c, c+10, c+20), self.value))

    def dxfstr(self):
        return ''.join(TAG_STRING_FORMAT % tag for tag in self.dxftags())


def point_tuple(value):
    return tuple(float(f) for f in value)


def _build_type_table(types):
    table = {}
    for caster, codes in types:
        for code in codes:
            table[code] = caster
    return table


TYPE_TABLE = _build_type_table([
    # all group code < 0 are spacial tags for internal use, but not accessible by get_dxf_attrib()
    (point_tuple, range(10, 20)),  # 2d or 3d points
    (float, range(20, 60)),  # code 20-39 belongs to 2d/3d points and should not appear alone
    (int, range(60, 100)),
    (point_tuple, range(110, 113)),  # 110, 111, 112 - UCS definition
    (float, range(113, 150)),  # 113-139 belongs to UCS definition and should not appear alone
    (int, range(160, 170)),
    (int, range(170, 180)),
    (point_tuple, [210]),  # extrusion direction
    (float, range(211, 240)),  # code 220, 230 belongs to extrusion direction and should not appear alone
    (int, range(270, 290)),
    (int, range(290, 300)),  # bool 1=True 0=False
    (int, range(370, 390)),
    (int, range(400, 410)),
    (int, range(420, 430)),
    (int, range(440, 460)),
    (float, range(460, 470)),
    (point_tuple, range(1010, 1020)),
    (float, range(1020, 1060)),  # code 1020-1039 belongs to 2d/3d points and should not appear alone
    (int, range(1060, 1072)),
])

POINT_CODES = frozenset([
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
    110, 111, 112, 210,
    1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019,
])

GENERAL_MARKER = 0
SUBCLASS_MARKER = 100
APP_DATA_MARKER = 102
EXT_DATA_MARKER = 1001
GROUP_MARKERS = frozenset([GENERAL_MARKER, SUBCLASS_MARKER, APP_DATA_MARKER, EXT_DATA_MARKER])
BINARY_FLAGS = frozenset([70, 90])
HANDLE_CODES = frozenset([5, 105])
POINTER_CODES = frozenset(chain(range(320, 370), range(390, 400), (480, 481, 1005)))
HEX_HANDLE_CODES = frozenset(chain(HANDLE_CODES, POINTER_CODES))


def is_pointer_code(code):
    return code in POINTER_CODES


def is_point_code(code):
    return code in POINT_CODES


def is_point_tag(tag):
    return tag[0] in POINT_CODES


def cast_tag_value(code, value, types=TYPE_TABLE):
    return types.get(code, ustr)(value)


def tag_type(code):
    return TYPE_TABLE.get(code, ustr)


def strtag(tag):
    return TAG_STRING_FORMAT % tuple(tag)


