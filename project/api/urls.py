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

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

ROUTER = DefaultRouter()
ROUTER.register(r"territorial-entities", views.TerritorialEntityViewSet)
ROUTER.register(r"poltical-relations", views.PoliticalRelationViewSet)
ROUTER.register(r"cached-data", views.CachedDataViewSet)
ROUTER.register(r"atomic-polygons", views.AtomicPolygonViewSet)
ROUTER.register(r"spacetime-volumes", views.SpacetimeVolumeViewSet)
ROUTER.register(r"narratives", views.NarrativeViewSet)
ROUTER.register(r"map-settings", views.MapSettingsViewSet)
ROUTER.register(r"narrations", views.NarrationViewSet)

urlpatterns = [path("", include(ROUTER.urls))]
