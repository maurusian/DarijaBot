edits = int(input("Edits: "))

articles = int(input("Articles: "))

total_pages = int(input("Total pages: "))

depth = (edits/total_pages)*(((total_pages - articles)/articles)**2)

print("depth: "+str(depth))
