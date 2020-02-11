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

from math import ceil
from datetime import datetime
import re
import requests
from jdcal import gcal2jd
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.contrib.gis.db.models.functions import Area, Transform
from api.models import TerritorialEntity, SpacetimeVolume
from itertools import tee

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

class Command(BaseCommand):

    
    """
    Populate cached datas with persons.
    """
    help = "Populate cached datas with persons."
    

    def handle(self, *args, **options):
        TEs = TerritorialEntity.objects.all()

        
        geom_count = 0
        for TE in TEs:

            STVs = SpacetimeVolume.objects.filter(entity=TE).annotate( lul=Transform("territory",3857)).order_by("start_date")

            print("FOR TE: {}".format(TE.label))

            for stv in STVs:
    
                print("FOR STV: {} Start date: {} End date:{}".format(stv.pk, stv.start_date, stv.end_date))
                for stv_overlap in SpacetimeVolume.objects.filter(entity=stv.entity).exclude(pk=stv.pk):
                    
#                    print(stv_overlap.pk)

                    # python manage.py clean_stvs
                    # Skip if we are inside another 
                    if (stv_overlap.end_date >= stv.end_date and stv_overlap.start_date < stv.start_date) or (stv_overlap.end_date > stv.end_date and stv_overlap.start_date <= stv.start_date) :
                        continue
                    # Union and delete if complete overlap 
                    elif stv_overlap.end_date == stv.end_date and stv_overlap.start_date == stv.start_date:
                        print("DELETING STV: {} Start date: {} End date:{}".format(stv_overlap.pk, stv_overlap.start_date, stv_overlap.end_date))

                        stv.territory = stv.territory.union(stv_overlap.territory)
                        stv_overlap.delete()
                        stv.save()
                    # If they are completely inside us: 1) Create new after overlap until original end date with original geom. 3) Make the original end date before overlap start date. 2) make overlap geom a union of two.
                    elif stv_overlap.start_date > stv.start_date and stv_overlap.end_date < stv.end_date:
                        

                        new_stv = SpacetimeVolume(start_date=stv_overlap.end_date + 1, end_date=stv.end_date, territory=stv.territory, entity=TE)
                        new_stv.save()
                        print("New stv id : {}".format(new_stv.pk))

                        stv.end_date = stv_overlap.start_date - 1
                        stv.save()

                        stv_overlap.territory = stv_overlap.territory.union(stv.territory)
                        stv_overlap.save()

                    # If their start is inside us: 1) Create new for before that 2) Union the overlap and set our start to their start 3) Set their start to our end 
                    elif stv_overlap.start_date >= stv.start_date and stv_overlap.start_date <= stv.end_date:
                        print("SETTING START DATE  STV: {} Start date: {} End date:{}".format(stv_overlap.pk, stv_overlap.start_date, stv_overlap.end_date))


                        new_stv = SpacetimeVolume(start_date=stv.start_date, end_date=stv_overlap.start_date-1, territory=stv.territory, entity=TE)
                        new_stv.save()
                        print("New stv id : {}".format(new_stv.pk))

                        
                        stv.territory = stv.territory.union(stv_overlap.territory)
                        stv.start_date = stv_overlap.start_date
                        stv.save()
                        
                        stv_overlap.start_date = stv.end_date + 1 
                        stv_overlap.save()
                        print("NEW START DATE  STV: {} Start date: {} End date:{}".format(stv_overlap.pk, stv_overlap.start_date, stv_overlap.end_date))

                    # If their end is inside us: 1) Create new after  2) Set their end to our start 3) Union the overlap and set our end to their end. 
                    elif stv_overlap.end_date <= stv.end_date and stv_overlap.end_date >= stv.start_date:
                        print("SETTING END DATE STV: {} Start date: {} End date:{}".format(stv_overlap.pk, stv_overlap.start_date, stv_overlap.end_date))

                        new_stv = SpacetimeVolume(start_date=stv_overlap.end_date+1, end_date=stv.end_date, territory=stv.territory, entity=TE)
                        new_stv.save()
                        print("New stv id : {}".format(new_stv.pk))

                        stv.territory = stv.territory.union(stv_overlap.territory)
                        stv.end_date = stv_overlap.end_date  
                        stv.save()
                        
                        stv_overlap.end_date = stv.start_date - 1
                        stv_overlap.save()
                        print("NEW END DATE STV: {} Start date: {} End date:{}".format(stv_overlap.pk, stv_overlap.start_date, stv_overlap.end_date))




            # for current_stv, next_stv in pairwise(STVs):

            #     if abs(current_stv.lul.area - next_stv.lul.area) < 10000000:
            #         print("Current TE: {} STV PK: {} START_DATE: {} END_DATE: {} Transform Area: {}".format(TE.label, current_stv.pk, current_stv.start_date, current_stv.end_date, current_stv.lul.area))

            #         print("Next TE: {} STV PK: {} START_DATE: {} END_DATE: {} Transform Area: {}".format(TE.label, next_stv.pk, next_stv.start_date, next_stv.end_date, next_stv.lul.area))

            #         next_stv.start_date = current_stv.start_date
            #         current_stv.delete()
            #         next_stv.references.append("https://www.placeholder.com")
            #         next_stv.save()

            #         geom_count += 1
