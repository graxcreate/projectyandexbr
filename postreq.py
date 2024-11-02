import requests

url = "http://localhost:8000/process_files"
token = "y0_AgAAAABr_8ycAADLWwAAAAEWoToZAAC4rpCZTHRD3rqHBV85aarbBnIoSg"

payload = {"token": token}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("API call successful!")
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")
    print(response.text)