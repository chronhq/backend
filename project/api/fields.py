"""
Chron.
Copyright (C) 2018 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
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

from django.contrib.gis.db import models
from jdcal import gcal2jd

class JDNField(models.DateField):
  description = "A field to save JDN values as postgres `date` types"

  def get_db_prep_value(self, value, *args, **kwargs):
    if value is None:
      return None
    jd = gcal2jd(*value)[0] + gcal2jd(*value)[1] + 0.5
    return f'J{jd}'

  def to_python(self, value):
    if value is None:
      return None
    return 

  def from_db_value(self, value, expression, connection, context):
    return self.to_python(value)

