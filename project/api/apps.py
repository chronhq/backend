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

from django.apps import AppConfig
from simple_history.signals import pre_create_historical_record


def add_invoice_to_historical_balance(sender, **kwargs):  # pylint: disable=W0613
    """
    Save group to historical record
    """
    instance = kwargs["instance"]
    if getattr(instance, "group", None):
        kwargs["history_instance"].group = instance.group
        del instance.group


class ApiConfig(AppConfig):
    """
    AppConfig for the `api` app
    """

    name = "api"

    def ready(self):
        from .models import HistoricalSpacetimeVolume  # pylint: disable=C0415

        pre_create_historical_record.connect(
            add_invoice_to_historical_balance, sender=HistoricalSpacetimeVolume
        )
