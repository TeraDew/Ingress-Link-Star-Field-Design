from array import array
import itertools
import reprlib
import math


class Vector:
    typecode = 'd'

    def __init__(self, componets):
        self._components = array(self.typecode, componets)

    def __iter__(self):
        return iter(self._components)

    def __repr__(self):
        componets = reprlib.repr(self._components)
        componets = componets[componets.find('['):-1]
        return 'Vector({})'.format(componets)

    def __str__(self):
        return str(tuple(self))

    def __eq__(self, other):
        if isinstance(other, Vector):
            return(len(self) == len(other) and all(a == b for a, b in zip(self, other)))
        else:
            return NotImplemented

    def __add__(self, other):
        pairs = itertools.zip_longest(self, other, fillvalue=0.0)
        return Vector(a+b for a, b in pairs)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        pairs = itertools.zip_longest(self, other, fillvalue=0.0)
        return Vector(a-b for a, b in pairs)

    def __rsub__(self, other):
        return self - other

    def __mul__(self, other):
        try:
            return sum(a*b for a, b in zip(self, other))
        except TypeError:
            return NotImplemented

    def __rmul__(self, other):
        return self * other

    def __len__(self):
        return len(self._components)

    def __matmul__(self, other):
        if len(self) == len(other) and len(other) == 3:
            if isinstance(other, Vector):
                a = (list(self)[1]*list(other)[2]-list(other)[1]*list(self)[2])
                b = -(list(self)[0]*list(other)[2] -
                      list(other)[0]*list(self)[2])
                c = (list(self)[0]*list(other)[1]-list(other)[0]*list(self)[1])
                return Vector([a, b, c])
            else:
                return NotImplemented
        else:
            raise TypeError('not the same dimension')

    def __rmatmul__(self, other):
        return self@other

    def __abs__(self):
        return math.sqrt(sum(x * x for x in self))
