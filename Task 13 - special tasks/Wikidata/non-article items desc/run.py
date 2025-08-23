import csv
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import requests
import pywikibot

def get_final_qid(qid):
    params = {
        'action': 'wbgetentities',
        'ids': qid,
        'format': 'json'
    }
    try:
        response = requests.get('https://www.wikidata.org/w/api.php', params=params)
        data = response.json()

        entities = data.get('entities', {})
        if not entities:
            return qid  # fallback

        entity_data = entities.get(qid)
        # If it's a redirect, the real QID is in entity_data['redirects']['to']
        if entity_data and 'redirects' in entity_data:
            return entity_data['redirects']['to']

        return qid
    except:
        print(response.text)



def should_exclude_item(item):
    if 'ary' in item.descriptions:
        return True
    return False

def extract_qid(url):
    return url.strip().rsplit('/', 1)[-1]

def main():
    batch_count = 93
    MAX_BATCH_ROWS = 15000
    #total disambig 1509721
    start_index = 1423777
    site = pywikibot.Site("wikidata", "wikidata")
    site.throttle.maxdelay = 0
    site.login()
    repo = site.data_repository()
    root = tk.Tk()
    root.withdraw()

    DESC_BY_ITEMS = {"cat":"تصنيف د ويكيميديا"
                    ,"disambig":"صفحة توضيح ديال ويكيميديا"
                    ,"mod":"مودول د ويكيميديا"
                    ,"tmp":"موضيل د ويكيميديا"
                    ,"list":"ليستة د ويكيميديا"
                    #,"main":"الصفحة اللولة د ويكيميديا"
                    ,"proj":"صفحة د لپروجي د ويكيميديا"
                    #,"port":"صفحة د لپروجي د ويكيميديا"
                    #,"help":"صفحة د لمعاونة د ويكيميديا"
                    }

    file_path = filedialog.askopenfilename(
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    if not file_path:
        messagebox.showerror("Error", "No input file selected.")
        return

    description = DESC_BY_ITEMS["cat"] #simpledialog.askstring("Description", "Enter the Darija description (ary):")
    print(description)
    if not description:
        messagebox.showerror("Error", "No description provided.")
        return

    quickstatements = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        #reader = csv.DictReader(csvfile)
        reader = list(csv.DictReader(csvfile))
        if not reader or "item" not in reader[0]:
            messagebox.showerror("Error", "'item' column not found in CSV.")
            return
        output_path = f"batch cats {batch_count}.txt"
        i = -1
        for j in range(start_index, len(reader)):
            row = reader[j]
            
            qid = extract_qid(row["item"])
            final_qid = get_final_qid(qid)
            print(f"{j}: {final_qid}")
            try:
                item = pywikibot.ItemPage(repo, final_qid)
                item.get()
            except pywikibot.exceptions.NoPageError:
                print("the item was deleted")
                continue
            
            if should_exclude_item(item):
                print("already has ary desc")
                continue
            with open(output_path, 'a', encoding='utf-8') as f:
                i+=1
                line = f"{final_qid}\tDary\t\"{description}\""
                f.write(line + "\n")
            if i >= MAX_BATCH_ROWS:
                i = 0
                print(f"QuickStatements saved to {output_path}")
                batch_count+=1
                output_path = f"batch cats {batch_count}.txt"
            
    
    #messagebox.showinfo("Success", f"QuickStatements saved to {output_path}")

if __name__ == "__main__":
    main()
