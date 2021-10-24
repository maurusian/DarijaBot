from pgvbotLib import *
import pywikibot
import xml.etree.ElementTree as ET



PERSON_INFO_TAG = ""
XML = "model.xml"

def load_xml():
    article = [] #list of paragraphs
    tree = ET.parse(XML)
    root = tree.getroot()
    print(root.tag)


load_xml()
#site = pywikibot.Site()

