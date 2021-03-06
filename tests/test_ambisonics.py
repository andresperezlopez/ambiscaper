# from ambiscaper.ambisonics import r128stats, get_integrated_lufs
# import numpy as np
# import os
# import pytest
# from ambiscaper.ambiscaper_exceptions import ScaperError
# from pkg_resources import resource_filename


import numpy as np
from numpy import pi, sqrt
import pytest
from ambiscaper.ambisonics import get_spherical_harmonic_normalization_coef, change_channel_ordering_fuma_2_acn, change_normalization_fuma_2_sn3d
from ambiscaper.ambisonics import get_ambisonics_spread_coefs
from ambiscaper.ambisonics import get_number_of_ambisonics_channels
from ambiscaper.ambisonics import get_ambisonics_coefs
from ambiscaper.ambisonics import _validate_ambisonics_order
from ambiscaper.ambisonics import _validate_ambisonics_degree
from ambiscaper.ambisonics import _validate_spread_coef
from ambiscaper.ambisonics import _validate_ambisonics_angle
from ambiscaper.ambisonics import _get_spread_gain
from ambiscaper.ambisonics import _get_spread_gain_weight
from ambiscaper.ambiscaper_exceptions import AmbiScaperError



def test_validate_ambisonics_order():

    def __test_bad_ambisonics_order(order):
        pytest.raises(AmbiScaperError, _validate_ambisonics_order,
                      order)

    bad_order_values = [-1, 1.5, '1']
    for bov in bad_order_values:
        __test_bad_ambisonics_order(bov)

def test_validate_ambisonics_degree():

    def __test_bad_ambisonics_degree(degree,order):
        pytest.raises(AmbiScaperError, _validate_ambisonics_degree,
                      degree,order)

    order = 3
    bad_degree_values = [5, -4, 1.5, '1']
    for bdv in bad_degree_values:
        __test_bad_ambisonics_degree(bdv,order)

    order = 1
    bad_degree_values = [2, -2, 1.5, '1']
    for bdv in bad_degree_values:
        __test_bad_ambisonics_degree(bdv, order)


def test_get_number_of_ambisonics_channels():

    # some known values
    orders = [0,1,2,3,4,5]
    numchannels = [1,4,9,16,25,36]
    for i,j in enumerate(orders):
        assert numchannels[i] == get_number_of_ambisonics_channels(orders[i])


def test_validate_angle():

    def __test_bad_angle(angle):
        pytest.raises(AmbiScaperError,_validate_ambisonics_angle,angle)

    # not a number
    bad_angle_values = ['1', None]
    for bav in bad_angle_values:
        __test_bad_angle(bav)


def test_get_spherical_harmonic_normalization_coef():

    def __assert_correct_spherical_harmonic_normalization(order, degree, value):
        assert(np.isclose([value],[get_spherical_harmonic_normalization_coef(order,degree)]))

        # so...
        # we can get some results of the sph_harm coeficients at references such as
        # http://mathworld.wolfram.com/SphericalHarmonic.html or
        # https: // en.wikipedia.org / wiki / Table_of_spherical_harmonics  # Real_spherical_harmonics
        #
        # however, these coefficients are not directly the ones computed by the coefficient in the formula
        # https://docs.scipy.org/doc/scipy-0.19.1/reference/generated/scipy.special.sph_harm.html
        # (which are the ones computed by get_spherical_harmonic_normalization_coef() )
        # since they include as well the contribution of the coefficients from the Legendre polynomial P_l^m
        #
        # so, in order to evaluate get_spherical_harmonic_normalization_coef(),
        # we must add the contribution of the polynomial's coefficients
        # (see http://mathworld.wolfram.com/AssociatedLegendrePolynomial.html)
    correct_args = [
                        [0, 0, sqrt(1 / (4 * pi))               ],
                        [1, 0, (1/2.)*(sqrt(3/pi))              ],
                        [1, 1, (1/2.)*(sqrt(3/(2*pi)))          ],
                        [2, 0, (1/4.)*(sqrt(5/pi))       *2     ],
                        [2, 1, (1/2.)*(sqrt(15/(2*pi)))  /3.    ],
                        [2, 2, (1/4.)*(sqrt(15/(2*pi)))  /3.    ],
                        [3, 0, (1/4.)*(sqrt(7/pi))       *2     ],
                        [3, 1, (1/8.)*(sqrt(21/pi))      *2/3.  ],
                        [3, 2, (1/4.)*(sqrt(105/(2*pi))) /15.   ],
                        [3, 3, (1/8.)*(sqrt(35/pi))      /15.   ],
    ]
    for correct_arg in correct_args:
        __assert_correct_spherical_harmonic_normalization(*correct_arg) # splat operator




def test_get_ambisonics_coefs():
    def __assert_correct_ambisonics_coefs(azimuth,elevation,order,groundtruth):
        # print(azimuth, elevation)
        # print(groundtruth)
        # print(get_ambisonics_coefs(azimuth,elevation,order))
        assert np.allclose(groundtruth,get_ambisonics_coefs(azimuth,elevation,order),rtol=1e-4,atol=1e-4)


    order = 5

    correct_args = [ #  azimuth, elevation, order, groundtruth

        # sampled points of the sphere in azimuth {0, pi/2... 3pi/2}, elevation {-pi/2, -pi/4... pi/2}
        [0., -pi/2, order,
         np.array([
             1.000000, -0.000000, -1.000000, -0.000000, 0.000000, 0.000000,
             1.000000, 0.000000, 0.000000, -0.000000, -0.000000, -0.000000,
             -1.000000, -0.000000, -0.000000, -0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 1.000000, 0.000000, 0.000000, 0.000000,
             0.000000, -0.000000, -0.000000, -0.000000, -0.000000, -0.000000,
             -1.000000, -0.000001, -0.000000, -0.000000, -0.000000, -0.000000])],

        [0., -pi/4, order,
         np.array([
             1.000000, 0.000000, -0.707107, 0.707107, 0.000000, -0.000000,
             0.250000, -0.866025, 0.433013, 0.000000, -0.000000, 0.000000,
             0.176777, 0.649519, -0.684653, 0.279508, 0.000000, -0.000000,
             0.000000, -0.000000, -0.406250, -0.197643, 0.698771, -0.522912,
             0.184877, 0.000000, -0.000000, 0.000000, -0.000000, -0.000000,
             0.375650, -0.256745, -0.452856, 0.647071, -0.392184, 0.124020])],

        [0., 0., order,
         np.array([
             1.000000, 0.000000, 0.000000, 1.000000, 0.000000, 0.000000,
             -0.500000, 0.000000, 0.866025, 0.000000, 0.000000, -0.000000,
             -0.000000, -0.612372, 0.000000, 0.790569, 0.000000, 0.000000,
             -0.000000, -0.000000, 0.375000, -0.000000, -0.559017, 0.000000,
             0.739510, 0.000000, 0.000000, -0.000000, -0.000000, 0.000000,
             0.000000, 0.484123, -0.000000, -0.522913, 0.000000, 0.701561])],

        [0., pi/4, order,
         np.array([
             1.000000, 0.000000, 0.707107, 0.707107, 0.000000, 0.000000,
             0.250000, 0.866025, 0.433013, 0.000000, 0.000000, 0.000000,
             -0.176777, 0.649519, 0.684653, 0.279509, 0.000000, 0.000000,
             0.000000, 0.000000, -0.406250, 0.197642, 0.698771, 0.522913,
             0.184878, 0.000000, 0.000000, 0.000000, 0.000000, -0.000000,
             -0.375650, -0.256745, 0.452855, 0.647071, 0.392185, 0.124020])],

        [0., pi/2, order,
         np.array([
             1.000000, -0.000000, 1.000000, -0.000000, 0.000000, -0.000000,
             1.000000, -0.000000, 0.000000, -0.000000, 0.000000, -0.000000,
             1.000000, -0.000000, 0.000000, -0.000000, 0.000000, -0.000000,
             0.000000, -0.000000, 1.000000, -0.000001, 0.000000, -0.000000,
             0.000000, -0.000000, 0.000000, -0.000000, 0.000000, -0.000000,
             1.000000, -0.000001, 0.000000, -0.000000, 0.000000, -0.000000])],

        [pi/2, -pi/2, order,
         np.array([
             1.000000, -0.000000, -1.000000, 0.000000, -0.000000, 0.000000,
             1.000000, -0.000000, -0.000000, 0.000000, 0.000000, -0.000000,
             -1.000000, 0.000000, 0.000000, -0.000000, 0.000000, -0.000000,
             -0.000000, 0.000000, 1.000000, -0.000000, -0.000000, 0.000000,
             0.000000, -0.000000, -0.000000, 0.000000, 0.000000, -0.000001,
             -1.000000, 0.000000, 0.000000, -0.000000, -0.000000, 0.000000])],

        [pi/2, -pi/4, order,
         np.array([
             1.000000, 0.707107, -0.707107, -0.000000, -0.000000, -0.866025,
             0.250000, 0.000000, -0.433013, -0.279508, 0.000000, 0.649519,
             0.176777, -0.000000, 0.684653, 0.000000, 0.000000, 0.522912,
             -0.000000, -0.197643, -0.406250, 0.000000, -0.698771, -0.000000,
             0.184877, 0.124020, -0.000000, -0.647071, 0.000000, -0.256745,
             0.375650, 0.000000, 0.452856, 0.000000, -0.392184, -0.000000])],

        [pi/2, 0., order,
         np.array([
             1.000000, 1.000000, 0.000000, -0.000000, -0.000000, 0.000000,
             -0.500000, -0.000000, -0.866025, -0.790569, -0.000000, -0.612372,
             -0.000000, 0.000000, -0.000000, 0.000000, 0.000000, -0.000000,
             0.000000, -0.000000, 0.375000, 0.000000, 0.559017, 0.000000,
             0.739510, 0.701561, 0.000000, 0.522913, 0.000000, 0.484123,
             0.000000, -0.000000, 0.000000, -0.000000, 0.000000, -0.000000])],

        [pi/2, pi/4, order,
         np.array([
             1.000000, 0.707107, 0.707107, -0.000000, -0.000000, 0.866025,
             0.250000, -0.000000, -0.433013, -0.279509, -0.000000, 0.649519,
             -0.176777, -0.000000, -0.684653, 0.000000, 0.000000, -0.522913,
             -0.000000, 0.197642, -0.406250, -0.000000, -0.698771, 0.000000,
             0.184878, 0.124020, 0.000000, -0.647071, -0.000000, -0.256745,
             -0.375650, 0.000000, -0.452855, 0.000000, 0.392185, -0.000000])],

        [pi/2, pi/2, order,
         np.array([
             1.000000, -0.000000, 1.000000, 0.000000, -0.000000, -0.000000,
             1.000000, 0.000000, -0.000000, 0.000000, -0.000000, -0.000000,
             1.000000, 0.000000, -0.000000, -0.000000, 0.000000, 0.000000,
             -0.000000, -0.000001, 1.000000, 0.000000, -0.000000, -0.000000,
             0.000000, -0.000000, 0.000000, 0.000000, -0.000000, -0.000001,
             1.000000, 0.000000, -0.000000, -0.000000, 0.000000, 0.000000])],

        [pi, -pi/2, order,
         np.array([
             1.000000, 0.000000, -1.000000, 0.000000, 0.000000, -0.000000,
             1.000000, -0.000000, 0.000000, 0.000000, -0.000000, 0.000000,
             -1.000000, 0.000000, -0.000000, 0.000000, 0.000000, -0.000000,
             0.000000, -0.000000, 1.000000, -0.000000, 0.000000, -0.000000,
             0.000000, 0.000000, -0.000000, 0.000000, -0.000000, 0.000000,
             -1.000000, 0.000001, -0.000000, 0.000000, -0.000000, 0.000000])],

        [pi, -pi/4, order,
         np.array([
             1.000000, -0.000000, -0.707107, -0.707107, 0.000000, 0.000000,
             0.250000, 0.866025, 0.433013, -0.000000, -0.000000, -0.000000,
             0.176777, -0.649519, -0.684653, -0.279508, 0.000000, 0.000000,
             0.000000, 0.000000, -0.406250, 0.197643, 0.698771, 0.522912,
             0.184877, -0.000000, -0.000000, -0.000000, -0.000000, 0.000000,
             0.375650, 0.256745, -0.452856, -0.647071, -0.392184, -0.124020])],

        [pi, 0., order,
         np.array([
             1.000000, -0.000000, 0.000000, -1.000000, 0.000000, -0.000000,
             -0.500000, -0.000000, 0.866025, -0.000000, 0.000000, 0.000000,
             -0.000000, 0.612372, 0.000000, -0.790569, 0.000001, -0.000000,
             -0.000000, 0.000000, 0.375000, 0.000000, -0.559017, -0.000000,
             0.739510, -0.000001, 0.000000, 0.000000, -0.000000, -0.000000,
             0.000000, -0.484123, -0.000000, 0.522913, 0.000000, -0.701561])],

        [pi, pi/4, order,
         np.array([
             1.000000, -0.000000, 0.707107, -0.707107, 0.000000, -0.000000,
             0.250000, -0.866025, 0.433013, -0.000000, 0.000000, -0.000000,
             -0.176777, -0.649519, 0.684653, -0.279509, 0.000000, -0.000000,
             0.000000, -0.000000, -0.406250, -0.197642, 0.698771, -0.522913,
             0.184878, -0.000000, 0.000000, -0.000000, 0.000000, 0.000000,
             -0.375650, 0.256745, 0.452855, -0.647071, 0.392185, -0.124020])],

        [pi, pi/2, order,
         np.array([
             1.000000, 0.000000, 1.000000, 0.000000, 0.000000, 0.000000,
             1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 1.000000, 0.000001, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             1.000000, 0.000001, 0.000000, 0.000000, 0.000000, 0.000000])],

        [3*pi/2, -pi/2, order,
         np.array([
             1.000000, 0.000000, -1.000000, 0.000000, 0.000000, -0.000000,
             1.000000, -0.000000, -0.000000, -0.000000, -0.000000, 0.000000,
             -1.000000, 0.000000, 0.000000, 0.000000, -0.000000, 0.000000,
             0.000000, -0.000000, 1.000000, -0.000000, -0.000000, -0.000000,
             0.000000, 0.000000, 0.000000, -0.000000, -0.000000, 0.000001,
             -1.000000, 0.000000, 0.000000, 0.000000, -0.000000, -0.000000])],

        [3*pi/2, -pi/4, order,
         np.array([
             1.000000, -0.707107, -0.707107, -0.000000, 0.000000, 0.866025,
             0.250000, 0.000000, -0.433013, 0.279508, -0.000000, -0.649519,
             0.176777, -0.000000, 0.684653, -0.000000, -0.000000, -0.522912,
             0.000000, 0.197643, -0.406250, 0.000000, -0.698771, 0.000000,
             0.184877, -0.124020, 0.000000, 0.647071, -0.000000, 0.256745,
             0.375650, 0.000000, 0.452856, -0.000000, -0.392184, 0.000000])],

        [3*pi/2, 0., order,
         np.array([
             1.000000, -1.000000, 0.000000, -0.000000, 0.000000, -0.000000,
             -0.500000, -0.000000, -0.866025, 0.790569, 0.000000, 0.612372,
             -0.000000, 0.000000, -0.000000, -0.000000, -0.000000, 0.000000,
             -0.000000, 0.000000, 0.375000, 0.000000, 0.559017, -0.000000,
             0.739510, -0.701561, -0.000000, -0.522913, -0.000000, -0.484123,
             0.000000, -0.000000, 0.000000, 0.000000, 0.000000, 0.000001])],

        [3*pi/2, pi/4, order,
         np.array([
             1.000000, -0.707107, 0.707107, -0.000000, 0.000000, -0.866025,
             0.250000, -0.000000, -0.433013, 0.279509, 0.000000, -0.649519,
             -0.176777, -0.000000, -0.684653, -0.000000, -0.000000, 0.522913,
             0.000000, -0.197642, -0.406250, -0.000000, -0.698771, -0.000000,
             0.184878, -0.124020, -0.000000, 0.647071, 0.000000, 0.256745,
             -0.375650, 0.000000, -0.452855, -0.000000, 0.392185, 0.000000])],

        [3*pi/2, pi/2, order,
         np.array([
             1.000000, 0.000000, 1.000000, 0.000000, 0.000000, 0.000000,
             1.000000, 0.000000, -0.000000, -0.000000, 0.000000, 0.000000,
             1.000000, 0.000000, -0.000000, 0.000000, -0.000000, -0.000000,
             0.000000, 0.000001, 1.000000, 0.000000, -0.000000, 0.000000,
             0.000000, 0.000000, -0.000000, -0.000000, 0.000000, 0.000001,
             1.000000, 0.000000, -0.000000, 0.000000, 0.000000, -0.000000])],

        # some random points
        [5.228859, 0.830568, order,
         np.array([
             1.000000, -0.586485, 0.738315, 0.333056, -0.338325, -0.749997,
             0.317663, 0.425911, -0.201818, 0.005187, -0.558549, -0.619725,
             -0.101317, 0.351932, -0.333185, -0.242495, 0.134650, 0.010132,
             -0.614929, -0.279256, -0.369155, 0.158585, -0.366817, -0.473688,
             -0.072702, 0.082995, 0.298243, 0.013401, -0.469437, 0.111161,
             -0.409540, -0.063127, -0.280028, -0.626500, -0.161032, 0.051947])],
        [4.002249, 0.576942, order,
         np.array([
             1.000000, -0.635533, 0.545463, -0.546414, 0.601478, -0.600432,
             -0.053705, -0.516235, -0.091222, -0.247097, 0.733619, -0.189785,
             -0.412465, -0.163172, -0.111263, 0.394455, -0.108201, -0.356601,
             0.420366, 0.251391, -0.353445, 0.216139, -0.063754, 0.569262,
             -0.348511, 0.266213, -0.177059, -0.274214, -0.104239, 0.401952,
             -0.017052, 0.345588, 0.015809, 0.437744, -0.570300, 0.115422])],
        [0.286065, -0.938906, order,
         np.array([
             1.000000, 0.166675, -0.806912, 0.566667, 0.163591, -0.232948,
             0.476661, -0.791982, 0.254032, 0.123277, -0.295170, 0.230217,
             -0.103098, 0.782697, -0.458353, 0.106518, 0.081953, -0.263182,
             0.375691, -0.165629, -0.211912, -0.563109, 0.583390, -0.227405,
             0.037242, 0.049945, -0.198385, 0.396281, -0.372246, 0.063525,
             0.390267, 0.215973, -0.578041, 0.342411, -0.090153, 0.007062])],
        [0.697165, 1.130225, order,
         np.array([
             1.000000, 0.273805, 0.904508, 0.326950, 0.155054, 0.428958,
             0.727202, 0.512217, 0.027649, 0.053189, 0.313603, 0.518216,
             0.493262, 0.618799, 0.055922, -0.030503, 0.008454, 0.127286,
             0.473105, 0.533913, 0.235377, 0.637543, 0.084364, -0.072998,
             -0.022952, -0.003340, 0.022941, 0.223865, 0.603371, 0.477511,
             -0.011389, 0.570193, 0.107593, -0.128384, -0.062280, -0.009315])],
        [0.512645, -0.681213, order,
         np.array([
             1.000000, 0.381013, -0.629736, 0.676951, 0.446742, -0.415584,
             0.094850, -0.738373, 0.271145, 0.370381, -0.629072, 0.229317,
             0.320273, 0.407430, -0.381808, 0.012176, 0.238876, -0.617101,
             0.512138, 0.042496, -0.424090, 0.075503, 0.310836, -0.020286,
             -0.124296, 0.108481, -0.451286, 0.629390, -0.157866, -0.230454,
             0.224499, -0.409451, -0.095815, 0.020690, 0.234821, -0.166168])],
    ]
    # evaluate them
    for correct_arg in correct_args:
        __assert_correct_ambisonics_coefs(*correct_arg) # splat operator


def test_validate_ambisonics_spread_coefs():

    def __test_bad_ambisonics_spread_coefs(coef):
        pytest.raises(AmbiScaperError,_validate_spread_coef,coef)

    bad_spread_coef_values = [-0.5,3,'1', None]
    for bsv in bad_spread_coef_values:
        __test_bad_ambisonics_spread_coefs(bsv)


def test_get_spread_gain():

    def __assert_correct_spread_gains(alpha, tau, ambisonics_order, max_ambisonics_order, value):
        # print(alpha, tau, ambisonics_order, max_ambisonics_order, value)
        assert (np.isclose(
            [value],
            [_get_spread_gain(alpha, tau, ambisonics_order, max_ambisonics_order)],
            rtol=1e-3,
            atol=1e-3))

    L = 5

    # with alpha=0 (no spread), all coefs to 1
    alpha = 0.0
    tau = 1.0
    correct_args = [[alpha,tau,l,L,1.0] for l in range(L+1) ]
    for correct_arg in correct_args:
        __assert_correct_spread_gains(*correct_arg) # splat operator

    tau = 0.5
    for correct_arg in correct_args:
        __assert_correct_spread_gains(*correct_arg) # splat operator

    tau = 0.25
    correct_args = [[alpha, tau, l, L, 1.0] for l in range(L)]
    correct_args.append([alpha, tau, 5, L, 0.9847328461196255])
    for correct_arg in correct_args:
        __assert_correct_spread_gains(*correct_arg)  # splat operator


    # with alpha=1.0 (full spread), most coefs to 0
    alpha = 1.0
    tau = 1.0
    correct_args = [[alpha, tau, 0, L, 0.5]]
    [correct_args.append([alpha, tau, l+1, L, 0.0]) for l in range(L)]
    for correct_arg in correct_args:
        __assert_correct_spread_gains(*correct_arg)  # splat operator

    tau = 0.5
    correct_args = [[alpha, tau, 0, L, 0.5]]
    [correct_args.append([alpha, tau, l + 1, L, 0.0]) for l in range(L)]
    for correct_arg in correct_args:
        __assert_correct_spread_gains(*correct_arg)  # splat operator

    tau = 0.25
    correct_args = [[alpha, tau, 0, L, 0.5]]
    correct_args.append([alpha, tau, 1, L, 0.015267153880374473])
    [correct_args.append([alpha, tau, l + 2, L, 0.0]) for l in range(L-1)]
    for correct_arg in correct_args:
        __assert_correct_spread_gains(*correct_arg)  # splat operator


    # alpha=0.5
    alpha = 0.5
    tau = 1.0
    correct_args=[]
    correct_args.append([alpha, tau, 0, L, 1.0])
    correct_args.append([alpha, tau, 1, L, 1.0])
    correct_args.append([alpha, tau, 2, L, 1.0])
    correct_args.append([alpha, tau, 3, L, 0.5])
    correct_args.append([alpha, tau, 4, L, 0.0])
    correct_args.append([alpha, tau, 5, L, 0.0])
    for correct_arg in correct_args:
        __assert_correct_spread_gains(*correct_arg)  # splat operator

    tau = 0.5
    correct_args = []
    correct_args.append([alpha, tau, 0, L, 1.0])
    correct_args.append([alpha, tau, 1, L, 1.0])
    correct_args.append([alpha, tau, 2, L, 1.0])
    correct_args.append([alpha, tau, 3, L, 0.5])
    correct_args.append([alpha, tau, 4, L, 0.0])
    correct_args.append([alpha, tau, 5, L, 0.0])
    for correct_arg in correct_args:
        __assert_correct_spread_gains(*correct_arg)  # splat operator

    tau = 0.25
    correct_args = []
    correct_args.append([alpha, tau, 0, L, 1.0])
    correct_args.append([alpha, tau, 1, L, 1.0])
    correct_args.append([alpha, tau, 2, L, 0.9847328461196255])
    correct_args.append([alpha, tau, 3, L, 0.5])
    correct_args.append([alpha, tau, 4, L, 0.015267153880374473])
    correct_args.append([alpha, tau, 5, L, 0.0])
    for correct_arg in correct_args:
        __assert_correct_spread_gains(*correct_arg)  # splat operator


def test_get_spread_gain_weight():

    def __assert_correct_spread_gain_weights(alpha, tau, max_ambisonics_order, value):
        # print(alpha, tau, max_ambisonics_order, value)
        assert (np.isclose(
            [value],
            [_get_spread_gain_weight(alpha, tau, max_ambisonics_order)],
            rtol=1e-1,
            atol=1e-1))

    L = 5

    # with alpha=0 (no spread), all coefs to 1
    alpha = 0.0
    tau = 1.0
    correct_args = [alpha,tau,L,1.0]
    __assert_correct_spread_gain_weights(*correct_args) # splat operator
    tau = 0.5
    correct_args = [alpha,tau,L,1.0]
    __assert_correct_spread_gain_weights(*correct_args) # splat operator
    tau = 0.25
    correct_args = [alpha,tau,L,1.0]
    __assert_correct_spread_gain_weights(*correct_args) # splat operator

    # alpha=1 (full spread): max value
    alpha = 1.0
    tau = 1.0
    correct_args = [alpha,tau,L,7.4]
    __assert_correct_spread_gain_weights(*correct_args) # splat operator
    tau = 0.5
    correct_args = [alpha,tau,L,7.4]
    __assert_correct_spread_gain_weights(*correct_args) # splat operator
    tau = 0.25
    correct_args = [alpha,tau,L,7.4]
    __assert_correct_spread_gain_weights(*correct_args) # splat operator

    # alpha=0.7
    alpha = 0.7
    tau = 1.0
    correct_args = [alpha,tau,L,2.2]
    __assert_correct_spread_gain_weights(*correct_args) # splat operator
    tau = 0.5
    correct_args = [alpha,tau,L,2.2]
    __assert_correct_spread_gain_weights(*correct_args) # splat operator
    tau = 0.25
    correct_args = [alpha,tau,L,2.2]
    __assert_correct_spread_gain_weights(*correct_args) # splat operator


def test_get_ambisonics_spread_coefs():

    def __assert_correct_spread_coefs(alpha, tau, max_ambisonics_order, value):
        assert(np.allclose(
            value,
            get_ambisonics_spread_coefs(alpha,tau,max_ambisonics_order),
            rtol=1e-1,
            atol=1e-1))

    L = 5
    num_channels = (pow((L+1),2))

    # alpha 0, all channels to 1
    alpha = 0.0
    tau = 1.0
    correct_args = [alpha, tau, L, [1.0 for _ in range(num_channels)]]
    __assert_correct_spread_coefs(*correct_args)
    tau = 0.5
    correct_args = [alpha, tau, L, [1.0 for _ in range(num_channels)]]
    __assert_correct_spread_coefs(*correct_args)
    tau = 0.25
    correct_args = [alpha, tau, L, [1.0 for _ in range(num_channels)]]
    __assert_correct_spread_coefs(*correct_args)

    # alpha 1, only W
    alpha = 1.0
    tau = 1.0
    correct_args = [alpha, tau, L, [3.7]+[0.0 for _ in range(num_channels-1)]]
    __assert_correct_spread_coefs(*correct_args)
    tau = 0.5
    correct_args = [alpha, tau, L, [3.7]+[0.1 for _ in range(num_channels-1)]]
    __assert_correct_spread_coefs(*correct_args)
    tau = 0.25
    correct_args = [alpha, tau, L, [3.7]+[0.1 for _ in range(num_channels-1)]]
    __assert_correct_spread_coefs(*correct_args)


def test_change_channel_ordering_fuma_2_acn():

    # Bad input values
    def __test_bad_input(array):
        pytest.raises(AmbiScaperError,change_channel_ordering_fuma_2_acn,array)

    # Not an np array
    bad_values = ['1', None, [1,2,3], [[1,2],[3,4]]]
    for bv in bad_values:
        __test_bad_input(bv)

    # Not correct shape (must be 4 channels - order 1)
    bad_values = [np.asarray([[1,2,3],[4,5,6]]),
                  np.asarray([[1,2,3,4,5],[6,7,8,9,10]])]
    for bv in bad_values:
        __test_bad_input(bv)


    # Assert correct values
    def __assert_correct_input(correct_arg, groundtruth):
        np.testing.assert_array_equal(groundtruth,change_channel_ordering_fuma_2_acn(correct_arg))

    correct_arg = np.asarray([[0,1,2,3],[4,5,6,7]])
    groundtruth = np.asarray([[0,2,3,1],[4,6,7,5]])
    __assert_correct_input(correct_arg, groundtruth)


def test_change_normalization_fuma_2_sn3d():

    # Bad input values
    def __test_bad_input(array):
        pytest.raises(AmbiScaperError,change_normalization_fuma_2_sn3d,array)

    # Not an np array
    bad_values = ['1', None, [1,2,3], [[1,2],[3,4]]]
    for bv in bad_values:
        __test_bad_input(bv)

    # Not correct shape (must be 4 channels - order 1)
    bad_values = [np.asarray([[1,2,3],[4,5,6]]),
                  np.asarray([[1,2,3,4,5],[6,7,8,9,10]])]
    for bv in bad_values:
        __test_bad_input(bv)


    # Assert correct values
    def __assert_correct_input(correct_arg, groundtruth):
        np.testing.assert_array_equal(groundtruth,change_normalization_fuma_2_sn3d(correct_arg))

    correct_arg = np.asarray([[1,1,1,1],[2,2,2,2]])
    groundtruth = np.asarray([[np.sqrt(2),1,1,1],[2*np.sqrt(2),2,2,2]])
    __assert_correct_input(correct_arg, groundtruth)