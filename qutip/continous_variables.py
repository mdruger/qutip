# This file is part of QuTIP.
#
#    QuTIP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    QuTIP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QuTIP.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2011-2013, Paul D. Nation & Robert J. Johansson
#
###########################################################################

"""
This module contains experimental functions for calculating continous
variable quantities from fock-basis representation of the state of
coupled harmonic modes
"""

from qutip.expect import expect
import numpy as np


def covariance_matrix(basis, rho):
    """
    The covariance matrix given a basis of operators.

    Parameters
    ----------

    basis : list of :class:`qutip.qobj.Qobj`
        List of operators that defines the basis for the covariance matrix.

    rho : :class:`qutip.qobj.Qobj`
        Density matrix for which to calculate the covariance matrix

    Returns
    -------

    cov_mat: *array*
        A 2-dimensional *array* of covariance values. 

    """

    return np.array([[expect(op1 * op2 + op2 * op1, rho) -
                      expect(op1, rho) * expect(op2, rho)
                      for op1 in basis]
                     for op2 in basis])


def correlation_matrix_field(a1, a2, rho=None):
    """
    Calculate the correlation matrix for given field operators :math:`a_1` and
    :math:`a_2`. If a density matrix is given the expectation values are
    calculated, otherwise a matrix with operators is returned.

    Parameters
    ----------

    a1 : :class:`qutip.qobj.Qobj`
        Field operator for mode 1.

    a2 : :class:`qutip.qobj.Qobj`
        Field operator for mode 2.

    rho : :class:`qutip.qobj.Qobj`
        Density matrix for which to calculate the covariance matrix.

    Returns
    -------

    cov_mat: *array* of complex numbers or :class:`qutip.qobj.Qobj`
        A 2-dimensional *array* of covariance values, or, if rho=0, a matrix
        of operators.
    """

    basis = [a1, a1.dag(), a2, a2.dag()]

    return _correlation_matrix(basis, rho)


def correlation_matrix_quadrature(a1, a2, rho=None):
    """
    Calculate the quadrature correlation matrix with given field operators
    :math:`a_1` and :math:`a_2`. If a density matrix is given the expectation
    values are calculated, otherwise a matrix with operators is returned.

    Parameters
    ----------

    a1 : :class:`qutip.qobj.Qobj`
        Field operator for mode 1.

    a2 : :class:`qutip.qobj.Qobj`
        Field operator for mode 2.

    rho : :class:`qutip.qobj.Qobj`
        Density matrix for which to calculate the covariance matrix.

    Returns
    -------

    cov_mat: *array* of complex numbers or :class:`qutip.qobj.Qobj`
        A 2-dimensional *array* of covariance values for the field quadratures, 
        or, if rho=0, a matrix of operators.

    """
    x1 = (a1 + a1.dag()) / np.sqrt(2)
    p1 = 1j * (a1 - a1.dag()) / np.sqrt(2)
    x2 = (a2 + a2.dag()) / np.sqrt(2)
    p2 = 1j * (a2 - a2.dag()) / np.sqrt(2)

    basis = [x1, p1, x2, p2]

    return _correlation_matrix(basis, rho)


def wigner_covariance_matrix(a1=None, a2=None, R=None, rho=None):
    """
    calculate the wigner covariance matrix given the quadrature correlation
    matrix (R) and a state.

    .. note::

        Experimental.

    """
    if R is not None:

        if rho is None:
            return np.array([[np.real(R[i, j] + R[j, i])
                              for i in range(4)]
                             for j in range(4)])
        else:
            return np.array([[np.real(expect(R[i, j] + R[j, i], rho))
                              for i in range(4)]
                             for j in range(4)])

    elif a1 is not None and a2 is not None:

        if rho is not None:
            x1 = (a1 + a1.dag()) / np.sqrt(2)
            p1 = 1j * (a1 - a1.dag()) / np.sqrt(2)
            x2 = (a2 + a2.dag()) / np.sqrt(2)
            p2 = 1j * (a2 - a2.dag()) / np.sqrt(2)
            return covariance_matrix([x1, p1, x2, p2], rho)
        else:
            raise ValueError("Must give rho if using field operators " +
                             "(a1 and a2)")

    else:
        raise ValueError("Must give either field operators (a1 and a2) " +
                         "or a precomputed correlation matrix (R)")


def wigner_logarithm_negativity(V):
    """
    Calculate the logarithmic negativity given the Wigner covariance matrix.

    .. note::

        Experimental.

    """

    A = V[0:2, 0:2]
    B = V[2:4, 2:4]
    C = V[0:2, 2:4]

    sigma = np.linalg.det(A) + np.linalg.det(B) - 2 * np.linalg.det(C)
    nu = np.sqrt(sigma / 2 - np.sqrt(sigma ** 2 - 4 * np.linalg.det(V)) / 2)
    lognu = -np.log(2 * nu)
    logneg = max(0, lognu)

    return logneg

def _correlation_matrix(basis, rho=None):
    """
    Internal function for calculating a correlation matrix given a list
    of operators to use as basis.
    """

    if rho is None:
        # return array of operators
        return np.array([[op1 * op2 for op1 in basis] for op2 in basis])
    else:
        # return array of expectation balues
        return np.array([[expect(op1 * op2, rho) for op1 in basis]
                         for op2 in basis])

