from django.core.management.base import BaseCommand, CommandError
from api.models import TerritorialEntity,SpacetimeVolume

class Command(BaseCommand):
    help = 'For syncing TR inception/dissolution dates with STVs we have.'


    def handle(self, *args, **options):

        statistics = {"processed":0, "changed":0}
        territory_set = TerritorialEntity.objects.all()

        
        for territory in territory_set:
            
            statistics["processed"] += 1
            start = SpacetimeVolume.objects.filter(entity=territory).order_by("start_date")
            end = SpacetimeVolume.objects.filter(entity=territory).order_by("-end_date")
            if territory.inception_date != start[0].start_date or territory.dissolution_date != end[0].end_date:
                print("changed")
                statistics["changed"] += 1
                territory.inception_date = start[0].start_date
                territory.dissolution_date = end[0].end_date
                territory.save()

        print("Processed {} TEs, changed {}".format(statistics["processed"], statistics["changed"]))
