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

from django.db.utils import IntegrityError
from django.test import TestCase

from .factories import PoliticalEntityFactory
from .models import DirectPoliticalRelation, IndirectPoliticalRelation, PoliticalEntity

# Create your tests here.
class ModelTest(TestCase):
    """
    Tests model constraints directly
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create basic model instances
        """

        cls.new_nation = PoliticalEntityFactory(wikidata_id=1, color=1, admin_level=1)
        cls.new_child_nation = PoliticalEntityFactory(
            wikidata_id=2, color=1, admin_level=1
        )
        cls.new_child_nation2 = PoliticalEntityFactory(
            wikidata_id=3, color=1, admin_level=1
        )
        cls.new_child_nation3 = PoliticalEntityFactory(
            wikidata_id=4, color=1, admin_level=1
        )
        cls.new_child_nation4 = PoliticalEntityFactory(
            wikidata_id=5, color=1, admin_level=1
        )

    def test_model_can_create_directpoliticalrelation(self):
        """
        Test if DPR can be created
        """

        dpr = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01", end_date="0005-01-01", entity=self.new_nation
        )
        # we need to do a full refresh to get the value of the path
        dpr.refresh_from_db()

        self.assertTrue(dpr.id > 0)
        self.assertEqual(dpr.entity, self.new_nation)
        self.assertTrue(dpr.path)

    def test_model_can_create_indirectpoliticalrelation(self):
        """
        Test if IPR can be created
        """

        ipr = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0001-01-01",
            entity=self.new_nation,
            relation_type=1,
        )
        # we need to do a full refresh to get the value of the path
        ipr.refresh_from_db()

        self.assertTrue(ipr.id > 0)
        self.assertEqual(ipr.entity, self.new_nation)
        self.assertTrue(ipr.path)

    def test_model_directpoliticalrelation_direct_children(self):
        """
        Test if DPR child hierarchy is functional
        """

        dpr_parent = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01", end_date="0005-01-01", entity=self.new_nation
        )
        dpr_parent.refresh_from_db()

        dpr_child1 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=dpr_parent,
        )
        dpr_child2 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=dpr_parent,
        )
        DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=dpr_child2,
        )
        dpr_child3 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=dpr_parent,
        )

        self.assertEqual(
            list(dpr_parent.children.order_by("entity")),
            [dpr_child1, dpr_child2, dpr_child3],
        )

    def test_model_indirectpoliticalrelation_direct_children(self):
        """
        Test if IPR child hierarchy is functional
        """

        ipr_parent = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_nation,
            relation_type=1,
        )
        ipr_parent.refresh_from_db()

        ipr_child1 = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child2 = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=ipr_parent,
            relation_type=1,
        )
        IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=ipr_child2,
            relation_type=1,
        )
        ipr_child3 = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=ipr_parent,
            relation_type=1,
        )

        self.assertEqual(
            list(ipr_parent.children.order_by("entity")),
            [ipr_child1, ipr_child2, ipr_child3],
        )

    def test_model_directpoliticalrelation_descendants(self):
        """
        Test if DPR descendant lookup is functional
        """

        dpr_parent = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01", end_date="0005-01-01", entity=self.new_nation
        )
        dpr_parent.refresh_from_db()

        DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=dpr_parent,
        )
        dpr_child2 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=dpr_parent,
        )
        dpr_child2_child = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=dpr_child2,
        )
        DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=dpr_child2_child,
        )

        self.assertEqual(
            list(
                DirectPoliticalRelation.objects.filter(
                    path__descendant_or_equal=dpr_parent.path
                )
                .values_list("path", flat=True)
                .order_by("path")
            ),
            ["1", "1.2", "1.3", "1.3.4", "1.3.4.5"],
        )

    def test_model_indirectpoliticalrelation_descendants(self):
        """
        Test if IPR descendant lookup is functional
        """

        ipr_parent = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_nation,
            relation_type=1,
        )
        ipr_parent.refresh_from_db()

        IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child2 = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child2_child = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=ipr_child2,
            relation_type=1,
        )
        IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=ipr_child2_child,
            relation_type=1,
        )

        self.assertEqual(
            list(
                IndirectPoliticalRelation.objects.filter(
                    path__descendant_or_equal=ipr_parent.path
                )
                .values_list("path", flat=True)
                .order_by("path")
            ),
            ["1", "1.2", "1.3", "1.3.4", "1.3.4.5"],
        )

    def test_model_directpoliticalrelation_ancestors(self):
        """
        Test if DPR ancestor lookup is functional
        """

        dpr_parent = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01", end_date="0005-01-01", entity=self.new_nation
        )
        dpr_parent.refresh_from_db()

        DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=dpr_parent,
        )
        dpr_child2 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=dpr_parent,
        )
        dpr_child2_child = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=dpr_child2,
        )
        dpr_child2_child_child = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=dpr_child2_child,
        )
        dpr_child2_child_child.refresh_from_db()

        self.assertEqual(
            list(
                DirectPoliticalRelation.objects.filter(
                    path__ancestor_or_equal=dpr_child2_child_child.path
                )
                .values_list("path", flat=True)
                .order_by("path")
            ),
            ["1", "1.3", "1.3.4", "1.3.4.5"],
        )

    def test_model_indirectpoliticalrelation_ancestors(self):
        """
        Test if IPR ancestor lookup is functional
        """

        ipr_parent = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_nation,
            relation_type=1,
        )
        ipr_parent.refresh_from_db()

        IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child2 = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child2_child = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=ipr_child2,
            relation_type=1,
        )
        ipr_child2_child_child = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=ipr_child2_child,
            relation_type=1,
        )
        ipr_child2_child_child.refresh_from_db()

        self.assertEqual(
            list(
                IndirectPoliticalRelation.objects.filter(
                    path__ancestor_or_equal=ipr_child2_child_child.path
                )
                .values_list("path", flat=True)
                .order_by("path")
            ),
            ["1", "1.3", "1.3.4", "1.3.4.5"],
        )

    def test_model_directpoliticalrelation_update_entity(self):
        """
        Update the entity field, it should update its path as well as
        the path of all of its descendants
        """

        dpr_parent = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01", end_date="0005-01-01", entity=self.new_nation
        )
        dpr_parent.refresh_from_db()

        DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=dpr_parent,
        )
        dpr_child2 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=dpr_parent,
        )
        dpr_child2_child = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=dpr_child2,
        )
        DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=dpr_child2_child,
        )

        dpr_child2.entity = PoliticalEntity.objects.create(
            wikidata_id=6, admin_level=1, color=1
        )
        dpr_child2.save()

        self.assertEqual(
            list(
                DirectPoliticalRelation.objects.filter(
                    path__descendant_or_equal=dpr_parent.path
                )
                .values_list("path", flat=True)
                .order_by("path")
            ),
            ["1", "1.2", "1.6", "1.6.4", "1.6.4.5"],
        )

    def test_model_indirectpoliticalrelation_update_entity(self):
        """
        Update the entity field, it should update its path as well as
        the path of all of its descendants
        """

        ipr_parent = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_nation,
            relation_type=1,
        )
        ipr_parent.refresh_from_db()

        IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child2 = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child2_child = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=ipr_child2,
            relation_type=1,
        )
        IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=ipr_child2_child,
            relation_type=1,
        )

        ipr_child2.entity = PoliticalEntity.objects.create(
            wikidata_id=6, admin_level=1, color=1
        )
        ipr_child2.save()

        self.assertEqual(
            list(
                IndirectPoliticalRelation.objects.filter(
                    path__descendant_or_equal=ipr_parent.path
                )
                .values_list("path", flat=True)
                .order_by("path")
            ),
            ["1", "1.2", "1.6", "1.6.4", "1.6.4.5"],
        )

    def test_model_directpoliticalrelation_update_parent(self):
        """
        update a parent polent, it should update its path as well as
        the path of all of its descendants
        """

        dpr_parent = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01", end_date="0005-01-01", entity=self.new_nation
        )
        dpr_parent.refresh_from_db()

        dpr_child1 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=dpr_parent,
        )
        dpr_child2 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=dpr_parent,
        )
        dpr_child2_child = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=dpr_child2,
        )
        DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=dpr_child2_child,
        )

        dpr_child2_child.parent = dpr_child1
        dpr_child2_child.save()

        self.assertEqual(
            list(
                DirectPoliticalRelation.objects.filter(
                    path__descendant_or_equal=dpr_parent.path
                )
                .values_list("path", flat=True)
                .order_by("path")
            ),
            ["1", "1.2", "1.2.4", "1.2.4.5", "1.3"],
        )

    def test_model_indirectpoliticalrelation_update_parent(self):
        """
        update a parent polent, it should update its path as well as
        the path of all of its descendants
        """

        ipr_parent = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_nation,
            relation_type=1,
        )
        ipr_parent.refresh_from_db()

        ipr_child1 = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child2 = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation2,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child2_child = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=ipr_child2,
            relation_type=1,
        )
        IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation4,
            parent=ipr_child2_child,
            relation_type=1,
        )

        ipr_child2_child.parent = ipr_child1
        ipr_child2_child.save()

        self.assertEqual(
            list(
                IndirectPoliticalRelation.objects.filter(
                    path__descendant_or_equal=ipr_parent.path
                )
                .values_list("path", flat=True)
                .order_by("path")
            ),
            ["1", "1.2", "1.2.4", "1.2.4.5", "1.3"],
        )

    def test_model_simple_recursion(self):
        """
        Ensure PolRels cannot be their own parent
        """

        ipr = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_nation,
            relation_type=1,
        )
        dpr = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01", end_date="0005-01-01", entity=self.new_nation
        )

        ipr.parent = ipr
        dpr.parent = dpr

        with self.assertRaises(IntegrityError):
            ipr.save()
            dpr.save()

    def test_model_nested_recursion(self):
        """
        Ensure a parent cannot be the descendant of one of its children
        """

        ipr_parent = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_nation,
            relation_type=1,
        )
        ipr_child = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=ipr_parent,
            relation_type=1,
        )
        ipr_child_child = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=ipr_child,
            relation_type=1,
        )

        dpr_parent = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01", end_date="0005-01-01", entity=self.new_nation
        )
        dpr_child = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=dpr_parent,
        )
        dpr_child_child = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation3,
            parent=dpr_child,
        )

        ipr_parent.parent = ipr_child_child
        dpr_parent.parent = dpr_child_child

        with self.assertRaises(IntegrityError):
            ipr_parent.save()
            dpr_parent.save()

    def test_model_directpoliticalrelation_direct_children(self):
        """
        Test if a child can change parent over time
        """

        dpr_parent_1 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01", end_date="0005-01-01", entity=self.new_nation
        )
        dpr_parent_2 = DirectPoliticalRelation.objects.create(
            start_date="0006-01-01", end_date="0007-01-01", entity=self.new_nation
        )
        dpr_parent.refresh_from_db()

        dpr_child1 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=dpr_parent_1,
        )
        dpr_child2 = DirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=dpr_parent_2,
        )

        self.assertTrue(1)

    def test_model_nested_recursion(self):
        """
        A polent can be parent during one period, and child in the following
        period
        """

        ipr_parent_before = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_nation,
            relation_type=1,
        )
        ipr_child_before = IndirectPoliticalRelation.objects.create(
            start_date="0001-01-01",
            end_date="0005-01-01",
            entity=self.new_child_nation,
            parent=ipr_parent_before,
            relation_type=1,
        )

        ipr_parent_after = IndirectPoliticalRelation.objects.create(
            start_date="0006-01-01",
            end_date="0007-01-01",
            entity=self.new_child_nation,
            relation_type=1,
        )
        ipr_child_after = IndirectPoliticalRelation.objects.create(
            start_date="0006-01-01",
            end_date="0007-01-01",
            entity=self.new_nation,
            parent=ipr_parent_after,
            relation_type=1,
        )

        self.assertTrue(1)
