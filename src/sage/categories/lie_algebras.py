r"""
Lie Algebras

AUTHORS:

- Travis Scrimshaw (07-15-2013): Initial implementation
"""

#*****************************************************************************
#       Copyright (C) 2013 Travis Scrimshaw <tscrim at ucdavis.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.misc.lazy_attribute import lazy_attribute
from sage.misc.lazy_import import LazyImport
from sage.categories.category import JoinCategory, Category
from sage.categories.category_types import Category_over_base_ring
from sage.categories.category_with_axiom import CategoryWithAxiom_over_base_ring
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
from sage.categories.modules import Modules
from sage.categories.sets_cat import Sets
from sage.categories.homset import Hom
from sage.categories.morphism import Morphism
from sage.structure.element import coerce_binop

class LieAlgebras(Category_over_base_ring):
    """
    The category of Lie algebras.

    EXAMPLES::

        sage: C = LieAlgebras(QQ); C
        Category of Lie algebras over Rational Field
        sage: sorted(C.super_categories(), key=str)
        [Category of vector spaces over Rational Field]

    We construct a typical parent in this category, and do some
    computations with it::

        sage: A = C.example(); A
        An example of a Lie algebra: the Lie algebra from the associative
         algebra Symmetric group algebra of order 3 over Rational Field
         generated by ([2, 1, 3], [2, 3, 1])

        sage: A.category()
        Category of Lie algebras over Rational Field

        sage: A.base_ring()
        Rational Field

        sage: a,b = A.lie_algebra_generators()
        sage: a.bracket(b)
        -[1, 3, 2] + [3, 2, 1]
        sage: b.bracket(2*a + b)
        2*[1, 3, 2] - 2*[3, 2, 1]

        sage: A.bracket(a, b)
        -[1, 3, 2] + [3, 2, 1]

    Please see the source code of `A` (with ``A??``) for how to
    implement other Lie algebras.

    TESTS::

        sage: C = LieAlgebras(QQ)
        sage: TestSuite(C).run()
        sage: TestSuite(C.example()).run()

    .. TODO::

        Many of these tests should use Lie algebras that are not the minimal
        example and need to be added after :trac:`16820` (and :trac:`16823`).
    """
    @cached_method
    def super_categories(self):
        """
        EXAMPLES::

            sage: LieAlgebras(QQ).super_categories()
            [Category of vector spaces over Rational Field]
        """
        # We do not also derive from (Magmatic) algebras since we don't want *
        #   to be our Lie bracket
        # Also this doesn't inherit the ability to add axioms like Associative
        #   and Unital, both of which do not make sense for Lie algebras
        return [Modules(self.base_ring())]

    # TODO: Find some way to do this without copying most of the logic.
    def _repr_object_names(self):
        r"""
        Return the name of the objects of this category.

        .. SEEALSO:: :meth:`Category._repr_object_names`

        EXAMPLES::

            sage: LieAlgebras(QQ)._repr_object_names()
            'Lie algebras over Rational Field'
            sage: LieAlgebras(Fields())._repr_object_names()
            'Lie algebras over fields'
            sage: from sage.categories.category import JoinCategory
            sage: from sage.categories.category_with_axiom import Blahs
            sage: LieAlgebras(JoinCategory((Blahs().Flying(), Fields())))
            Category of Lie algebras over (flying unital blahs and fields)
        """
        base = self.base()
        if isinstance(base, Category):
            if isinstance(base, JoinCategory):
                name = '('+' and '.join(C._repr_object_names() for C in base.super_categories())+')'
            else:
                name = base._repr_object_names()
        else:
            name = base
        return "Lie algebras over {}".format(name)

    def example(self, gens=None):
        """
        Return an example of a Lie algebra as per
        :meth:`Category.example <sage.categories.category.Category.example>`.

        EXAMPLES::

            sage: LieAlgebras(QQ).example()
            An example of a Lie algebra: the Lie algebra from the associative algebra
             Symmetric group algebra of order 3 over Rational Field
             generated by ([2, 1, 3], [2, 3, 1])

        Another set of generators can be specified as an optional argument::

            sage: F.<x,y,z> = FreeAlgebra(QQ)
            sage: LieAlgebras(QQ).example(F.gens())
            An example of a Lie algebra: the Lie algebra from the associative algebra
             Free Algebra on 3 generators (x, y, z) over Rational Field
             generated by (x, y, z)
        """
        if gens is None:
            from sage.combinat.symmetric_group_algebra import SymmetricGroupAlgebra
            from sage.rings.all import QQ
            gens = SymmetricGroupAlgebra(QQ, 3).algebra_generators()
        from sage.categories.examples.lie_algebras import Example
        return Example(gens)

    WithBasis = LazyImport('sage.categories.lie_algebras_with_basis',
                           'LieAlgebrasWithBasis', as_name='WithBasis')

    class FiniteDimensional(CategoryWithAxiom_over_base_ring):
        WithBasis = LazyImport('sage.categories.finite_dimensional_lie_algebras_with_basis',
                               'FiniteDimensionalLieAlgebrasWithBasis', as_name='WithBasis')

        def extra_super_categories(self):
            """
            Implements the fact that a finite dimensional Lie algebra over
            a finite ring is finite.

            EXAMPLES::

                sage: LieAlgebras(IntegerModRing(4)).FiniteDimensional().extra_super_categories()
                [Category of finite sets]
                sage: LieAlgebras(ZZ).FiniteDimensional().extra_super_categories()
                []
                sage: LieAlgebras(GF(5)).FiniteDimensional().is_subcategory(Sets().Finite())
                True
                sage: LieAlgebras(ZZ).FiniteDimensional().is_subcategory(Sets().Finite())
                False
                sage: LieAlgebras(GF(5)).WithBasis().FiniteDimensional().is_subcategory(Sets().Finite())
                True
            """
            if self.base_ring() in Sets().Finite():
                return [Sets().Finite()]
            return []

    class ParentMethods:
        #@abstract_method
        #def lie_algebra_generators(self):
        #    """
        #    Return the generators of ``self`` as a Lie algebra.
        #    """

        # TODO: Move this to LieAlgebraElement, cythonize, and use more standard
        #   coercion framework test (i.e., have_same_parent)
        def bracket(self, lhs, rhs):
            """
            Return the Lie bracket ``[lhs, rhs]`` after coercing ``lhs`` and
            ``rhs`` into elements of ``self``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: L.bracket(x, x + y)
                -[1, 3, 2] + [3, 2, 1]
                sage: L.bracket(x, 0)
                0
                sage: L.bracket(0, x)
                0
            """
            return self(lhs)._bracket_(self(rhs))

        # Do not override this. Instead implement :meth:`_construct_UEA`;
        #   then, :meth:`lift` and :meth:`universal_enveloping_algebra`
        #   will automatically setup the coercion
        def universal_enveloping_algebra(self):
            """
            Return the universal enveloping algebra of ``self``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: L.universal_enveloping_algebra()
                Noncommutative Multivariate Polynomial Ring in b0, b1, b2
                 over Rational Field, nc-relations: {}

            ::

                sage: L = LieAlgebra(QQ, 3, 'x', abelian=True)
                sage: L.universal_enveloping_algebra()
                Multivariate Polynomial Ring in x0, x1, x2 over Rational Field

            .. SEEALSO::

                :meth:`lift`
            """
            return self.lift.codomain()

        @abstract_method(optional=True)
        def _construct_UEA(self):
            """
            Return the universal enveloping algebra of ``self``.

            Unlike :meth:`universal_enveloping_algebra`, this method does not
            (usually) construct the canonical lift morphism from ``self``
            to the universal enveloping algebra (let alone register it
            as a coercion).

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: L._construct_UEA()
                Noncommutative Multivariate Polynomial Ring in b0, b1, b2
                 over Rational Field, nc-relations: {}

            ::

                sage: L = LieAlgebra(QQ, 3, 'x', abelian=True)
                sage: L.universal_enveloping_algebra() # indirect doctest
                Multivariate Polynomial Ring in x0, x1, x2 over Rational Field
            """

        @abstract_method(optional=True)
        def module(self):
            """
            Return an `R`-module which is isomorphic to the
            underlying `R`-module of ``self``.

            The rationale behind this method is to enable linear
            algebraic functionality on ``self`` (such as
            computing the span of a list of vectors in ``self``)
            via an isomorphism from ``self`` to an `R`-module
            (typically, although not always, an `R`-module of
            the form `R^n` for an `n \in \NN`) on which such
            functionality already exists. For this method to be
            of any use, it should return an `R`-module which has
            linear algebraic functionality that ``self`` does
            not have.

            For instance, if ``self`` has ordered basis
            `(e, f, h)`, then ``self.module()`` will be the
            `R`-module `R^3`, and the elements `e`, `f` and
            `h` of ``self`` will correspond to the basis
            vectors `(1, 0, 0)`, `(0, 1, 0)` and `(0, 0, 1)`
            of ``self.module()``.

            This method :meth:`module` needs to be set whenever
            a finite-dimensional Lie algebra with basis is
            intended to support linear algebra (which is, e.g.,
            used in the computation of centralizers and lower
            central series). One then needs to also implement
            the `R`-module isomorphism from ``self`` to
            ``self.module()`` in both directions; that is,
            implement:

            * a ``to_vector`` ElementMethod which sends every
              element of ``self`` to the corresponding element of
              ``self.module()``;

            * a ``from_vector`` ParentMethod which sends every
              element of ``self.module()`` to an element
              of ``self``.

            The ``from_vector`` method will automatically serve
            as an element constructor of ``self`` (that is,
            ``self(v)`` for any ``v`` in ``self.module()`` will
            return ``self.from_vector(v)``).

            .. TODO::

                Ensure that this is actually so.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: L.module()
                Vector space of dimension 3 over Rational Field
            """

        @abstract_method(optional=True)
        def from_vector(self, v):
            """
            Return the element of ``self`` corresponding to the
            vector ``v`` in ``self.module()``.

            Implement this if you implement :meth:`module`; see the
            documentation of the latter for how this is to be done.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: u = L.from_vector(vector(QQ, (1, 0, 0))); u
                (1, 0, 0)
                sage: parent(u) is L
                True
            """

        @lazy_attribute
        def lift(self):
            """
            Construct the lift morphism from ``self`` to the universal
            enveloping algebra of ``self`` (the latter is implemented
            as :meth:`universal_enveloping_algebra`).

            This is a Lie algebra homomorphism. It is injective if
            ``self`` is a free module over its base ring, or if the
            base ring is a `\QQ`-algebra.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: a, b, c = L.lie_algebra_generators()
                sage: lifted = L.lift(2*a + b - c); lifted
                2*b0 + b1 - b2
                sage: lifted.parent() is L.universal_enveloping_algebra()
                True
            """
            M = LiftMorphism(self, self._construct_UEA())
            M.register_as_coercion()
            return M

        def subalgebra(self, gens, names=None, index_set=None, category=None):
            r"""
            Return the subalgebra of ``self`` generated by ``gens``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: a, b, c = L.lie_algebra_generators()
                sage: L.subalgebra([2*a - c, b + c])
                An example of a finite dimensional Lie algebra with basis:
                 the 2-dimensional abelian Lie algebra over Rational Field
                 with basis matrix:
                [   1    0 -1/2]
                [   0    1    1]

            ::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: L.subalgebra([x + y])
                Traceback (most recent call last):
                ...
                NotImplementedError: subalgebras not yet implemented: see #17416
            """
            raise NotImplementedError("subalgebras not yet implemented: see #17416")
            #from sage.algebras.lie_algebras.subalgebra import LieSubalgebra
            #return LieSubalgebra(gens, names, index_set, category)

        @abstract_method(optional=True)
        def killing_form(self, x, y):
            """
            Return the Killing form of ``x`` and ``y``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: a, b, c = L.lie_algebra_generators()
                sage: L.killing_form(a, b+c)
                0
            """

        def is_abelian(self):
            r"""
            Return ``True`` if this Lie algebra is abelian.

            A Lie algebra `\mathfrak{g}` is abelian if `[x, y] = 0` for all
            `x, y \in \mathfrak{g}`.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: L.is_abelian()
                False
                sage: R = QQ['x,y']
                sage: L = LieAlgebras(QQ).example(R.gens())
                sage: L.is_abelian()
                True

            ::

                sage: L.<x> = LieAlgebra(QQ,1)  # todo: not implemented - #16823
                sage: L.is_abelian()  # todo: not implemented - #16823
                True
                sage: L.<x,y> = LieAlgebra(QQ,2)  # todo: not implemented - #16823
                sage: L.is_abelian()  # todo: not implemented - #16823
                False
            """
            G = self.lie_algebra_generators()
            if G not in FiniteEnumeratedSets():
                raise NotImplementedError("infinite number of generators")
            zero = self.zero()
            return all(x._bracket_(y) == zero for x in G for y in G)

        def is_commutative(self):
            """
            Return if ``self`` is commutative. This is equivalent to ``self``
            being abelian.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: L.is_commutative()
                False

            ::

                sage: L.<x> = LieAlgebra(QQ, 1) # todo: not implemented - #16823
                sage: L.is_commutative() # todo: not implemented - #16823
                True
            """
            return self.is_abelian()

        @abstract_method(optional=True)
        def is_solvable(self):
            """
            Return if ``self`` is a solvable Lie algebra.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: L.is_solvable()
                True
            """

        @abstract_method(optional=True)
        def is_nilpotent(self):
            """
            Return if ``self`` is a nilpotent Lie algebra.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: L.is_nilpotent()
                True
            """

        def _test_jacobi_identity(self, **options):
            """
            Test that the Jacobi identity is satisfied on (not
            necessarily all) elements of this set.

            INPUT:

            - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

            EXAMPLES:

            By default, this method runs the tests only on the
            elements returned by ``self.some_elements()``::

                sage: L = LieAlgebras(QQ).example()
                sage: L._test_jacobi_identity()

            However, the elements tested can be customized with the
            ``elements`` keyword argument::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: L._test_jacobi_identity(elements=[x+y, x, 2*y, x.bracket(y)])

            See the documentation for :class:`TestSuite` for more information.
            """
            tester = self._tester(**options)
            elts = tester.some_elements()
            jacobi = lambda x, y, z: self.bracket(x, self.bracket(y, z)) + \
                self.bracket(y, self.bracket(z, x)) + \
                self.bracket(z, self.bracket(x, y))
            zero = self.zero()
            for x in elts:
                for y in elts:
                    if x == y:
                        continue
                    for z in elts:
                        tester.assert_(jacobi(x, y, z) == zero)

        def _test_antisymmetry(self, **options):
            """
            Test that the antisymmetry axiom is satisfied on (not
            necessarily all) elements of this set.

            INPUT:

            - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

            EXAMPLES:

            By default, this method runs the tests only on the
            elements returned by ``self.some_elements()``::

                sage: L = LieAlgebras(QQ).example()
                sage: L._test_antisymmetry()

            However, the elements tested can be customized with the
            ``elements`` keyword argument::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: L._test_antisymmetry(elements=[x+y, x, 2*y, x.bracket(y)])

            See the documentation for :class:`TestSuite` for more information.
            """
            tester = self._tester(**options)
            elts = tester.some_elements()
            zero = self.zero()
            for x in elts:
                tester.assert_(self.bracket(x, x) == zero)

        def _test_distributivity(self, **options):
            r"""
            Test the distributivity of the Lie bracket `[,]` on `+` on (not
            necessarily all) elements of this set.

            INPUT:

            - ``options`` -- any keyword arguments accepted by :meth:`_tester`.

            TESTS::

                sage: L = LieAlgebras(QQ).example()
                sage: L._test_distributivity()

            EXAMPLES:

            By default, this method runs the tests only on the
            elements returned by ``self.some_elements()``::

                sage: L = LieAlgebra(QQ, 3, 'x,y,z', representation="polynomial")
                sage: L.some_elements()
                [x + y + z]
                sage: L._test_distributivity()

            However, the elements tested can be customized with the
            ``elements`` keyword argument::

                sage: L = LieAlgebra(QQ, cartan_type=['A', 2]) # todo: not implemented - #16821
                sage: h1 = L.gen(0) # todo: not implemented - #16821
                sage: h2 = L.gen(1) # todo: not implemented - #16821
                sage: e2 = L.gen(3) # todo: not implemented - #16821
                sage: L._test_distributivity(elements=[h1, h2, e2]) # todo: not implemented - #16821

            See the documentation for :class:`TestSuite` for more information.
            """
            tester = self._tester(**options)
            S = tester.some_elements()
            from sage.misc.misc import some_tuples
            for x,y,z in some_tuples(S, 3, tester._max_runs):
                # left distributivity
                tester.assert_(self.bracket(x, (y + z))
                               == self.bracket(x, y) + self.bracket(x, z))
                # right distributivity
                tester.assert_(self.bracket((x + y), z)
                               == self.bracket(x, z) + self.bracket(y, z))

    class ElementMethods:
        @coerce_binop
        def bracket(self, rhs):
            """
            Return the Lie bracket ``[self, rhs]``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: x.bracket(y)
                -[1, 3, 2] + [3, 2, 1]
                sage: x.bracket(0)
                0
            """
            return self._bracket_(rhs)

        # Implement this method to define the Lie bracket. You do not
        # need to deal with the coercions here.
        @abstract_method
        def _bracket_(self, y):
            """
            Return the Lie bracket ``[self, y]``, where ``y`` is an
            element of the same Lie algebra as ``self``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).example()
                sage: x,y = L.lie_algebra_generators()
                sage: x._bracket_(y)
                -[1, 3, 2] + [3, 2, 1]
                sage: y._bracket_(x)
                [1, 3, 2] - [3, 2, 1]
                sage: x._bracket_(x)
                0
            """

        @abstract_method(optional=True)
        def to_vector(self):
            """
            Return the vector in ``g.module()`` corresponding to the
            element ``self`` of ``g`` (where ``g`` is the parent of
            ``self``).

            Implement this if you implement ``g.module()``.
            See :meth:`LieAlgebras.module` for how this is to be done.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: u = L((1, 0, 0)).to_vector(); u
                (1, 0, 0)
                sage: parent(u)
                Vector space of dimension 3 over Rational Field
            """

        @abstract_method(optional=True)
        def lift(self):
            """
            Return the image of ``self`` under the canonical lift from the Lie
            algebra to its universal enveloping algebra.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: a, b, c = L.lie_algebra_generators()
                sage: elt = 3*a + b - c
                sage: elt.lift()
                3*b0 + b1 - b2

            ::

                sage: L.<x,y> = LieAlgebra(QQ, abelian=True)
                sage: x.lift()
                x
            """

        def killing_form(self, x):
            """
            Return the Killing form of ``self`` and ``x``.

            EXAMPLES::

                sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
                sage: a, b, c = L.lie_algebra_generators()
                sage: a.killing_form(b)
                0
            """
            return self.parent().killing_form(self, x)

class LiftMorphism(Morphism):
    """
    The natural lifting morphism from a Lie algebra to its
    enveloping algebra.
    """
    def __init__(self, domain, codomain):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
            sage: f = L.lift

        We skip the category test since this is currently not an element of
        a homspace::

            sage: TestSuite(f).run(skip="_test_category")
        """
        Morphism.__init__(self, Hom(domain, codomain))

    def _call_(self, x):
        """
        Lift ``x`` to the universal enveloping algebra.

        EXAMPLES::

            sage: L = LieAlgebras(QQ).FiniteDimensional().WithBasis().example()
            sage: a, b, c = L.lie_algebra_generators()
            sage: L.lift(3*a + b - c)
            3*b0 + b1 - b2
        """
        return x.lift()

