-- function to calculate the path of any given polent
CREATE OR REPLACE FUNCTION _update_polent_path() RETURNS TRIGGER AS
$$
BEGIN
    IF NEW.parent_id IS NULL THEN
        NEW.path = NEW.entity_id::text::ltree;
    ELSE
        SELECT path || NEW.entity_id::text
          FROM api_DirectPoliticalRelation
         WHERE NEW.parent_id IS NULL or politicalrelation_ptr_id = NEW.parent_id
          INTO NEW.path;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- function to update the path of the descendants of a polent
CREATE OR REPLACE FUNCTION _update_descendants_polent_path() RETURNS TRIGGER AS
$$
BEGIN
    UPDATE api_DirectPoliticalRelation
       SET path = NEW.path || subpath(api_DirectPoliticalRelation.path, nlevel(OLD.path))
     WHERE api_DirectPoliticalRelation.path <@ OLD.path AND politicalrelation_ptr_id != NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- calculate the path every time we insert a new polent
DROP TRIGGER IF EXISTS polent_path_insert_trg ON api_DirectPoliticalRelation;
CREATE TRIGGER polent_path_insert_trg
               BEFORE INSERT ON api_DirectPoliticalRelation
               FOR EACH ROW
               EXECUTE PROCEDURE _update_polent_path();


-- calculate the path when updating the parent or the entity_id
DROP TRIGGER IF EXISTS polent_path_update_trg ON api_DirectPoliticalRelation;
CREATE TRIGGER polent_path_update_trg
               BEFORE UPDATE ON api_DirectPoliticalRelation
               FOR EACH ROW
               WHEN (OLD.parent_id IS DISTINCT FROM NEW.parent_id
                     OR OLD.entity_id IS DISTINCT FROM NEW.entity_id)
               EXECUTE PROCEDURE _update_polent_path();


-- if the path was updated, update the path of the descendants
DROP TRIGGER IF EXISTS polent_path_after_trg ON api_DirectPoliticalRelation;
CREATE TRIGGER polent_path_after_trg
               AFTER UPDATE ON api_DirectPoliticalRelation
               FOR EACH ROW
               WHEN (NEW.path IS DISTINCT FROM OLD.path)
               EXECUTE PROCEDURE _update_descendants_polent_path();
