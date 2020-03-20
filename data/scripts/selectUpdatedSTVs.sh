PREV=$1
[ "${PREV}" == "" ] && PREV=0;

psql="psql -d \"host=db user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}\" -t -c"

query="
SELECT string_agg(DISTINCT id::text, ' ') FROM (
	SELECT api_historicalspacetimevolume.id, api_historicalspacetimevolume.history_date 
	FROM api_historicalspacetimevolume
	UNION 
	SELECT api_spacetimevolume.id, api_historicalterritorialentity.history_date
	FROM api_spacetimevolume
	JOIN api_historicalterritorialentity
	ON api_historicalterritorialentity.id = entity_id
	JOIN api_territorialentity
	ON api_territorialentity.id = entity_id
	WHERE NOT (
		api_historicalterritorialentity.color_id=api_territorialentity.color_id
		AND api_historicalterritorialentity.admin_level=api_territorialentity.admin_level
	)
) AS foo
WHERE history_date >= to_timestamp(${PREV})
"

updates=$(eval $psql "\"$query\"" | sed 's/^\s//' | grep -v -e '^$')

[ "${updates}" != "" ] && echo $updates;
exit 0;
