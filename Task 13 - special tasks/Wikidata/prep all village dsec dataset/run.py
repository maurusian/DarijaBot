import pandas as pd
import pywikibot
from pywikibot import pagegenerators
from pywikibot.data import api

offset = 31000

# --- Step 1: Load QIDs from Excel ---
def load_qids(filepath):
    df = pd.read_excel(filepath)
    return df['qid'].dropna().unique().tolist()

# --- Step 2: Check if item should be excluded ---
def should_exclude_item(item):
    if 'ary' in item.descriptions:
        return True
    claims = item.claims
    if 'P582' in claims or 'P576' in claims:
        return True
    return False

# --- Step 3: Get valid country labels from P17 ---
def get_valid_country_labels(item, site):
    if 'P17' not in item.claims:
        return []

    country_labels = []
    for claim in item.claims['P17']:
        country = claim.getTarget()
        if not country or not isinstance(country, pywikibot.ItemPage):
            continue
        country.get()
        # Check P31 = Q6256
        if 'P31' not in country.claims:
            continue
        if not any(p.getTarget().id == 'Q6256' for p in country.claims['P31']):
            continue
        # Check ary label
        if any(p.getTarget().id == 'Q3024240' for p in country.claims['P31']):
            continue
        if 'ary' not in country.labels:
            continue
        country_labels.append(country.labels['ary'])

    return list(set(country_labels))  # deduplicate

# --- Step 4: Process items ---
def process_items(qids, repo, site, output_path):
    #results = []
    i = 0
    for qid in qids:
        i+=1
        print(f"************ {i}/241139: {qid}")
        if i>offset: #already treated
            try:
                item = pywikibot.ItemPage(repo, qid)
                item.get()
                if should_exclude_item(item):
                    print("treated")
                    continue
                labels = get_valid_country_labels(item, site)
                if labels:
                    #results.append({'qid': qid, 'country': ', '.join(labels)})
                    with open(output_path, 'a', encoding='utf-8') as f:
                        country_desc = ', '.join(labels)
                        description = f'دوّار ف {country_desc}'
                        line = f'{qid}\tDary\t"{description}"\n'
                        f.write(line)
                else:
                    print("no country field")
            except Exception as e:
                print(f"Error processing {qid}: {e}")
            
    #return results

# --- Step 5: Save to Excel ---
def save_to_excel(data, output_path):
    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)

# --- Step 5: Save QuickStatements for descriptions ---
def save_quickstatements(data, output_path):
    with open(output_path, 'a', encoding='utf-8') as f:
        for row in data:
            qid = row['qid']
            country_desc = row['country']
            description = f'دوّار ف {country_desc}'
            line = f'{qid}\tDary\t"{description}"\n'
            f.write(line)


# --- Main execution ---
def main():
    input_path = "all villages in Wikidata.xlsx"
    output_path = "villages_with_country_quickstatements.txt"
    qids = load_qids(input_path)

    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()

    process_items(qids, repo, site, output_path)
    #save_quickstatements(results, output_path)

if __name__ == "__main__":
    main()
