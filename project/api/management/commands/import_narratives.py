from django.core.management.base import BaseCommand, CommandError
from api.models import Narration, Narrative, MapSettings
from jdcal import gcal2jd
from math import ceil
import openpyxl
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    help = 'For importing narratives from excel files. Not generalized.'



    def dms2dd(degrees, minutes, seconds, direction):
        dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
        if direction == 'E' or direction == 'N':
            dd *= -1
        return dd


    def handle(self, *args, **options):
        """ Do your work here """





    excel_document = openpyxl.load_workbook('geo_events1.xlsx')
    
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
            if len(dates) == 1:
                
                date = ceil(sum(gcal2jd(int(dates[0]), 1, 1))) + 0.0
            elif len(dates) == 2:
                date = ceil(sum(gcal2jd(int(dates[0]), dates[1], 1))) + 0.0
            else:
                date = ceil(sum(gcal2jd(int(dates[0]), dates[1], dates[2]))) + 0.0
            print(row)
            if sheet.title == "Russia":
                x_coord_split = row[2].value.split("°")
                y_coord_split = row[3].value.split("°")
                point = Point(dms2dd(x_coord_split[0],x_coord_split[1],0,"S"), dms2dd(y_coord_split[0],y_coord_split[1],0,"W"))
            else:
                point = Point(float(row[2].value), float(row[3].value))


            n = Narration(
                narrative=narrative[0],
                title=row[4].value,
                date_label=row[0].value,
                map_datetime=date,
                settings=settings,
                location=point
            )
            n.save()



