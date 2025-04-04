import requests

url = "https://emkc.org/api/v2/piston/runtimes"
response = requests.get(url)

if response.status_code == 200:
    languages = response.json()
    for lang in languages:
        print(f"Language: {lang['language']}, Version: {lang['version']}")
else:
    print("Failed to fetch languages")


