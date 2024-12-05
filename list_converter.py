import json
import sys

# Read the file path from the first program argument
file_path = sys.argv[1]

# Read the content of the file
with open(file_path, 'r') as file:
    data = file.read()

# Split the data into individual JSON objects
json_objects = data.strip().split('\n')

# List to store the requested URLs
requested_urls = []

for json_str in json_objects:
    obj = json.loads(json_str)
    children_url = None
    landing_url = obj['landing'].get('finalUrl')
    requested_urls.append(landing_url)
    if obj['children']:
        children_url = obj['children'][0].get('finalUrl')
        requested_urls.append(children_url)

# Print each URL on a new line without quotes
for url in requested_urls:
    print(url)
