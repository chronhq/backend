-- used when we access the path directly
CREATE INDEX api_DirectPoliticalRelation_path
          ON api_DirectPoliticalRelation
       USING btree(path);

CREATE INDEX api_IndirectPoliticalRelation_path
          ON api_IndirectPoliticalRelation
       USING btree(path);

-- used when we get descendants or ancestors
CREATE INDEX api_DirectPoliticalRelation_path_gist
          ON api_DirectPoliticalRelation
       USING GIST(path);

CREATE INDEX api_IndirectPoliticalRelation_path_gist
          ON api_IndirectPoliticalRelation
       USING GIST(path);
