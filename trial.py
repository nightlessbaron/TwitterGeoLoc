import json
in_file = open('carmen/data/on_record.json')
arr = json.load(in_file)
for a in arr:
	print(*a)
	break