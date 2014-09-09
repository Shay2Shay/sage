r"""
Hyperbolic Isometries

This module implements the abstract base class for isometries of
hyperbolic space of arbitrary dimension.  It also contains the
implementations for specific models of hyperbolic geometry.

The isometry groups of all implemented models are either matrix Lie
groups or are doubly covered by matrix Lie groups.  As such, the
isometry constructor takes a matrix as input.  However, since the
isometries themselves may not be matrices, quantities like the trace
and determinant are not directly accessible from this class.

AUTHORS:

- Greg Laun (2013): initial version

EXAMPLES:

We can construct isometries in the upper half plane model, abbreviated
UHP for convenience::

    sage: HyperbolicPlane.UHP.isometry(matrix(2,[1,2,3,4]))
    Isometry in UHP
    [1 2]
    [3 4]
    sage: A = HyperbolicPlane.UHP.isometry(matrix(2,[0,1,1,0]))
    sage: A.inverse()
    Isometry in UHP
    [0 1]
    [1 0]
"""

#***********************************************************************
#       Copyright (C) 2013 Greg Laun <glaun@math.umd.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#***********************************************************************

from sage.categories.homset import Hom
from sage.categories.morphism import Morphism
from sage.misc.lazy_import import lazy_import
from sage.misc.lazy_attribute import lazy_attribute
lazy_import('sage.modules.free_module_element', 'vector')
from sage.rings.infinity import infinity
from sage.geometry.hyperbolic_space.hyperbolic_constants import EPSILON
from sage.misc.latex import latex
from sage.rings.all import CC
from sage.functions.other import real, imag

class HyperbolicIsometry(Morphism):
    r"""
    Abstract base class for hyperbolic isometries.  This class should
    never be instantiated.

    INPUT:

    - ``A`` -- a matrix representing a hyperbolic isometry in the
      appropriate model

    EXAMPLES::

        sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
        sage: A = HyperbolicIsometryUHP(identity_matrix(2))
        sage: B = HyperbolicIsometryHM(identity_matrix(3))
    """

    #####################
    # "Private" Methods #
    #####################

    def __init__(self, model, A):
        r"""
        See :class:`HyperbolicIsometry` for full documentation.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: HyperbolicIsometryUHP(matrix(2, [0,1,-1,0]))
            Isometry in UHP
            [ 0  1]
            [-1  0]
        """
        model.isometry_test(A)
        self._matrix = A
        Morphism.__init__(self, Hom(model, model))

    @lazy_attribute
    def _cached_matrix(self):
        r"""
        The representation of the current isometry used for
        calculations.  For example, if the current model uses the
        HyperbolicMethodsUHP class, then _cached_matrix will hold the
        `SL(2,\RR)` representation of ``self.matrix()``.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicIsometryHM(identity_matrix(3))
            sage: A._cached_matrix
            [1 0]
            [0 1]
        """
        return self.model().isometry_to_model(self.matrix(),
                                              self._HMethods.model().short_name)

    def _repr_(self):
        r"""
        Return a string representation of ``self``.

        OUTPUT:

        - a string

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: HyperbolicIsometryUHP(identity_matrix(2))
            Isometry in UHP
            [1 0]
            [0 1]
        """
        return self._repr_type() + " in {0}\n{1}".format(self.domain().short_name(), self._matrix)

    def _repr_type(self):
        r"""
        Return the type of morphism.
        """
        return "Isometry"

    def _latex_(self):
        r"""
        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicPlane.UHP.isometry(identity_matrix(2))
            sage: B = HyperbolicPlane.HM.isometry(identity_matrix(3))
            sage: latex(A)
            \pm \left(\begin{array}{rr}
            1 & 0 \\
            0 & 1
            \end{array}\right)

            sage: latex(B)
            \left(\begin{array}{rrr}
            1 & 0 & 0 \\
            0 & 1 & 0 \\
            0 & 0 & 1
            \end{array}\right)
        """
        if self.model().isometry_group_is_projective:
            return "\pm " + latex(self._matrix)
        else:
            return latex(self._matrix)

    def __eq__(self, other):
        r"""
        Return ``True`` if the isometries are the same and ``False`` otherwise.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicIsometryUHP(identity_matrix(2))
            sage: B = HyperbolicIsometryUHP(-identity_matrix(2))
            sage: A == B
            True
        """
        pos_matrix = bool(abs(self.matrix() - other.matrix()) < EPSILON)
        neg_matrix = bool(abs(self.matrix() + other.matrix()) < EPSILON)
        if self.domain().is_isometry_group_projective():
            return self.domain() is other.domain() and (pos_matrix or neg_matrix)
        else:
            return self.domain() is other.domain() and pos_matrix

    def __pow__(self, n):
        r"""
        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicIsometryUHP(matrix(2,[3,1,2,1]))
            sage: A**3
            Isometry in UHP
            [41 15]
            [30 11]
        """
        return self.__class__(self.domain(), self._matrix**n)

    def __mul__(self, other):
        r"""
        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicIsometryUHP(Matrix(2,[5,2,1,2]))
            sage: B = HyperbolicIsometryUHP(Matrix(2,[3,1,1,2]))
            sage: B*A
            Isometry in UHP
            [16  8]
            [ 7  6]
            sage: A = HyperbolicIsometryUHP(Matrix(2,[5,2,1,2]))
            sage: p = HyperbolicPlane.UHP.point(2 + I)
            sage: A*p
            Point in UHP 8/17*I + 53/17

            sage: g = HyperbolicPlane.UHP.geodesic(2 + I,4 + I)
            sage: A*g
            Geodesic in UHP from 8/17*I + 53/17 to 8/37*I + 137/37

            sage: A = diagonal_matrix([1, -1, 1])
            sage: A = HyperbolicIsometryHM(A)
            sage: A.orientation_preserving()
            False
            sage: p = HyperbolicPlane.HM.point((0, 1, sqrt(2)))
            sage: A*p
            Point in HM (0, -1, sqrt(2))
        """
        from sage.geometry.hyperbolic_space.hyperbolic_geodesic import HyperbolicGeodesic
        from sage.geometry.hyperbolic_space.hyperbolic_point import HyperbolicPoint
        if self.model_name() != other.model_name():
            raise TypeError("{0} and {1} are not in the same"
                            "model".format(self, other))
        if isinstance(other, HyperbolicIsometry):
            return self.__class__(self.domain(), self._matrix*other._matrix)
        elif isinstance(other, HyperbolicPoint):
            return self._model.get_point(self.model().isometry_act_on_point(
                self._matrix, other.coordinates()))
        elif isinstance(other, HyperbolicGeodesic):
            return self._model.get_geodesic(self*other.start(), self*other.end())
        else:
            NotImplementedError("multiplication is not defined between a "
                                "hyperbolic isometry and {0}".format(other))

    def _call_(self, other):
        r"""
        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicIsometryUHP(Matrix(2,[5,2,1,2]))
            sage: p = UHP.point(2 + I)
            sage: A(p)
            Point in UHP 8/17*I + 53/17.

            sage: g = UHP.geodesic(2 + I,4 + I)
            sage: A (g)
            Geodesic in UHP from 8/17*I + 53/17 to 8/37*I + 137/37.

            sage: A = diagonal_matrix([1, -1, 1])
            sage: A = HyperbolicIsometryHM(A)
            sage: A.orientation_preserving()
            False
            sage: p = HM.point((0, 1, sqrt(2)))
            sage: A(p)
            Point in HM (0, -1, sqrt(2)).
        """
        from sage.geometry.hyperbolic_space.hyperbolic_geodesic import HyperbolicGeodesic
        if self.domain() is not other.domain():
            raise TypeError("{0} is not in the {1} model".format(other, self.model_name()))

        if isinstance(other, HyperbolicGeodesic):
            return self.domain().get_geodesic(self(other.start()), self(other.end()))
        return self.domain().get_point(self.model().isometry_act_on_point(
            self.matrix(), other.coordinates()))

    #######################
    # Setters and Getters #
    #######################

    def matrix(self):
        r"""
        Return the matrix of the isometry.

        .. NOTE::

            We do not allow the ``matrix`` constructor to work as these may
            be elements of a projective group (ex. `PSL(n, \RR)`), so these
            isometries aren't true matrices.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: HyperbolicIsometryUHP(-identity_matrix(2)).matrix()
            [-1  0]
            [ 0 -1]
        """
        return self._matrix

    def inverse(self):
        r"""
        Return the inverse of the isometry ``self``.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicIsometryUHP(matrix(2,[4,1,3,2]))
            sage: B = A.inverse()
            sage: A*B == HyperbolicIsometryUHP(identity_matrix(2))
            True
        """
        return self.__class__(self._model, self.matrix().inverse())

    __invert__ = inverse

    def is_identity(self):
        """
        Return ``True`` if ``self`` is the identity isometry.
        """
        return self._matrix.is_one()

    def model(self):
        r"""
        Return the model to which ``self`` belongs.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: HyperbolicIsometryUHP(identity_matrix(2)).model()
            <class 'sage.geometry.hyperbolic_space.hyperbolic_model.HyperbolicModelUHP'>

            sage: HyperbolicIsometryPD(identity_matrix(2)).model()
            <class 'sage.geometry.hyperbolic_space.hyperbolic_model.HyperbolicModelPD'>

            sage: HyperbolicIsometryKM(identity_matrix(3)).model()
            <class 'sage.geometry.hyperbolic_space.hyperbolic_model.HyperbolicModelKM'>

            sage: HyperbolicIsometryHM(identity_matrix(3)).model()
            <class 'sage.geometry.hyperbolic_space.hyperbolic_model.HyperbolicModelHM'>
        """
        return self.domain()

    def model_name(self):
        r"""
        Return the short name of the hyperbolic model.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: HyperbolicIsometryUHP(identity_matrix(2)).model_name()
            'UHP'

            sage: HyperbolicIsometryPD(identity_matrix(2)).model_name()
            'PD'

            sage: HyperbolicIsometryKM(identity_matrix(3)).model_name()
            'KM'

            sage: HyperbolicIsometryHM(identity_matrix(3)).model_name()
            'HM'
        """
        return self.domain().short_name()

    def to_model(self, other):
        r"""
        Convert the current object to image in another model.

        INPUT:

        - ``other`` -- (a string representing) the image model

        EXAMPLES::

            sage: H = HyperbolicPlane()
            sage: UHP = H.UHP()
            sage: PD = H.PD()
            sage: KM = H.KM()
            sage: HM = H.HM()

            sage: I = UHP.get_isometry(identity_matrix(2))
            sage: I.to_model(HM)
            Isometry in HM
            [1 0 0]
            [0 1 0]
            [0 0 1]
            sage: I.to_model('HM')
            Isometry in HM
            [1 0 0]
            [0 1 0]
            [0 0 1]

            sage: I = PD.isometry(matrix(2,[I, 0, 0, -I]))
            sage: I.to_model(UHP)
            [ 0  1]
            [-1  0]

            sage: I.to_model(HM)
            [-1  0  0]
            [ 0 -1  0]
            [ 0  0  1]

            sage: Ito_model(KM)
            [-1  0  0]
            [ 0 -1  0]
            [ 0  0  1]

            sage: J = HM.isosometry(diagonal_matrix([-1, -1, 1]))
            sage: J.to_model(UHP)
            [ 0 -1]
            [ 1  0]

            sage: J.to_model(PD)
            [-I  0]
            [ 0  I]

            sage: J.to_model(KM)
            [-1  0  0]
            [ 0 -1  0]
            [ 0  0  1]
        """
        if isinstance(other, str):
            other = getattr(self.domain().realization_of(), other)
        phi = other.coerce_map_from(self.domain())
        return phi.convert_isometry(self)

    ###################
    # Boolean Methods #
    ###################

    def orientation_preserving(self):
        r"""
        Return ``True`` if ``self`` is orientation preserving and ``False``
        otherwise.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicIsometryUHP(identity_matrix(2))
            sage: A.orientation_preserving()
            True
            sage: B = HyperbolicIsometryUHP(matrix(2,[0,1,1,0]))
            sage: B.orientation_preserving()
            False
        """
        return self._HMethods.orientation_preserving(self._cached_matrix)

    ####################################
    # Methods implemented in _HMethods #
    ####################################

    def classification(self):
        r"""
        Classify the hyperbolic isometry as elliptic, parabolic,
        hyperbolic or a reflection.

        A hyperbolic isometry fixes two points on the boundary of
        hyperbolic space, a parabolic isometry fixes one point on the
        boundary of hyperbolic space, and an elliptic isometry fixes no
        points.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: H = HyperbolicIsometryUHP(matrix(2,[2,0,0,1/2]))
            sage: H.classification()
            'hyperbolic'

            sage: P = HyperbolicIsometryUHP(matrix(2,[1,1,0,1]))
            sage: P.classification()
            'parabolic'

            sage: E = HyperbolicIsometryUHP(matrix(2,[-1,0,0,1]))
            sage: E.classification()
            'reflection'
        """
        R = self._model.realization_of().a_realization()
        return self.to_model(R).classification()
        #return self.to_model(R).classification(self._cached_matrix)

    def translation_length(self):
        r"""
        For hyperbolic elements, return the translation length;
        otherwise, raise a ``ValueError``.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: H = HyperbolicIsometryUHP(matrix(2,[2,0,0,1/2]))
            sage: H.translation_length()
            2*arccosh(5/4)

        ::

            sage: f_1 = HyperbolicPlane.UHP.point(-1)
            sage: f_2 = HyperbolicPlane.UHP.point(1)
            sage: H = HyperbolicIsometryUHP.isometry_from_fixed_points(f_1, f_2)
            sage: p = HyperbolicPlane.UHP.point(exp(i*7*pi/8))
            sage: bool((p.dist(H*p) - H.translation_length()) < 10**-9)
            True
        """
        return self._HMethods.translation_length(self._cached_matrix)

    def axis(self, **graphics_options):
        r"""
        For a hyperbolic isometry, return the axis of the
        transformation; otherwise raise a ``ValueError``.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: H = HyperbolicIsometryUHP(matrix(2,[2,0,0,1/2]))
            sage: H.axis()
            Geodesic in UHP from 0 to +Infinity

        It is an error to call this function on an isometry that is
        not hyperbolic::

            sage: P = HyperbolicIsometryUHP(matrix(2,[1,4,0,1]))
            sage: P.axis()
            Traceback (most recent call last):
            ...
            ValueError: the isometry is not hyperbolic: axis is undefined
        """
        if self.classification() not in ['hyperbolic',
                                         'orientation-reversing hyperbolic']:
            raise ValueError("the isometry is not hyperbolic: axis is undefined")
        return self.domain().get_geodesic(*self.fixed_point_set())

    def fixed_point_set(self, **graphics_options):
        r"""
        Return the a list containing the fixed point set of orientation-
        preserving isometries.

        OUTPUT:

        - a list of hyperbolic points

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: H = HyperbolicIsometryUHP(matrix(2, [-2/3,-1/3,-1/3,-2/3]))
            sage: (p1,p2) = H.fixed_point_set()
            sage: H*p1 == p1
            True
            sage: H*p2 == p2
            True
            sage: A = HyperbolicIsometryUHP(matrix(2,[0,1,1,0]))
            sage: A.orientation_preserving()
            False
            sage: A.fixed_point_set()
            [Boundary point in UHP 1, Boundary point in UHP -1]

       ::

            sage: B = HyperbolicIsometryUHP(identity_matrix(2))
            sage: B.fixed_point_set()
            Traceback (most recent call last):
            ...
            ValueError: the identity transformation fixes the entire hyperbolic plane
        """
        pts = self._HMethods.fixed_point_set(self._cached_matrix)
        pts =  [self._HMethods.model().point_to_model(k, self.model_name())
                for k in pts]
        return [self.domain().get_point(k, **graphics_options) for k in pts]

    def fixed_geodesic(self, **graphics_options):
        r"""
        If ``self`` is a reflection in a geodesic, return that geodesic.

        EXAMPLES::

            sage: A = HyperbolicPlane.UHP.isometry(matrix(2, [0, 1, 1, 0]))
            sage: A.fixed_geodesic()
            Geodesic in UHP from 1 to -1
        """
        fps = self._HMethods.fixed_point_set(self._cached_matrix)
        if len(fps) < 2:
            raise ValueError("isometries of type {0}".format(self.classification())
                             + " don't fix geodesics")
        from sage.geometry.hyperbolic_space.model_factory import ModelFactory
        fact = ModelFactory.find_factory(self._HMethods.model_name())
        geod = fact.get_geodesic(fps[0], fps[1])
        return geod.to_model(self.model_name())

    def repelling_fixed_point(self, **graphics_options):
        r"""
        For a hyperbolic isometry, return the attracting fixed point;
        otherwise raise a ``ValueError``.

        OUTPUT:

        - a hyperbolic point

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicIsometryUHP(Matrix(2,[4,0,0,1/4]))
            sage: A.repelling_fixed_point()
            Boundary point in UHP 0
        """
        fp = self._HMethods.repelling_fixed_point(self._cached_matrix)
        fp = self._HMethods.model().point_to_model(fp, self.model_name())
        return self.domain().get_point(fp)

    def attracting_fixed_point(self, **graphics_options):
        r"""
        For a hyperbolic isometry, return the attracting fixed point;
        otherwise raise a `ValueError``.

        OUTPUT:

        - a hyperbolic point

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: A = HyperbolicIsometryUHP(Matrix(2,[4,0,0,1/4]))
            sage: A.attracting_fixed_point()
            Boundary point in UHP +Infinity
        """
        fp = self._HMethods.attracting_fixed_point(self._cached_matrix)
        fp = self._HMethods.model().point_to_model(fp, self.model_name())
        return self.domain().get_point(fp)

    def isometry_from_fixed_points(self, repel, attract):
        r"""
        Given two fixed points ``repel`` and ``attract`` as hyperbolic
        points return a hyperbolic isometry with ``repel`` as repelling
        fixed point and ``attract`` as attracting fixed point.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import *
            sage: p, q = [HyperbolicPlane.UHP.point(k) for k in [2 + I, 3 + I]]
            sage: HyperbolicIsometryUHP.isometry_from_fixed_points(p, q)
            Traceback (most recent call last):
            ...
            ValueError: fixed points of hyperbolic elements must be ideal

            sage: p, q = [HyperbolicPlane.UHP.point(k) for k in [2, 0]]
            sage: HyperbolicIsometryUHP.isometry_from_fixed_points(p, q)
            Isometry in UHP
            [  -1    0]
            [-1/3 -1/3]
        """
        try:
            A = self._HMethods.isometry_from_fixed_points(repel._cached_coordinates,
                                                          attract._cached_coordinates)
            A = self._HMethods.model().isometry_to_model(A, self.model_name())
            return self.domain().get_isometry(A)
        except(AttributeError):
            repel = self.domain().get_point(repel)
            attract = self.domain().get_point(attract)
            return self.isometry_from_fixed_points(repel, attract)

class HyperbolicIsometryUHP(HyperbolicIsometry):
    r"""
    Create a hyperbolic isometry in the UHP model.

    INPUT:

    - a matrix in `GL(2, \RR)`

    EXAMPLES::

        sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import HyperbolicIsometryUHP
        sage: A = HyperbolicIsometryUHP(identity_matrix(2))
    """

    def orientation_preserving(self):
        r"""
        Return ``True`` if ``self`` is orientation preserving and ``False``
        otherwise.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_methods import HyperbolicMethodsUHP
            sage: A = identity_matrix(2)
            sage: HyperbolicMethodsUHP.orientation_preserving(A)
            True
            sage: B = matrix(2,[0,1,1,0])
            sage: HyperbolicMethodsUHP.orientation_preserving(B)
            False
        """
        return bool(self._matrix.det() > 0)

    def classification(self):
        r"""
        Classify the hyperbolic isometry as elliptic, parabolic, or
        hyperbolic.

        A hyperbolic isometry fixes two points on the boundary of
        hyperbolic space, a parabolic isometry fixes one point on the
        boundary of hyperbolic space, and an elliptic isometry fixes
        no points.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_methods import HyperbolicMethodsUHP
            sage: HyperbolicMethodsUHP.classification(identity_matrix(2))
            'identity'

            sage: HyperbolicMethodsUHP.classification(4*identity_matrix(2))
            'identity'

            sage: HyperbolicMethodsUHP.classification(matrix(2,[2,0,0,1/2]))
            'hyperbolic'

            sage: HyperbolicMethodsUHP.classification(matrix(2, [0, 3, -1/3, 6]))
            'hyperbolic'

            sage: HyperbolicMethodsUHP.classification(matrix(2,[1,1,0,1]))
            'parabolic'

            sage: HyperbolicMethodsUHP.classification(matrix(2,[-1,0,0,1]))
            'reflection'
        """
        A = self._matrix.n()
        A = A / (abs(A.det()).sqrt())
        tau = abs(A.trace())
        a = A.list()
        if A.det() > 0:
            tf = bool((a[0] - 1)**2 + a[1]**2 + a[2]**2 + (a[3] - 1)**2  <
                      EPSILON)
            tf = bool((a[0] - 1)**2 + a[1]**2 + a[2]**2 + (a[3] - 1)**2  <
                      EPSILON)
            if tf:
                return 'identity'
            if tau -  2 < -EPSILON:
                return 'elliptic'
            elif tau -2  > -EPSILON and tau -  2 < EPSILON:
                return 'parabolic'
            elif tau - 2  > EPSILON:
                return 'hyperbolic'
            else:
                raise ValueError("something went wrong with classification:" +
                                 " trace is {}".format(A.trace()))
        else:  #The isometry reverses orientation.
            if tau < EPSILON:
                return 'reflection'
            else:
                return 'orientation-reversing hyperbolic'

    def translation_length(self):
        r"""
        For hyperbolic elements, return the translation length;
        otherwise, raise a ``ValueError``.

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_methods import HyperbolicMethodsUHP
            sage: HyperbolicMethodsUHP.translation_length(matrix(2,[2,0,0,1/2]))
            2*arccosh(5/4)

        ::

            sage: H = HyperbolicMethodsUHP.isometry_from_fixed_points(-1,1)
            sage: p = exp(i*7*pi/8)
            sage: from sage.geometry.hyperbolic_space.hyperbolic_model import mobius_transform
            sage: Hp = mobius_transform(H, p)
            sage: bool((HyperbolicMethodsUHP.point_dist(p, Hp) - HyperbolicMethodsUHP.translation_length(H)) < 10**-9)
            True
        """
        d = sqrt(self._matrix.det()**2)
        tau = sqrt((self._matrix / sqrt(d)).trace()**2)
        if self.classification() in ['hyperbolic', 'oriention-reversing hyperbolic']:
            return 2 * arccosh(tau/2)
        raise TypeError("translation length is only defined for hyperbolic transformations")

    def fixed_point_set(self):
        r"""
        Return the a list containing the fixed point set of
        orientation-preserving isometries.

        OUTPUT:

        - a list of hyperbolic points

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_methods import HyperbolicMethodsUHP
            sage: H = matrix(2, [-2/3,-1/3,-1/3,-2/3])
            sage: (p1,p2) = HyperbolicMethodsUHP.fixed_point_set(H)
            sage: from sage.geometry.hyperbolic_space.hyperbolic_model import mobius_transform
            sage: bool(mobius_transform(H, p1) == p1)
            True
            sage: bool(mobius_transform(H, p2) == p2)
            True

            sage: HyperbolicMethodsUHP.fixed_point_set(identity_matrix(2))
            Traceback (most recent call last):
            ...
            ValueError: the identity transformation fixes the entire hyperbolic plane
        """
        d = sqrt(self._matrix.det()**2)
        M = self._matrix / sqrt(d)
        tau = M.trace()**2
        M_cls = self.classification()
        if M_cls == 'identity':
            raise ValueError("the identity transformation fixes the entire "
                             "hyperbolic plane")
        if M_cls == 'parabolic':
            if abs(M[1,0]) < EPSILON:
                return [infinity]
            else:
                # boundary point
                return [(M[0,0] - M[1,1]) / (2*M[1,0])]
        elif M_cls == 'elliptic':
            d = sqrt(tau - 4)
            return [(M[0,0] - M[1,1] + sign(M[1,0])*d)/(2*M[1,0])]
        elif M_cls == 'hyperbolic':
            if M[1,0] != 0: #if the isometry doesn't fix infinity
                d = sqrt(tau - 4)
                p_1 = (M[0,0] - M[1,1]+d) / (2*M[1,0])
                p_2 = (M[0,0] - M[1,1]-d) / (2*M[1,0])
                return [p_1, p_2]
            else: #else, it fixes infinity.
                p_1 = M[0,1] / (M[1,1] - M[0,0])
                p_2 = infinity
                return [p_1, p_2]
        else:
            # raise NotImplementedError("fixed point set not implemented for"
            #                           " isometries of type {0}".format(M_cls))
            try:
                p, q = [M.eigenvectors_right()[k][1][0] for k in range(2)]
            except (IndexError):
                M = M.change_ring(RDF)
                p, q = [M.eigenvectors_right()[k][1][0] for k in range(2)]
            if p[1] == 0:
                p = infinity
            else:
                p = p[0] / p[1]
            if q[1] == 0:
                q = infinity
            else:
                q = q[0] / q[1]
            pts = [p, q]
            return [k for k in pts if imag(k) >= 0]

    def repelling_fixed_point(self):
        r"""
        Return the repelling fixed point; otherwise raise a ``ValueError``.

        OUTPUT:

        - a hyperbolic point

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_methods import HyperbolicMethodsUHP
            sage: A = matrix(2,[4,0,0,1/4])
            sage: HyperbolicMethodsUHP.repelling_fixed_point(A)
            0
        """
        if self.classification() not in ['hyperbolic',
                                         'orientation-reversing hyperbolic']:
            raise ValueError("repelling fixed point is defined only" +
                             "for hyperbolic isometries")
        v = self._matrix.eigenmatrix_right()[1].column(1)
        if v[1] == 0:
            return infinity
        return v[0] / v[1]

    def attracting_fixed_point(self):
        r"""
        Return the attracting fixed point; otherwise raise a ``ValueError``.

        OUTPUT:

        - a hyperbolic point

        EXAMPLES::

            sage: from sage.geometry.hyperbolic_space.hyperbolic_methods import HyperbolicMethodsUHP
            sage: A = matrix(2,[4,0,0,1/4])
            sage: HyperbolicMethodsUHP.attracting_fixed_point(A)
            +Infinity
        """
        if self.classification() not in \
                ['hyperbolic', 'orientation-reversing hyperbolic']:
            raise ValueError("Attracting fixed point is defined only" +
                             "for hyperbolic isometries.")
        v = self._matrix.eigenmatrix_right()[1].column(0)
        if v[1] == 0:
            return infinity
        return v[0] / v[1]

class HyperbolicIsometryPD(HyperbolicIsometry):
    r"""
    Create a hyperbolic isometry in the PD model.

    INPUT:

    - a matrix in `PU(1,1)`

    EXAMPLES::

        sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import HyperbolicIsometryPD
        sage: A = HyperbolicIsometryPD(identity_matrix(2))
    """

class HyperbolicIsometryKM(HyperbolicIsometry):
    r"""
    Create a hyperbolic isometry in the KM model.

    INPUT:

    - a matrix in `SO(2,1)`

    EXAMPLES::

        sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import HyperbolicIsometryKM
        sage: A = HyperbolicIsometryKM(identity_matrix(3))
    """

class HyperbolicIsometryHM(HyperbolicIsometry):
    r"""
    Create a hyperbolic isometry in the HM model.

    INPUT:

    - a matrix in `SO(2,1)`

    EXAMPLES::

        sage: from sage.geometry.hyperbolic_space.hyperbolic_isometry import HyperbolicIsometryHM
        sage: A = HyperbolicIsometryHM(identity_matrix(3))
    """

