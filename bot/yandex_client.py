import requests
import os

BASE_URL = "https://cloud-api.yandex.net/v1/disk"


def get_token():
    return os.getenv("YANDEX_TOKEN")


def ensure_folder_exists(path: str):
    headers = {"Authorization": f"OAuth {get_token()}"}
    resp = requests.put(f"{BASE_URL}/resources", headers=headers, params={"path": path})
    return resp.status_code in (201, 409)


def upload_file_to_yandex(local_path: str, remote_path: str) -> bool:
    headers = {"Authorization": f"OAuth {get_token()}"}
    folder = remote_path.split("/")[0]
    ensure_folder_exists(folder)

    params = {"path": remote_path, "overwrite": "true"}
    resp = requests.get(f"{BASE_URL}/resources/upload", headers=headers, params=params)
    if resp.status_code != 200:
        print("❌ Ошибка получения upload URL:", resp.status_code, resp.text)
        return False

    href = resp.json().get("href")
    if not href:
        return False

    with open(local_path, "rb") as f:
        upload_resp = requests.put(href, files={"file": f})
        print("Yandex upload:", upload_resp.status_code)
        return upload_resp.status_code in (201, 202)


def get_disk_info():
    """Возвращает данные о диске: свободное/занятое/всего"""
    headers = {"Authorization": f"OAuth {get_token()}"}
    r = requests.get(BASE_URL, headers=headers)
    if r.status_code != 200:
        print("⚠️ Ошибка при запросе информации о диске:", r.status_code, r.text)
        return {"free_space": 0, "used_space": 0, "total_space": 0}

    data = r.json()
    return {
        "free_space": data["total_space"] - data["used_space"],
        "used_space": data["used_space"],
        "total_space": data["total_space"],
    }
