from urllib.request import urlopen, quote
import json, sys

QUERY = """
SELECT ?person ?personLabel ?dateOfBirth ?dateOfDeath ?articleMA WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE]".
    ?person rdfs:label ?personLabel .
    

    } 
  ?person wdt:P31 wd:Q5.
  ?person wdt:P27 wd:Q1028.

  OPTIONAL {?person wdt:P569 ?dateOfBirth. }

  OPTIONAL {?person wdt:P570 ?dateOfDeath. }
  
  
  
      ?articleMA schema:about ?person .
      ?articleMA schema:name ?personLabel .
      ?articleMA schema:inLanguage "ar" .
      ?articleMA schema:isPartOf <https://ar.wikipedia.org/> .
   
  
  
	
	FILTER EXISTS {
        
      ?articleMA schema:about ?person .
      ?articleMA schema:inLanguage "ar" .
      ?articleMA schema:isPartOf <https://ar.wikipedia.org/> .
    }
  
 
 
  
}

group by ?person ?personLabel ?nativeName ?dateOfBirth ?dateOfDeath  ?articleMA


LIMIT 5000
"""

QUERY2 = """
# examples of dates, precision, time zones and calendars
SELECT ?time ?timeprecision ?timezone ?timecalendar ?timecalendarLabel
WHERE
{ SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
     { wd:Q5598  p:P569/psv:P569 ?timenode. }  # Jul 15, 1606
     UNION 
     { wd:Q220   p:P571/psv:P571 ?timenode. } # 13 April 753 BCE
     UNION 
     { wd:Q1     p:P580/psv:P580 ?timenode. } # 13798 million years BCE
  
     ?timenode wikibase:timeValue         ?time.
     ?timenode wikibase:timePrecision     ?timeprecision.
     ?timenode wikibase:timeTimezone      ?timezone.
     ?timenode wikibase:timeCalendarModel ?timecalendar.
  
     
}
"""

TIMEQUERY = """
SELECT ?time ?timeprecision
WHERE
{ SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
     { wd:{1}  p:{2}/psv:{2} ?timenode. }
     ?timenode wikibase:timeValue         ?time.
     ?timenode wikibase:timePrecision     ?timeprecision.
     
}
"""
filename = './data/query.sparql'
def wikidata_rest_query(filename):
    with open(filename,'r',encoding='utf8') as f:
        query = f.read()
    url = "https://query.wikidata.org/sparql?query=%s&format=json" % quote(query)
    with urlopen(url) as f:
        response = f.read().decode("utf-8")
    return json.loads(response)

jason = wikidata_rest_query(filename)

print(dict(jason))

def get_precision(objectCode,date_type,date):
    #print(objectCode)
    #print(date_type)
    #print(date)
    query = TIMEQUERY.replace('{1}',objectCode).replace('{2}',date_type)
    #print(query)
    url = "https://query.wikidata.org/sparql?query=%s&format=json" % quote(query)
    with urlopen(url) as f:
        response = f.read().decode("utf-8")

    res = json.loads(response)
    #print(res)
    values = []
    for i in range(len(res['results']['bindings'])):
        if res['results']['bindings'][i]['time']['value'] == date:

            values.append(int(res['results']['bindings'][i]['timeprecision']['value']))

    return max(values)
    

def simplify_json(jason):
    dict_list = []
    
    for i in range(len(jason['results']['bindings'])):
        print(i)
        print(jason['results']['bindings'][i]['personLabel']['value'])
        dict_list.append({})
        dict_list[i]['personLabel']    = jason['results']['bindings'][i]['personLabel']['value']
        try:
            dict_list[i]['dateOfBirth']    = jason['results']['bindings'][i]['dateOfBirth']['value']
            
        except KeyError:
            print('Date of Birth not available for '+jason['results']['bindings'][i]['personLabel']['value'])
            print(sys.exc_info())
        objectCode = jason['results']['bindings'][i]['person']['value'].split('/')[-1]
        date_type  = 'P569'
        date       = dict_list[i]['dateOfBirth']
        dict_list[i]['birthPrecision'] = get_precision(objectCode,date_type,date)
        try:
            dict_list[i]['dateOfDeath']    = jason['results']['bindings'][i]['dateOfDeath']['value']
            objectCode = jason['results']['bindings'][i]['person']['value'].split('/')[-1]
            date_type  = 'P570'
            date       = dict_list[i]['dateOfDeath']
            dict_list[i]['deathPrecision'] = get_precision(objectCode,date_type,date)
        except KeyError:
            print('Date of Death not available for '+jason['results']['bindings'][i]['personLabel']['value'])
            print(sys.exc_info())
    return dict_list

print(simplify_json(jason))
