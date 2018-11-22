-- make sure we cannot have a path where one of the ancestor is the row itself
-- (this would cause an infinite recursion)
ALTER TABLE api_DirectPoliticalRelation
        ADD CONSTRAINT check_no_recursion
            CHECK(index(path, entity_id::text::ltree) = (nlevel(path) - 1));

ALTER TABLE api_IndirectPoliticalRelation
        ADD CONSTRAINT check_no_recursion
            CHECK(index(path, entity_id::text::ltree) = (nlevel(path) - 1));

