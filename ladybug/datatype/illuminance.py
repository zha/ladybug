# coding=utf-8
"""Illuminance data type."""
from __future__ import division

from .base import DataTypeBase


class Illuminance(DataTypeBase):
    """Illuminance"""
    _units = ('lux', 'fc')
    _si_units = ('lux')
    _ip_units = ('fc')
    _min = 0
    _abbreviation = 'Ev'
    _point_in_time = False
    _min_epw = 0
    _missing_epw = 999999  # note will be missing if >= 999900

    def _lux_to_fc(self, value):
        return value / 10.7639

    def _fc_to_lux(self, value):
        return value * 10.7639

    def to_unit(self, values, unit, from_unit):
        """Return values in a given unit given the input from_unit."""
        return self._to_unit_base('lux', values, unit, from_unit)

    def to_ip(self, values, from_unit):
        """Return values in fc given the input from_unit."""
        if from_unit == 'fc':
            return values, from_unit
        else:
            return self.to_unit(values, 'fc', from_unit), 'fc'

    def to_si(self, values, from_unit):
        """Return values in lux given the input from_unit."""
        if from_unit == 'lux':
            return values, from_unit
        else:
            return self.to_unit(values, 'lux', from_unit), 'lux'

    @property
    def isIlluminance(self):
        """Return True."""
        return True


class GlobalHorizontalIlluminance(Illuminance):
    _abbreviation = 'GHI'


class DirectNormalIlluminance(Illuminance):
    _abbreviation = 'DNI'


class DiffuseHorizontalIlluminance(Illuminance):
    _abbreviation = 'DHI'
