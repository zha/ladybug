# coding=utf-8
from __future__ import division

from ladybug.datatype.speed import Speed
from ladybug.datatype.generic import GenericType
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.header import Header
from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection
from ladybug.dt import DateTime
from ladybug.epw import EPW
from ladybug.windrose import WindRose, linspace, histogram, histogram_circular
from ladybug_geometry.geometry2d.polygon import Polygon2D
from ladybug_geometry.geometry2d.mesh import Mesh2D

from pprint import pprint as pp
import os
import math

# Simplify method names
linspace = HourlyContinuousCollection.linspace
histogram = HourlyContinuousCollection.histogram
histogram_circular = HourlyContinuousCollection.histogram_circular

#from ladybug.legend import Legend, LegendParameters
#from ladybug.datacollectionimmutable import HourlyContinuousCollectionImmutable


def _rad2deg(r):
    return r * 180. / math.pi


def _deg2rad(d):
    return d * math.pi / 180.


def test_linspace():
    """Test the generation of bin array from bin range and num"""

    # Base case
    bin_arr = linspace(0, 360, 0)
    assert [] == bin_arr, bin_arr

    bin_arr = linspace(0, 360, 1)
    assert [0] == bin_arr, bin_arr

    bin_arr = linspace(0, 360, 2)
    assert [0, 360.0] == bin_arr, bin_arr

    bin_arr = linspace(0, 360, 4)
    assert [0.0, 120.0, 240.0, 360.0] == bin_arr, bin_arr

    bin_arr = linspace(0, 360, 5)
    assert [0.0, 90.0, 180.0, 270.0, 360.0] == bin_arr, bin_arr

    # Start from non zero
    bin_arr = linspace(180, 360, 4)
    assert [180.0, 240.0, 300.0, 360.0] == bin_arr, bin_arr

    # Start from non zero, w/ floats
    bin_arr = linspace(180., 360., 4)
    assert [180., 240.0, 300.0, 360.0] == bin_arr, bin_arr


def test_histogram():
    """Test the windrose histogram."""

    # Test simple 2 div
    bin_arr = linspace(0, 2, 3)
    assert bin_arr == [0, 1, 2]
    vals = [0, 0, 0, 1, 1, 1, 2, 2]
    hist = histogram(vals, bin_arr)
    assert hist == [[0, 0, 0], [1, 1, 1]]

    # Test out of bounds with 3 divisions
    bin_arr = linspace(0, 3, 4)
    vals = [0, 0, 0, 1, 1, 1, 2, 2]
    hist = histogram(vals, bin_arr)
    assert hist == [[0, 0, 0], [1, 1, 1], [2, 2]]

    # Test out of bounds with 2 divisions
    bin_arr = linspace(0, 3, 3)
    vals = [-1, -2, 10, 0, 0, 0, 1, 1, 1, 2, 2, 34]
    hist = histogram(vals, bin_arr)
    assert hist == [[-2, -1, 0, 0, 0, 1, 1, 1], [2, 2]], hist

    # Test edge bounds
    bin_arr = linspace(0, 3, 3)
    vals = [0, 0, 0, 1, 1, 1, 2, 2, 3, 3]
    hist = histogram(vals, bin_arr)
    assert hist == [[0, 0, 0, 1, 1, 1], [2, 2]], hist

    # Test edge bounds 2
    hist = histogram([0, 0, 0.9, 1, 1.5, 1.99, 2, 3], (0, 1, 2, 3))
    assert hist == [[0, 0, 0.9], [1, 1.5, 1.99], [2]], hist


def test_histogram_circular():
    """Test the windrose histogram_circular data."""

    # Test out of bounds with 3 divisions
    bin_arr = linspace(-2, 2, 3)
    assert bin_arr == [-2, 0, 2], bin_arr
    vals = [-2, -1, 0, 0, 0, 1, 1, 1, 2, 2]
    hist = histogram_circular(vals, bin_arr)
    assert hist == [[-2, -1], [0, 0, 0, 1, 1, 1]], hist


def test_bin_vectors():
    """Bin vectors"""

    # Testing vals
    dir_vals = [0, 0, 0, 10, 85, 90, 95, 170, 285, 288]
    spd_vals = dir_vals

    # Make into fake data collections
    a_per = AnalysisPeriod(6, 21, 12, 6, 21, 13)
    dates = [DateTime(6, 21, i) for i in range(len(dir_vals))]
    spd_header = Header(Speed(), 'm/s', a_per)
    dir_header = Header(GenericType('Direction', 'deg'), 'deg', a_per)
    spd_data = HourlyDiscontinuousCollection(spd_header, spd_vals, dates)
    dir_data = HourlyDiscontinuousCollection(dir_header, dir_vals, dates)

    # Init simple dir set divided by 4
    w = WindRose(dir_data, spd_data, 4)

    # # Testing
    # bin_vecs = w.bin_vectors
    # f = _deg2rad
    # a = [315, 45., 45, 135, 135, 225, 225, 315]
    # #a = WindRose._compute_plotting_angles(a)
    # a = [_deg2rad(_a) for _a in a]
    # chk_bin_vecs = [[(-math.cos(45),  math.sin(45)),   # 0
    #                  (math.cos(a[1]), math.sin(a[1]))],
    #                 [(math.cos(a[1]), -math.sin(a[1])),   # 1
    #                  (math.cos(a[2]), -math.sin(a[2]))],
    #                 [(math.cos(a[2]), -math.sin(a[2])),   # 2
    #                  (math.cos(a[3]), -math.sin(a[3]))],
    #                 [(math.cos(a[3]), -math.sin(a[3])),   # 3
    #                  (-math.cos(a[4]), -math.sin(a[4]))]]

    # for i, (chk_vec, vec) in enumerate(zip(chk_bin_vecs, bin_vecs)):
    #     # Check x, y
    #     print([_rad2deg(_chk_vec) for _chk_vec in chk_vec[1]])
    #     print([_rad2deg(_vec) for _vec in vec[1]])
    #     print('--')
    #     # left vec
    #     assert abs(chk_vec[0][0] - vec[0][0]) < 1e-5, (i, chk_vec[0][0], vec[0][0])
    #     assert abs(chk_vec[0][1] - vec[0][1]) < 1e-5, (i, chk_vec[0][1], vec[0][1])
    #     # right vec
    #     assert abs(chk_vec[1][0] - vec[1][0]) < 1e-5, (i, chk_vec[1][0], vec[1][0])
    #     assert abs(chk_vec[1][1] - vec[1][1]) < 1e-5, (i, chk_vec[1][1], vec[1][1])


def test_xticks_radial():
    """Test polar coordinate array"""

    # Testing vals
    dir_vals = [0, 0, 0, 10, 85, 90, 95, 170, 285, 288]
    spd_vals = dir_vals

    # Make into fake data collections
    a_per = AnalysisPeriod(6, 21, 12, 6, 21, 13)
    dates = [DateTime(6, 21, i) for i in range(len(dir_vals))]
    spd_header = Header(Speed(), 'm/s', a_per)
    dir_header = Header(GenericType('Direction', 'deg'), 'deg', a_per)
    spd_data = HourlyDiscontinuousCollection(spd_header, spd_vals, dates)
    dir_data = HourlyDiscontinuousCollection(dir_header, dir_vals, dates)

    # # Init simple dir set divided by 4
    # w = WindRose(dir_data, spd_data, 4)
    # # Testing
    # bin_vecs = w.bin_vectors
    # xticks = WindRose._xtick_radial_lines(bin_vecs)

    # f = _deg2rad
    # cos, sin = math.cos, math.sin
    # chk_xticks = [
    #     [(0, 0), (cos(f(315)), -sin(f(315)))],
    #     [(0, 0), (cos(f(45.)), -sin(f(45.)))],
    #     [(0, 0), (cos(f(45)), -sin(f(45)))],
    #     [(0, 0), (cos(f(135)), -sin(f(135)))],
    #     [(0, 0), (cos(f(135)), -sin(f(135)))],
    #     [(0, 0), (cos(f(225)), -sin(f(225)))],
    #     [(0, 0), (cos(f(225)), -sin(f(225)))],
    #     [(0, 0), (cos(f(315)), -sin(f(315)))]]

    # for i, (chk_xtick, xtick) in enumerate(zip(chk_xticks, xticks)):
    #     # Check x, y
    #     assert abs(chk_xtick[1][0] - xtick.to_array()[1][0]) < 1e-10
    #     assert abs(chk_xtick[1][1] - xtick.to_array()[1][1]) < 1e-10


def test_radial_histogram():
    """ Test circular histogram"""
    # Testing vals
    dir_vals = [0, 0, 0, 10, 85, 90, 95, 170, 285, 288]
    spd_vals = dir_vals

    # Make into fake data collections
    a_per = AnalysisPeriod(6, 21, 12, 6, 21, 13)
    dates = [DateTime(6, 21, i) for i in range(len(dir_vals))]
    spd_header = Header(Speed(), 'm/s', a_per)
    dir_header = Header(GenericType('Direction', 'deg'), 'deg', a_per)
    spd_data = HourlyDiscontinuousCollection(spd_header, spd_vals, dates)
    dir_data = HourlyDiscontinuousCollection(dir_header, dir_vals, dates)

    # Init simple dir set divided by 4
    w = WindRose(dir_data, spd_data, 4)

    # Testing
    bin_vecs = w.bin_vectors
    vec_cpt = (0, 0)
    radius_arr = (0., 1.)
    ytick_num = 1
    hist = w.histogram_data
    histstack = w._histogram_data_stacked(hist, ytick_num)
    show_stack = False
    vecs = WindRose._histogram_array_radial(bin_vecs, vec_cpt, hist, histstack,
                                            radius_arr, show_stack)

    # f = _deg2rad
    # cos, sin = math.cos, math.sin
    # # Init simple dir set divided by 4
    # chk_vecs = [
    #     [(0, 0), (cos(f(45)), -sin(f(45))), (cos(f(315)), -sin(f(315)))],
    #     [(0, 0), (cos(f(135)), -sin(f(135))), (cos(f(45)), -sin(f(45)))],
    #     [(0, 0), (cos(f(225)), -sin(f(225))), (cos(f(135)), -sin(f(135)))],
    #     [(0, 0), (cos(f(315)), -sin(f(315))), (cos(f(225)), -sin(f(225)))]]

    # # Get histogram properties for calculating radius
    # min_bar_radius, max_bar_radius = radius_arr
    # delta_bar_radius = max_bar_radius - min_bar_radius
    # max_bar_num = max([len(bar) for bar in hist])

    # for i, (chk_vec, vec) in enumerate(zip(chk_vecs, vecs)):

    #     # Compute the current bar radius
    #     curr_bar = hist[i]
    #     rad = len(curr_bar) / max_bar_num * delta_bar_radius

    #     # Convert ot polys for easy testing
    #     poly = Polygon2D.from_array(vec)
    #     chk_poly = Polygon2D.from_array([(c[0] * rad, c[1] * rad) for c in chk_vec])
    #     assert poly.is_equivalent(chk_poly, 1e-5)


def test_histogram_data_stacked():

    # Testing vals
    dir_vals = [0, 0, 0, 10, 10, 10, 85, 90, 90, 90, 95, 170, 285, 288]
    spd_vals = dir_vals

    # Make into fake data collections
    a_per = AnalysisPeriod(6, 21, 12, 6, 21, 13)
    dates = [DateTime(6, 21, i) for i in range(len(dir_vals))]
    spd_header = Header(Speed(), 'm/s', a_per)
    dir_header = Header(GenericType('Direction', 'deg'), 'deg', a_per)
    spd_data = HourlyDiscontinuousCollection(spd_header, spd_vals, dates)
    dir_data = HourlyDiscontinuousCollection(dir_header, dir_vals, dates)

    # Init simple dir set divided by 4
    w = WindRose(dir_data, spd_data, 4)
    w.legend_parameters.segment_count = 3

    # Bin values to divide into colors
    # 315-45:  [10, 10, 10];         2 intervals
    # 45-135:  [85, 90, 90, 90, 95]; 3 intervals, [85. , 88.3, 91.7, 95. ]
    # 135-225: [170];                1 intervals
    # 225-315: [285, 288];           2 intervals, [285. , 286.5, 288. ]

    # interval_num: [2, 3, 1, 2]
    chk_histstack = [
        [(10 + 10)/2., (10 + 10)/2.],
        [(85 + 88.3)/2., (88.3 + 91.7)/2., (91.7 + 95)/2.],
        [170.],
        [(285 + 286.5)/2., (286.5 + 288)/2.]
    ]

    # Testing
    histstack = WindRose._histogram_data_stacked(w.histogram_data, 3)
    for chkh, h in zip(chk_histstack, histstack):
        for c, _h in zip(chkh, h):
            assert abs(c - _h) <= 1e-1


def test_simple_windrose_mesh():
    # Testing vals
    dir_vals = [0, 0, 0, 10, 10, 10, 85, 90, 90, 90, 95, 170, 285, 288]
    spd_vals = dir_vals

    # Make into fake data collections
    a_per = AnalysisPeriod(6, 21, 12, 6, 21, 13)
    dates = [DateTime(6, 21, i) for i in range(len(dir_vals))]
    spd_header = Header(Speed(), 'm/s', a_per)
    dir_header = Header(GenericType('Direction', 'deg'), 'deg', a_per)
    spd_data = HourlyDiscontinuousCollection(spd_header, spd_vals, dates)
    dir_data = HourlyDiscontinuousCollection(dir_header, dir_vals, dates)

    # Init simple dir set divided by 4
    w = WindRose(dir_data, spd_data, 4)
    w.legend_parameters.segment_count = 3
    w.show_zeros = False
    w.show_stack = False
    mesh = w.colored_mesh
    assert isinstance(mesh, Mesh2D)

    # All true
    w = WindRose(dir_data, spd_data, 4)
    w.legend_parameters.segment_count = 10
    w.show_zeros = True
    w.show_stack = True
    mesh = w.colored_mesh
    assert isinstance(mesh, Mesh2D)

    # Init simple dir set divided by 8
    w = WindRose(dir_data, spd_data, 4)
    w.legend_parameters.segment_count = 3
    w.show_zeros = False
    w.show_stack = False
    mesh = w.colored_mesh
    assert isinstance(mesh, Mesh2D)


def test_windrose_mesh():
    # Plot windrose
    epw_path = os.path.join(os.getcwd(), 'tests/fixtures/epw/tokyo.epw')
    epw = EPW(epw_path)

    w = WindRose(epw.wind_direction, epw.wind_speed, 16)
    w.legend_parameters.segment_count = 3
    w.show_zeros = False
    w.show_stack = False
    mesh = w.colored_mesh

    # Simple test type
    assert isinstance(mesh, Mesh2D)


if __name__ == '__main__':
    test_linspace()
    test_histogram()
    test_histogram_circular()
    #test_bin_vectors()
    #test_xticks_radial()
    #test_radial_histogram()
    test_histogram_data_stacked()
    test_simple_windrose_mesh()
    test_windrose_mesh()