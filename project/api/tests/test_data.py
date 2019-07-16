from api.factories import TerritorialEntityFactory
from jdcal import gcal2jd
from math import ceil

def set_up_data(cls):
  """
  Create basic model instances
  """
  # Constants
  cls.JD_0001 = ceil(sum(gcal2jd(1, 1, 1))) + 0.0
  cls.JD_0002 = ceil(sum(gcal2jd(2, 1, 1))) + 0.0
  cls.JD_0003 = ceil(sum(gcal2jd(3, 1, 1))) + 0.0
  cls.JD_0004 = ceil(sum(gcal2jd(4, 1, 1))) + 0.0
  cls.JD_0005 = ceil(sum(gcal2jd(5, 1, 1))) + 0.0

  # TerritorialEntities
  cls.european_union = TerritorialEntityFactory(
      wikidata_id=10,
      label="European Union",
      color=1,
      admin_level=1,
      inception_date=0,
      dissolution_date=1,
  )
  cls.nato = TerritorialEntityFactory(
      wikidata_id=11,
      label="NATO",
      color=1,
      admin_level=1,
      inception_date=0,
      dissolution_date=1,
  )

  cls.germany = TerritorialEntityFactory(
      wikidata_id=20,
      label="Germany",
      color=1,
      admin_level=2,
      inception_date=0,
      dissolution_date=1,
  )
  cls.france = TerritorialEntityFactory(
      wikidata_id=21,
      label="France",
      color=1,
      admin_level=2,
      inception_date=0,
      dissolution_date=1,
  )
  cls.spain = TerritorialEntityFactory(
      wikidata_id=22,
      label="Spain",
      color=1,
      admin_level=2,
      inception_date=0,
      dissolution_date=1,
  )
  cls.italy = TerritorialEntityFactory(
      wikidata_id=23,
      label="Italy",
      color=1,
      admin_level=2,
      inception_date=0,
      dissolution_date=1,
  )
  cls.british_empire = TerritorialEntityFactory(
      wikidata_id=24,
      label="British Empire",
      color=1,
      admin_level=2,
      inception_date=0,
      dissolution_date=1,
  )
  cls.british_hk = TerritorialEntityFactory(
      wikidata_id=25,
      label="British HK",
      color=1,
      admin_level=2,
      inception_date=0,
      dissolution_date=1,
  )

  cls.alsace = TerritorialEntityFactory(
      wikidata_id=30,
      label="Alsace",
      color=1,
      admin_level=3,
      inception_date=0,
      dissolution_date=1,
  )
  cls.lorraine = TerritorialEntityFactory(
      wikidata_id=31,
      label="Lorraine",
      color=1,
      admin_level=3,
      inception_date=0,
      dissolution_date=1,
  )