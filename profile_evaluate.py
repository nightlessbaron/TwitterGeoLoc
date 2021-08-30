import json, os
from geopandas import GeoSeries
from shapely.geometry import Polygon
from geopy.geocoders import Nominatim
import unidecode

# Utils
# Ok, above code is working alright :)
def round_float(inp):
	return str(round(float(inp), 1))

def compute_centroid(metadata):
	if metadata['place'] != None:
		bounding_box = tuple(metadata.get('place', {}).get('bounding_box', {}).get('coordinates', '')[0])
		shape = GeoSeries(Polygon(bounding_box))
		return str(shape.centroid.y[0]), str(shape.centroid.x[0]) # Return in format (Latitude, Longitude)
	return None, None

def process_tweet(text):
	return text.replace('\n\n', ' ').replace('\r\n', ' ').replace('\n', ' ')

def get_location(location):
	city = location.raw.get('city', '')
	if city == '':
		city = location.raw.get('address', {}).get('town', '')
	elif city == '':
		city = location.raw.get('address', {}).get('village', '')
	else:
		city = location.raw.get('address', {}).get('county', '')
	state = location.raw.get('address', {}).get('state', '')
	country = location.raw.get('address', {}).get('country', '')
	return city, state, country

def new_locations(city, state, new_city, new_state):
	if city != '':
		if new_city != city and new_city != '':
			city = new_city
	else:
		city = new_city
	if state != '':
		if new_state != state and new_state != '':
			city = new_state
	else:
		state = new_state
	return city, state

# Get requests from geonames-service using python
import requests, csv

def try_once(place, record, place_dict):
	try_place = {'USA':'Puerto Rico'}
	country = place.split(',')[1]
	if country in try_place:
		place = place.replace(country, try_place[country])
		return get_place(place, record, place_dict, 1)
	else:
		with open('off_record.txt', 'a') as ff:
			ff.write(place+'\n')
		return None, None, None, record+1, None

def get_place(place, record, place_dict, flag):  # Record computes how many times the research results in None
	if place in place_dict: #.split(',')[0]
		location = place_dict[place]
	else:
		response = requests.get('http://ee97-34-73-65-113.ngrok.io/location?location='+place).json()
		location = response.get('records', [])
		if len(location) != 0:
			location = location[0]
		place_dict[place] = location #.split(',')[0]
	if location == []:
		if flag == 0:
			return try_once(place, record, place_dict)
		with open('off_record.txt', 'a') as ff:
			ff.write(place+'\n')
		return None, None, None, record+1, None
	else:
		city, state, country, geoid = location.get('Name', ''), location.get('State', '').split(' (')[0], location.get('Country', ''), location.get('GeonameId', '')
		if country in city:
			return '','',country, record, geoid
		elif state in city:
			return '', state, country, record, geoid
		else:
			return city.split(' (')[0], state, country, record, geoid

def location_name_change(line):
	name_change = {'Brasil':'Brazil', 'Espana':'Spain', 'Nederland':'Netherlands', 'Deutschland':'Germany', 'Belgie':'Belgium', 'Lombardia':'Lombardy',
	'Polska':'Poland', 'Sverige':'Sweden', 'Rossiia':'Russia', 'Piemonte':'Piedmont', 'Danmark':'Denmark', 'Schweiz':'Switzerland', 'Suisse':'Switzerland',
	'Lazio':'Latium', 'Norge':'Norway', 'Belgique':'Belgium', 'Osterreich':'Austria', 'Veracruz de Ignacio de la Llave':'Veracruz', 'Toscana':'Tuscany',
	'Magyarorszag':'Hungary', 'Latvija':'Latvia', 'Pulau Pinang':'Penang', 'Puglia':'Apulia', 'Sicilia':'Sicily', 'Suomi':'Finland', 'Royaume du Maroc':'Morocco',
	'Distrito Federal':'Mexico City', 'Espanya':'Spain', 'Coahuila de Zaragoza': 'Coahuila', 'Trentino-South Tyrol':'Trentino-Alto Adige',
	'The Netherlands':'Netherlands', 'Sumatera Barat':'West Sumatra', 'Wilayah Persekutuan Kuala Lumpur':'Kuala Lumpur', 'Queretaro Arteaga':'Queretaro',
	'Nederlan':'Netherlands', 'Sulawesi Selatan':'South Sulawesi', 'Lietuva':'Lithuania', 'Svizzera':'Switzerland', 'Eesti':'Estonia', 'Sardegna':'Sardinia',
	'Melaka':'Malacca', 'Jawa Timur':'East Java', 'DKI Jakarta':'Jakarta', 'Sulawesi Utara':'North Sulawesi', 'Nusa Tenggara Barat': 'West Nusa Tenggara',
	'Kepulauan Riau':'Riau Islands', 'Sumatera Utara':'North Sumatra', "Tverskaia oblast'":"Tver Oblast", 'Comunidad Valenciana':'Valencian Community',
	'Sulawesi Tenggara':'South East Sulawesi', "Stavropol'skii krai":"Stavropol Krai", 'Sachsen':'Saxony', 'Putrajaya Federal Territory':'Putrajaya',
	'Pinang':'Penang', 'Picardie':'Picardy', "Novosibirskaia oblast'":"Novosibirsk Oblast", 'Nord-Pas-de-Calais':'Hauts-de-France', 'Negri Sembilan':'Negeri Sembilan',
	'Nangro Aceh Darussalam':'Aceh', "Moskovskaia oblast'":'Moscow Oblast', 'Mordoviia respublika':'Mordovia Republic', 'Kuala Lumpur Federal Territory':'Kuala Lumpur',
	"Kostromskaia oblast'":"Kostroma Oblast", 'Kalimantan Timur':'East Kalimantan', 'Johore':'Johor', 'Islas Canarias':'Canary Islands', 'Espainia':'Spain',
	'Buriatiia respublika':'Buryatia', 'Bretagne':'Brittany', 'Belgien':'Belgium', 'Bashkortostan respublika':'Bashkortostan', 'Andalucia':'Andalusia',
	"Iaroslavskaia oblast'":"Yaroslavl Oblast"}

	if len(line.split(',')) == 3:
		ncity, _, ncountry = line.split(',')
	elif len(line.split(',')) == 2:
		ncity, ncountry = line.split(',')
	elif len(line.split(',')) == 1:
		ncity = ''
		ncountry = line.split(',')[0]
	else:
		return line
	ncountry = ncountry.lstrip()
	if ncountry in name_change:
		fcountry = name_change[ncountry]
		if ncity != '':
			place = ncity + ',' + fcountry
		else:
			place = fcountry
	else:
		if ncity != '':
			place = ncity + ',' + ncountry
		else:
			place = ncountry
	return place

def main():
	geolocator = Nominatim(user_agent="geolocator")
	try:
		os.remove('off_record.txt')
	except:
		print("No such files present in the directory")
	json_array = []
	place_dict, count, record = {}, 0, 0
	with open('profile_location_database.txt', 'r', encoding='utf-8') as ff:
		prof_loc = ff.readlines()
		prof_loc = list(set(prof_loc))
		print("Unique Locations:", len(prof_loc))

	for itr, prof in enumerate(prof_loc):
		if itr > 5000:
			break
		prof = prof.replace('\n', '')
		place = location_name_change(prof)
		city, state, country, geoid = None, None, None, None
		try:
			if place != '': # Try finding the location in zoophy service (geonames service)
				city, state, country, record, geoid = get_place(place, record, place_dict, 0)
			if prof != '':
				json_array.append({prof: [geoid, city, state, country]})
		except:
			print("There was an exception,", prof, "skipped")

		if itr % 1000 == 0 and itr != 0:
			print(itr)
		if itr == 0:
			print("First iteration successful!")

	obj = json.dumps(json_array)
	with open('on_record.json', 'a') as fj:
		fj.write(obj)

	print(record)

if __name__ == '__main__':
	main()