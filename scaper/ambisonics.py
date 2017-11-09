'''
ambisonics.py

SN3D coefs
ACN ordering
unlimited order

reference system with right-hand rule
azimuth [0..2pi]
elevation [-pi/2..pi/2]
-X positive to (0,0)
-Y positive to (pi/2,0)
-Z positive to (_,pi/2)

'''
import numpy as np
from numpy import pi
from math import sin, cos, sqrt, factorial
from scaper.scaper_exceptions import ScaperError
from numbers import Number
from scipy.special import sph_harm

from scaper.util import delta_kronecker


def _validate_ambisonics_order(order):

    if (order<0):
        raise ScaperError(
            'Ambisonics order must be bigger than 0')
    if (not isinstance(order,int)):
        raise ScaperError(
            'Ambisonics order must be an integer')

def _validate_ambisonics_degree(degree, order):

    _validate_ambisonics_order(order)

    if (not isinstance(degree,int)):
        raise ScaperError(
            'Ambisonics degree must be an integer')
    if (np.abs(degree) > order):
        raise ScaperError(
            'Ambisonics degree modulus must be minor or equal to ambisonics order')


def get_number_of_ambisonics_channels(order):
    _validate_ambisonics_order(order)
    return pow(order+1,2)


def _validate_ambisonics_angle(angle):
    if (not isinstance(angle,Number)):
            raise ScaperError(
                'Ambisonics angle must be a number')




def get_ambisonics_coefs(azimuth,elevation,order):
    # up to the given order
    _validate_ambisonics_angle(azimuth)
    _validate_ambisonics_angle(elevation)
    _validate_ambisonics_order(order)

    coefs = []
    coef_index = 0
    for l in range(order+1):
        for m in range(-l,l+1):
            coefs.append(get_spherical_harmonic(azimuth, elevation, l, m))

    return np.array(coefs)


def get_spherical_harmonic(azimuth, elevation, ambisonics_order, ambisonics_degree):

    _validate_ambisonics_degree(ambisonics_degree, ambisonics_order)

    l = ambisonics_order
    m = abs(ambisonics_degree)

    # in the sph_harm, the elevation is defined in the range [0..pi]
    # luckily the sph_harm reference system follows the right-hand rule
    # so there is no other changes involved
    elevation_internal = elevation - (pi/2)

    # the harmonics with positive degree are the real part of the solution
    # and the ones with negative degree are the imaginary part
    # degree 0 is symmetrical for both solutions
    # check http://mathworld.wolfram.com/SphericalHarmonic.html
    if (ambisonics_degree >= 0):
        coef = get_real_spherical_harmonic(azimuth,elevation_internal,l, m)
    else:
        coef = get_imag_spherical_harmonic(azimuth,elevation_internal,l, m)

    # normalization
    #
    # get_real_spherical_harmonic returns a value with a different normalization
    # that the one we want
    # (check https://docs.scipy.org/doc/scipy-0.19.1/reference/generated/scipy.special.sph_harm.html)
    #
    # therefore we "take it out" from the result, and apply our desired SN3D normalization
    # as described in Daniel2003, 2.1 (http://gyronymo.free.fr/audio3D/publications/AES23%20NFC%20HOA.pdf)
    # we must account as well for the Condon-Shortley phase, which is already included in coef
    sn3d_factor = pow(-1,m) *sqrt ( (2-delta_kronecker(0,m)) * ( float(factorial(l-m)) / float(factorial(l+m)) ) )
    coef = coef / get_spherical_harmonic_normalization_coef(ambisonics_order,ambisonics_degree) * sn3d_factor

    # if we would want to include N3D support at some moment, uncomment this lines
    # n3d_factor =  sqrt((2*l)+1)
    # coef = coef * n3d_factor

    return coef


def get_spherical_harmonic_normalization_coef(order,degree):
    # standard normalization function, without Condon-Shotley

    # we can use it to divide the sph_harm function by this number and get 1-normalization

    # this is the default coef given by sph_harm function

    # this is an implementation of the normalization function provided by sph_harm
    # see https://docs.scipy.org/doc/scipy-0.19.1/reference/generated/scipy.special.sph_harm.html
    #
    # it follows the standard normalization convention as used IIRC in physics
    # since we want SN3D and not this one, we use this function to compute it
    # in order to substract it to the resulting coefficients, and then applying
    # the SN3D normalization
    #
    # notice that Condon-Shortley phase is not included here, since it is calculated internally
    # by means of lpmv function
    l = order
    m = abs(degree)
    return  sqrt( ( ((2*l)+1) / (4*pi) ) * ( float(factorial(l-m)) / float(factorial(l+m)) ) )


def get_real_spherical_harmonic(azimuth, elevation, ambisonics_order, ambisonics_degree):
    # NOTE THAT EVERYTHING IS CHANGED RESPECT TO THE MAN ENTRY
    # here, we use phi as azimuth and theta as elevation
    # furthermore, L is ambisonics order and M is ambisonics degree
    return np.asscalar(np.real(sph_harm(ambisonics_degree,ambisonics_order,azimuth,elevation)))

def get_imag_spherical_harmonic(azimuth, elevation, ambisonics_order, ambisonics_degree):
    # NOTE THAT EVERYTHING IS CHANGED RESPECT TO THE MAN ENTRY
    # here, we use phi as azimuth and theta as elevation
    # furthermore, L is ambisonics order and M is ambisonics degree
    return np.asscalar(np.imag(sph_harm(ambisonics_degree,ambisonics_order,azimuth,elevation)))


################################################
# This is the old implementation up to order 3,
# with explicit equations taken from from
# D. Malham, 'Higher order Ambisonic systems'
# https://www.york.ac.uk/inst/mustech/3d_audio/higher_order_ambisonics.pdf
# notice that phi and theta are switched from standard...
#
# left here just in case for convenience
################################################
#
# def get_ambisonics_coefs(azimuth,elevation,order):
#
#     _validate_angle(azimuth)
#     _validate_angle(elevation)
#     _validate_ambisonics_order(order)
#
#     # azimuth and elevation values are fine as long as they are real numbers...
#
#     coefs = np.zeros(get_number_of_ambisonics_channels(order))
#
#     a = azimuth     # usually phi
#     e = elevation   # usually theta
#
#     if (order >= 0):
#         coefs[0] = 1. # W
#
#     if (order >= 1):
#         coefs[1] = sin(a) * cos(e)    # Y
#         coefs[2] = sin(e)             # Z
#         coefs[3] = cos(a) * cos(e)    # X
#
#     if (order >= 2):
#         coefs[4] = (sqrt(3)/2.) * sin(2*a) * pow(cos(e),2)    # V
#         coefs[5] = (sqrt(3)/2.) * sin(a) * sin(2*e)           # T
#         coefs[6] = 0.5 * ( 3*pow(sin(e),2)-1 )                # R
#         coefs[7] = (sqrt(3)/2.) * cos(a) * sin(2*e)           # S
#         coefs[8] = (sqrt(3)/2.) * cos(2*a) * pow(cos(e),2)    # U
#
#     if (order >= 3):
#         coefs[9] = (sqrt(5./8.)) * sin(3*a) * pow(cos(e),3)                   # Q
#         coefs[10] = (sqrt(15)/2.) * sin(2*a) * sin(e) * pow(cos(e),2)         # O
#         coefs[11] = (sqrt(3./8.)) * sin(a) * cos(e) * (5*(pow(sin(e),2))-1)   # M
#         coefs[12] = 0.5 * ( sin(e) * (5*(pow(sin(e),2))-3) )                  # K
#         coefs[13] = (sqrt(3./8.)) * cos(a) * cos(e) * ((5*pow(sin(e),2))-1)   # L
#         coefs[14] = (sqrt(15)/2.) * cos(2*a) * sin(e) * pow(cos(e),2)         # N
#         coefs[15] = (sqrt(5./8.)) * cos(3*a) * pow(cos(e),3)                  # P
#
#     return coefs