import pywikibot
import re

def extract_links_from_paragraph(page_title, paragraph_title):
    # Set up the site and the page
    site = pywikibot.Site('ary', 'wikipedia')
    page = pywikibot.Page(site, page_title)

    # Get the page content
    text = page.get()

    # Split the text into sections
    sections = text.split('==')

    # Find the section with the given title
    paragraph_text = None
    for i in range(len(sections)):
        if paragraph_title.strip() in sections[i].strip():
            # The actual paragraph text is the section after the title
            paragraph_text = sections[i + 1]
            break

    if not paragraph_text:
        print(f'Paragraph titled "{paragraph_title}" not found.')
        return []

    # Extract links from the paragraph text
    links = []
    link_start = paragraph_text.find('[')
    while link_start != -1:
        link_end = paragraph_text.find(']', link_start)
        if link_end == -1:
            break

        link = paragraph_text[link_start + 1:link_end]
        if link.startswith('['):  # Handle double square brackets for links
            link = link[1:]
            link = link.split('|')[0]  # Remove display text if present
        links.append(link)

        link_start = paragraph_text.find('[', link_end)

    return links

def extract_qids_from_page(page_title):
    # Set up the site and the page
    site = pywikibot.Site('ary', 'wikipedia')
    page = pywikibot.Page(site, page_title)

    # Get the page content
    text = page.get()

    # Regex to find QIDs (e.g., Q12345)
    qid_pattern = r'Q\d+'
    qids = re.findall(qid_pattern, text)

    # Return unique QIDs
    return list(set(qids))

def get_qids_from_titles(titles):
    qids = set()
    
    for title in titles:
        try:
            page_qids = extract_qids_from_page(title)
            qids.update(page_qids)
        except Exception as e:
            print(f"Error retrieving QIDs for {title}: {e}")
    
    return list(qids)

def write_qids_to_file(qids, filename):
    with open(filename, 'w') as file:
        for qid in qids:
            file.write(f"{qid}\n")

if __name__=="__main__":
    page_title = 'ويكيپيديا:1000 مقالة خاص يكونو ف جميع لويكيپيديات'
    paragraph_title = 'ليستات د لمواضيع'
    links = extract_links_from_paragraph(page_title, paragraph_title)
    qids = get_qids_from_titles(links)
    filename = 'qids.txt'
    write_qids_to_file(qids, filename)
