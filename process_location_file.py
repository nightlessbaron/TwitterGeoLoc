import json, os
path = 'C:/Users/Varad/OneDrive/Desktop/carmen-python/carmen/data/'
os.chdir(path)

import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

with open('location_all_countries_restricted.json', encoding='utf-8') as floc:
	lines = json.load("[" + floc.read().replace("}\n{", "},\n{") + "]")
	#.split('\n')
	#for line in lines:
#		line["name"] = remove_accents(line["name"])
#		line["aliases"] = [remove_accents(i) for i in line["aliases"].split(', ')]
#		with open('new_location_database.json', 'a', encoding='ascii') as file:
#			json.dumps(line, file)
#			file.write('\n')