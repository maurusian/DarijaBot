use wikidatawiki_p; 
--SELECT CURRENT_DATE;
SELECT DISTINCT CONCAT('P', wbpt_property_id)
from wbt_property_terms 
ORDER bY wbpt_property_id asc;

use wikidatawiki_p; 
SELECT DISTINCT CONCAT('P',wbpt_property_id)
from wbt_property_terms 
--WHERE wbpt_property_id > 9000
LIMIT 11000;