# -*- coding: utf-8 -*-
# This file is part of pygal
#
# A python svg graph plotting library
# Copyright © 2012-2013 Kozea
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pygal. If not, see <http://www.gnu.org/licenses/>.
"""
Histogram chart

"""

from __future__ import division
from pygal.graph.graph import Graph
from pygal.util import swap, ident, compute_scale, decorate, cached_property


class Histogram(Graph):
    """Histogram chart"""

    _dual = True
    _series_margin = 0

    @cached_property
    def _values(self):
        """Getter for secondary series values (flattened)"""
        return [val[0]
                for serie in self.series
                for val in serie.values
                if val[0] is not None]

    @cached_property
    def _secondary_values(self):
        """Getter for secondary series values (flattened)"""
        return [val[0]
                for serie in self.secondary_series
                for val in serie.values
                if val[0] is not None]

    @cached_property
    def xvals(self):
        return [val
                for serie in self.all_series
                for dval in serie.values
                for val in dval[1:3]
                if val is not None]

    @cached_property
    def yvals(self):
        return [val[0]
                for serie in self.series
                for val in serie.values
                if val[0] is not None]

    def _has_data(self):
        """Check if there is any data"""
        return sum(
            map(len, map(lambda s: s.safe_values, self.series))) != 0 and any((
            sum(map(abs, self.xvals)) != 0,
            sum(map(abs, self.yvals)) != 0))

    def _bar(self, parent, x0, x1, y, index, i, zero, secondary=False):
        x, y = self.view((x0, y))
        x1, _ = self.view((x1, y))
        width = x1 - x
        height = self.view.y(zero) - y
        series_margin = width * self._series_margin
        x += series_margin
        width -= 2 * series_margin

        r = self.rounded_bars * 1 if self.rounded_bars else 0
        self.svg.transposable_node(
            parent, 'rect',
            x=x, y=y, rx=r, ry=r, width=width, height=height,
            class_='rect reactive tooltip-trigger')
        transpose = swap if self.horizontal else ident
        return transpose((x + width / 2, y + height / 2))

    def bar(self, serie_node, serie, index, rescale=False):
        """Draw a bar graph for a serie"""
        bars = self.svg.node(serie_node['plot'], class_="histbars")
        points = serie.points

        for i, (y, x0, x1) in enumerate(points):
            if None in (x0, x1, y) or (self.logarithmic and y <= 0):
                continue
            metadata = serie.metadata.get(i)

            bar = decorate(
                self.svg,
                self.svg.node(bars, class_='histbar'),
                metadata)
            val = self._format(serie.values[i][0])

            x_center, y_center = self._bar(
                bar, x0, x1, y, index, i, self.zero, secondary=rescale)
            self._tooltip_data(
                bar, val, x_center, y_center, classes="centered")
            self._static_value(serie_node, val, x_center, y_center)

    def _compute(self):
        if self.xvals:
            xmin = min(self.xvals)
            xmax = max(self.xvals)
            xrng = (xmax - xmin)
        else:
            xrng = None

        if self.yvals:
            ymin = min(min(self.yvals), self.zero)
            ymax = max(max(self.yvals), self.zero)
            yrng = (ymax - ymin)
        else:
            yrng = None

        for serie in self.all_series:
            serie.points = serie.values

        if xrng:
            self._box.xmin, self._box.xmax = xmin, xmax
        if yrng:
            self._box.ymin, self._box.ymax = ymin, ymax

        x_pos = compute_scale(
            self._box.xmin, self._box.xmax, self.logarithmic, self.order_min)
        y_pos = compute_scale(
            self._box.ymin, self._box.ymax, self.logarithmic, self.order_min)

        self._x_labels = list(zip(map(self._format, x_pos), x_pos))
        self._y_labels = list(zip(map(self._format, y_pos), y_pos))

    def _plot(self):
        for index, serie in enumerate(self.series):
            self.bar(self._serie(index), serie, index)
        for index, serie in enumerate(self.secondary_series, len(self.series)):
            self.bar(self._serie(index), serie, index, True)
