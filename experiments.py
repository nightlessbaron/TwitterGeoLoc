def process_database_file():	
	import json, os, unicodedata
	path = 'C:/Users/Varad/OneDrive/Desktop/carmen-python/carmen/data/'
	os.chdir(path)
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


def loading_data():
	import json
	in_file = open('carmen/data/on_record.json')
	arr = json.load(in_file)
	for a in arr:
		print(*a)
		break

#------------------------------------------------

def loading_unique_id():
	import json
	unique = {}
	with open('dataset/dataset.json', 'r', encoding='utf-8') as ff:
		for line in ff.readlines():
			json_line = json.loads(line)
			if json_line['place'] == None:
				continue
			geoid = json_line.get('place', {}).get('id', '')
			if geoid != '' and geoid not in unique:
				unique[geoid] = json_line.get('place', {}).get('full_name', '')
	print(unique)

#-------------------------------------------------

def modify_json(file1, file2):
	import json, os
	with open(file1, 'r') as ff, open(file2, 'a', encoding='utf-8') as ag:
		data = json.load(ff)
		for itr in data:
			json.dump(itr, ag)
			ag.write('\n')
	os.remove('dataset/00_other.json')

# ---------------------------------------------------

def unique_prof_loc():
	import json, os
	with open('profile_locations.json', 'r') as ff, open('carmen/data/profile_locations_resolved.json', 'a') as plr, \
	open('profile_locations_unresolved.json', 'a') as plu:
		location_string = json.load(ff)
		for location in location_string:
			if next(iter(location.values())) == [None, None, None, None]:
				json.dump(location, plu)
				plu.write('\n')
			else:
				json.dump(location, plr)
				plr.write('\n')

if __name__ == '__main__':
	modify_json('dataset/00_other.json', 'dataset/00_other_modified.json')