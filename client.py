import os
import requests
from bs4 import BeautifulSoup
import datetime
import json
import time

class FileProxyClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.url = f"http://{self.ip}:{self.port}"

        if requests.get(self.url).status_code != 200:
            raise Exception(f"Ping to the server:{self.url} failed!")
        
        if requests.get(self.url).text != "ok":
            raise Exception(f"Server ping returned unexpected reponse")

    def send_request(self, year, month, day):
        response = requests.get(f"{self.url}/api/request/{year}/{month}/{day}")

        if response.status_code != 200:
            return "Error: request to server failed!"

        return response.text
    
    def download_file(self, name, location):
        if not os.path.exists(location):
            raise Exception("Error: invalid location")

        response = requests.get(f"{self.url}/api/download/{name}", stream=True)

        if response.status_code != 200:
            raise Exception(f"Download failed: {response.status_code} - {response.text}")

        with open(os.path.join(location, name), "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return os.path.join(location, name)
    
    def check_files(self):
        response = requests.get(f"{self.url}/api/check")
        
        if response.status_code != 200:
            return []
        
        return response.json()

    def send_clean_request(self):
        return requests.get(f"{self.url}/api/clean")

    def auto_download(self, location):
        check_response = self.check_files()

        for file in check_response:
            self.download_file(file, location)
        
        return f"All Files Downloaded For: {os.path.join(location)}"

    def start_process(self, year=2016, month=12, day=1):
        year = year
        month = month
        day = day
        if os.path.exists("./info.json") and year != 2016 and month != 12 and day != 1:
            with open("./info.json", "r") as f:
                data = json.load(f)
                year = data.get("year")
                month = data.get("month")
                day = data.get("day")
            
        
        base_save_path = "./maven_data"
        if month == 12:
            next_month = datetime.date(year + 1, 1, 1)
        else:
            next_month = datetime.date(year, month + 1, 1)
        days_in_month = (next_month - datetime.timedelta(days=1)).day

        for day in range(day, days_in_month + 1):
            save_path = os.path.join(base_save_path, f"{year}", f"{month:02d}", f"{day:02d}")

            if os.path.exists(save_path) and os.listdir(save_path):
                print(f"跳过 {year}-{month:02d}-{day:02d}（已有数据）")
                continue

            os.makedirs(save_path, exist_ok=True)

            print(f"\n=== {year}-{month:02d}-{day:02d} ===")

            self.send_request(year, month, day)
            self.auto_download(save_path)
            self.send_clean_request()

            with open("./info.json", "w") as f:
                json.dump({ "year": year, "month": month, "day": day }, f, indent=4)


if __name__ == "__main__":
    client = FileProxyClient("172.233.183.49", 8000)
    try:
        client.start_process()
    except Exception as e:
        print("Error:", e)
