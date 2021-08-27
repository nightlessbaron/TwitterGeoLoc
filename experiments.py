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

def modify_json():
	import json, os
	with open('dataset/twitter_geo.json', 'r') as ff, open('dataset/arxiv_geo.json', 'a', encoding='utf-8') as ag:
		data = json.load(ff)
		for itr in data:
			json.dump(itr, ag)
			ag.write('\n')
	os.remove('dataset/twitter_geo.json')

if __name__ == '__main__':
	modify_json()