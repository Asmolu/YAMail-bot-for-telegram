import requests
import os

YA_TOKEN = os.getenv("YANDEX_TOKEN")
BASE_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"

def upload_file_to_yandex(local_path: str, remote_path: str) -> bool:
    headers = {"Authorization": f"OAuth {YA_TOKEN}"}
    params = {"path": remote_path, "overwrite": "true"}

    # Получаем ссылку для загрузки
    resp = requests.get(BASE_URL, headers=headers, params=params)
    if resp.status_code != 200:
        return False

    href = resp.json().get("href")
    if not href:
        return False

    # Загружаем файл
    with open(local_path, "rb") as f:
        upload_resp = requests.put(href, files={"file": f})
        return upload_resp.status_code in (201, 202)
 