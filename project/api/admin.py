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

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    TerritorialEntity,
    PoliticalRelation,
    SpacetimeVolume,
    CachedData,
    Narration,
    Narrative,
    MapSettings,
    City,
    Profile,
    NarrativeVote,
    Symbol,
    SymbolFeature,
)

# Register your models here.
admin.site.register(TerritorialEntity, SimpleHistoryAdmin)
admin.site.register(PoliticalRelation, SimpleHistoryAdmin)
admin.site.register(SpacetimeVolume, SimpleHistoryAdmin)
admin.site.register(CachedData, SimpleHistoryAdmin)
admin.site.register(Narration, SimpleHistoryAdmin)
admin.site.register(Narrative, SimpleHistoryAdmin)
admin.site.register(MapSettings, SimpleHistoryAdmin)
admin.site.register(City, SimpleHistoryAdmin)
admin.site.register(Profile, SimpleHistoryAdmin)
admin.site.register(NarrativeVote, SimpleHistoryAdmin)
admin.site.register(Symbol, SimpleHistoryAdmin)
admin.site.register(SymbolFeature, SimpleHistoryAdmin)
