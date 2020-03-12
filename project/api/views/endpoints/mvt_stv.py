# pylint: disable=C0302

"""
Chron.
Copyright (C) 2020 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
Daniil Mordasov, Liam O’Flynn, Mikhail Orlov.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from django.http import HttpResponse
from api.models import MVTLayers


def mvt_stv(request, zoom, x_coor, y_coor):
    """
    Custom view to serve Mapbox Vector Tiles for Political Borders.
    """

    tiles = MVTLayers.objects.filter(
        layer="stv", zoom=zoom, x_coor=x_coor, y_coor=y_coor
    )
    if len(tiles) == 0:
        return HttpResponse(status=204)
    return HttpResponse(bytes(tiles[0].tile), content_type="application/x-protobuf")
