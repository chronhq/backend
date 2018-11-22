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

from django.db import models


class LtreeField(models.TextField):
    """
    Field for the Postgres ltree data type
        https://www.postgresql.org/docs/current/ltree.html
    """

    description = "ltree"

    def __init__(self, *args, **kwargs):
        kwargs["editable"] = False
        kwargs["null"] = True
        kwargs["default"] = None
        super(LtreeField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return "ltree"


class AncestorOrEqual(models.Lookup):
    """
    Lookup for ancestors of the tree
    """

    lookup_name = "ancestor_or_equal"

    def as_sql(self, qn, connection):  # pylint: disable=W0221
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "%s @> %s" % (lhs, rhs), params


class DescendantOrEqual(models.Lookup):
    """
    Lookup for descendants of the tree
    """

    lookup_name = "descendant_or_equal"

    def as_sql(self, qn, connection):  # pylint: disable=W0221
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "%s <@ %s" % (lhs, rhs), params


LtreeField.register_lookup(AncestorOrEqual)
LtreeField.register_lookup(DescendantOrEqual)
