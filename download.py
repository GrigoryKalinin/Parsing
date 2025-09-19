import requests

url = "https://www.stankiproma.ru/wp-content/uploads/feed-yml-0.xml"
response = requests.get(url)

with open("feed-yml-0.xml", "wb") as file:
    file.write(response.content)

print("Файл скачан")