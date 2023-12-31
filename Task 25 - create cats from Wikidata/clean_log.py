'''
def replace_category_with_link(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        if 'تّصنيف تصنيف:' in line:
            start_index = line.find('تصنيف:')
            end_index = line.find(' ماقدرش لبوت', start_index)
            category_name = line[start_index:end_index]
            wiki_link = f"[[:{category_name}]]"
            updated_line = line.replace(category_name, wiki_link)
            updated_lines.append(updated_line)
        else:
            updated_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(updated_lines)

def remove_duplicates(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        unique_lines = set(file.readlines())

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(unique_lines)



# Replace 'your_log_file.txt' with the path to your log file
replace_category_with_link('remote_log.txt')

# Replace 'your_log_file.txt' with the path to your log file
remove_duplicates('remote_log.txt')
'''
import pywikibot
import traceback
def is_linked_on_wikidata(page_name):
    site = pywikibot.Site("ary", "wikipedia")
    repo = site.data_repository()
    try:
        page = pywikibot.Page(site,page_name)
        item = pywikibot.ItemPage.fromPage(page)
        return True if item.exists() else False
    except Exception as e:
        print("An error occurred: ", str(e))
        print(traceback.format_exc())
        return False

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        if '[[:' in line and ']]' in line:
            start_index = line.find('[[:') + 3  # 3 is the length of '[[:'
            end_index = line.find(']]', start_index)
            page_name = line[start_index:end_index]

            if not is_linked_on_wikidata(page_name):
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(updated_lines)

# Replace 'your_log_file.txt' with the path to your log file
process_file('remote_log.txt')
