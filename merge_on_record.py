import json

def merge_on_records():
	merged_json = []
	temp_dict = {}
	with open('on_record_1.json', 'r') as f1, open('on_record_2.json', 'r') as f2:
		rec2 = json.load(f2)
		for rec in rec2:
			if next(iter(rec.keys())) in temp_dict:
				temp_dict[next(iter(rec.keys()))] += 1
			else:
				temp_dict[next(iter(rec.keys()))] = 1
				merged_json.append(rec)

		rec1 = json.load(f1)
		for rec in rec1:
			if next(iter(rec.keys())) in temp_dict:
				temp_dict[next(iter(rec.keys()))] += 1
			else:
				temp_dict[next(iter(rec.keys()))] = 1
				merged_json.append(rec)

		print(len(merged_json))		

	with open('on_record.json', 'w') as ff:
		json.dump(merged_json, ff)

def analyze_prev_record():
	temp_dict = {}
	count = 0
	with open('MetaPainting/on_record.json', 'r') as f2:
		for rec in json.load(f2):
			if next(iter(rec.keys())) in temp_dict:
				temp_dict[next(iter(rec.keys()))] += 1
				count += 1
			else:
				temp_dict[next(iter(rec.keys()))] = 1
	print('Repeated unnecessary data', count)

analyze_prev_record()