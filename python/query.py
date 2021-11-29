def query(url):
	response = requests.get(url).json()
	
	return response