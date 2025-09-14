import os
import requests
import json

class FileProxyClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.url = f"http://{self.ip}:{self.port}"

        if requests.get(self.url).status_code != 200:
            raise Exception(f"Ping to the server:{self.url} failed!")
        
        if requests.get(self.url).text != "ok":
            raise Exception(f"Server ping returned unexpected reponse")

    def send_request(self, data):
        response = requests.get(f"{self.url}/api/request/{data}")

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

    def auto_download(self, location):
        check_response = self.check_files()

        for file in check_response:
            self.download_file(file, location)
        
        return f"All Files Downloaded For: {os.path.join(location)}"

if __name__ == "__main__":
    client = FileProxyClient("127.0.0.1", 8000)
    try:
        print(client.auto_download("./downloads"))
    except Exception as e:
        print("Error:", e)
