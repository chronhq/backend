from django.core.management.base import BaseCommand, CommandError
from api.models import Narration, Narrative, MapSettings, CachedData
from jdcal import gcal2jd
from math import ceil
import openpyxl
from django.contrib.gis.geos import Point
import re

class Command(BaseCommand):
    help = 'For importing narratives from excel files. Not generalized.'

    def parseQID(id_string):
        id_list = id_string.split(",")
        parsed_list = map(lambda each:each[1:], id_list)
        return list(parsed_list)

    def handle(self, *args, **options):
        """ Import narrations from xlsx sheet. """

    excel_document = openpyxl.load_workbook('data.xlsx')
    
    for sheet in excel_document:
        all_rows = sheet.rows
        settings = MapSettings(zoom_min = 2.0,zoom_max = 7.5)
        settings.save()
        narrative = Narrative.objects.filter(title=sheet.title)
        skipped_sheet = iter(sheet)
        next(skipped_sheet)
        for row in skipped_sheet:
            dates = str(row[0].value).split("-")
            if dates[0] == "" or int(dates[0]) < 1783:
                    continue
            # if len(dates) == 1:
                
            date = ceil(sum(gcal2jd(int(dates[0]), 1, 1))) + 0.0
            # elif len(dates) == 2:
            #     date = ceil(sum(gcal2jd(int(dates[0]), dates[1], 1))) + 0.0
            # else:
            #     date = ceil(sum(gcal2jd(int(dates[0]), dates[1], dates[2]))) + 0.0
            # if sheet.title == "Russia":
            #     x_coord_split = row[2].value.split("°")
            #     y_coord_split = row[3].value.split("°")
            #     point = Point(dms2dd(x_coord_split[0],x_coord_split[1],0,"S"), dms2dd(y_coord_split[0],y_coord_split[1],0,"W"))
            # else:
            #     point = Point(float(row[2].value), float(row[3].value))


            n = Narration(
                narrative=narrative[0],
                title=row[1].value,
                date_label=row[0].value,
                map_datetime=date,
                settings=settings,
                description=row[2].value
            )
            n.save()
            attached_events_list = re.sub('[A-z]', '', row[4].value + ',' + row[5].value).split(',')
            
            print(attached_events_list)
            cached_datas = CachedData.objects.filter(wikidata_id__in=attached_events_list)
            for data in cached_datas:
                n.attached_events.add(data)



