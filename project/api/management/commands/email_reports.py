"""
Chron.
Copyright (C) 2018 Alisa Belyaeva, Ata Ali Kilicli, Amaury Martiny,
Daniil Mordasov, Liam O'Flynn, Mikhail Orlov.

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

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from api.models import HistoricalTerritorialEntity, HistoricalSpacetimeVolume
from datetime import datetime, timedelta



# TODO
user = "Test User"
overlaps_count = 0


email_text = f"""
Hi, {user}!

Here is our daily report.

Thanks to our community we have following updates:
  - {len(te_changes)} modified entities
  - {len(stv_changes)} changed territories
  - {overlaps_count} changed by overlaps

Territories:
  - ✏️ Created {XX}
  - 🗑 Deleted {XX}
  - ✂️ Modified {XX}

Overlaps:
  {te.wikidata_id} {te.name}
    {stv.start_date} - {stv.end_date}

Entities:
  {te.wikidata_id} {te.name}
    -? {te.hist.start_date} ⟶ {te.new.start_date}
    -? {te.hist.end_date} ⟶ {te.new.end_date}
    -? {te.hist.color} ⟶ {te.new.color}
    -? Territories C {XX} / D {XX} / M {XX}

Truly yours,

Chronmaps Team!

--
To unsubscribe visit https://chronmaps.com/admin
"""


class Command(BaseCommand):
    """
    Create daily report emails.
    """

    help = "Create daily report emails."

    def handle(self, *args, **options):

        te_changes = HistoricalTerritorialEntity.objects.filter(history_date__gt=datetime.now() - timedelta(days=20))
        stv_changes = HistoricalSpacetimeVolume.objects.filter(history_date__gt=datetime.now() - timedelta(days=20))

        stv_created = 0
        stv_deleted = 0
        stv_modified = 0
        for stv in stv_changes:
            if stv.history_type == "+":
              stv_created += 1
            elif stv.history_type == "-":
              stv_deleted += 1
            else:
              stv_modified += 1
