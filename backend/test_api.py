import requests

# Test getting contract versions
response = requests.get('http://localhost:8000/api/contracts/1/versions/1')
print('Status code:', response.status_code)
print('Content:', response.json())
