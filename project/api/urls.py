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
ROUTER.register(r"political-relations", views.PoliticalRelationViewSet)
ROUTER.register(r"cached-data", views.CachedDataViewSet)
ROUTER.register(r"cities", views.CityViewSet)
ROUTER.register(r"spacetime-volumes", views.SpacetimeVolumeViewSet)
ROUTER.register(r"narratives", views.NarrativeViewSet)
ROUTER.register(r"map-settings", views.MapSettingsViewSet)
ROUTER.register(r"narrations", views.NarrationViewSet)
ROUTER.register(r"narrative-votes", views.NarrativeVoteViewSet)
ROUTER.register(r"profiles", views.ProfileViewSet)

urlpatterns = [
    path(
        "mvt/cached-data/<int:zoom>/<int:x_cor>/<int:y_cor>",
        views.mvt_cacheddata,
        name="mvt-cacheddata",
    ),
    path(
        "mvt/cities/<int:zoom>/<int:x_cor>/<int:y_cor>",
        views.mvt_cities,
        name="mvt-cities",
    ),
    path(
        "mvt/narratives/<int:narrative>/<int:zoom>/<int:x_cor>/<int:y_cor>",
        views.mvt_narration_events,
        name="mvt-narrationevents",
    ),
    path("mvt/stv/<int:zoom>/<int:x_cor>/<int:y_cor>", views.mvt_stv, name="mvt-stv"),
    path(
        "mvt/visual-center/<int:zoom>/<int:x_cor>/<int:y_cor>",
        views.mvt_visual_center,
        name="mvt-visualcenter",
    ),
    path("", include(ROUTER.urls)),
]
