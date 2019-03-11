psql='psql -U postgres -t -c'

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
DATA="${DIR}/../data"
mkdir -p $DATA
FCFILE="${DATA}/stv.json"

TABLE='api_spacetimevolume'

echo $DIR

function feature() {
  local target="$1"
  query="
    SELECT jsonb_build_object(
      'type',       'Feature',
      'id',         id,
      'geometry',   ST_AsGeoJSON(geom)::json,
      'properties', to_jsonb(row) - 'geom'
    ) FROM (
      SELECT api_spacetimevolume.*, geom.geom,
        api_territorialentity.wikidata_id, api_territorialentity.color,
        api_territorialentity.admin_level
        FROM api_spacetimevolume
        JOIN (
            SELECT ST_COLLECT(geom) AS geom, spacetimevolume_id as id FROM api_spacetimevolume_territory
            JOIN api_atomicpolygon ON atomicpolygon_id = api_atomicpolygon.id
            GROUP BY (spacetimevolume_id)
        ) as geom ON geom.id = api_spacetimevolume.id
        JOIN api_territorialentity ON api_spacetimevolume.entity_id = api_territorialentity.id
        WHERE api_spacetimevolume.id = $target
      ) row;
  "
}


SEPARATOR=""

echo '{"type": "FeatureCollection","features": [' > $FCFILE
for id in `$psql "select id from $TABLE"`; do
  # echo This is id: $id;
  feature $id
  $psql "$query" >> $FCFILE
  echo -n $SEPARATOR >> $FCFILE
  SEPARATOR=","
done
echo ']}' >> $FCFILE
