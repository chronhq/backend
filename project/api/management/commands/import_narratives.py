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
import re
from math import ceil
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from jdcal import gcal2jd
import openpyxl
from api.models import Narration, Narrative, MapSettings, CachedData


class Command(BaseCommand):
    """
    For importing narratives from excel files. Not generalized.
    """

    help = "For importing narratives from excel files. Not generalized."

    def handle(self, *args, **options):
        """Import narrations from xlsx sheet.
        The columns are:
        date	date_label	title	description	x	y	persons	battles	treaties
        """

    excel_document = openpyxl.load_workbook("data.xlsx")

    for sheet in excel_document:
        all_rows = sheet.rows
        settings = MapSettings(zoom_min=2.0, zoom_max=7.5)
        settings.save()
        narrative = Narrative.objects.filter(title=sheet.title)
        skipped_sheet = iter(sheet)
        next(skipped_sheet)
        for row in skipped_sheet:
            dates = str(row[0].value).split("-")
            if dates[0] == "" or int(dates[0]) < 1783:
                continue

            if len(dates) == 1:
                date = ceil(sum(gcal2jd(int(dates[0]), 1, 1))) + 0.0
            elif len(dates) == 2:
                date = ceil(sum(gcal2jd(int(dates[0]), dates[1], 1))) + 0.0
            else:
                print(row[0].value)
                date = ceil(sum(gcal2jd(int(dates[0]), dates[1], dates[2]))) + 0.0

            point = Point(float(row[4].value), float(row[5].value))

            n = Narration(
                narrative=narrative[0],
                settings=settings,
                map_datetime=date,
                date_label=row[1].value,
                title=row[2].value,
                description=row[3].value,
            )
            n.save()
            if row[7].value is not None:
                attached_battles_list = re.sub("[A-z]", "", row[7].value).split(",")

                print(attached_battles_list)
                cached_datas = CachedData.objects.filter(
                    wikidata_id__in=attached_battles_list
                )
                for data in cached_datas:
                    n.attached_events.add(data)

            if row[8].value is not None:
                attached_treaties_list = re.sub("[A-z]", "", row[8].value).split(",")

                print(attached_treaties_list)
                cached_datas = CachedData.objects.filter(
                    wikidata_id__in=attached_treaties_list
                )
                for data in cached_datas:
                    n.attached_events.add(data)
