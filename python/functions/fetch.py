import requests

def fetch(url):
	response = requests.get(url).json()
	
	return response