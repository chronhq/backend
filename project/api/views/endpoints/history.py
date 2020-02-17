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

from django.core.paginator import Paginator
from django.http import HttpResponse
from django.core.serializers import serialize
from api.models import SpacetimeVolume, TerritorialEntity


def all_history(request):
    return HttpResponse("OK")

def te_history(request, TE):

    page_number = request.GET.get('page')
    limit = request.GET.get('limit')

    history = SpacetimeVolume.history.filter(entity=TE)


    for x in history:
        print(x)


    if limit is not None:
        paginator = Paginator(history, limit)
    else:
        paginator = Paginator(history, 25)
    
    if page_number is not None:
        page = paginator.get_page(page_number)
    else:
        page = paginator.get_page("1")

    json = serialize('json', page)
    
    
    return HttpResponse(json, content_type='application/json')