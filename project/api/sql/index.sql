-- used when we access the path directly
CREATE INDEX api_DirectPoliticalRelation_path
          ON api_DirectPoliticalRelation
       USING btree(path);

-- used when we get descendants or ancestors
CREATE INDEX api_DirectPoliticalRelation_path_gist
          ON api_DirectPoliticalRelation
       USING GIST(path);
