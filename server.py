from flask import Flask, send_file, jsonify
import os
import datetime
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)

@app.route("/")
def home():
    return "ok"

@app.route("/api/request/<year>/<month>/<day>")
def request_files(year, month, day):
    clean()
    year = int(year)
    month = int(month)
    day = int(day)

    save_path = "./temp_files"

    base_save_path = "./temp_files"
    base_url = "https://sprg.ssl.berkeley.edu/data/maven/data/sci/"
    date_path = f"{year}{month:02d}{day:02d}"

    doy = (datetime.datetime(year, month, day) - datetime.datetime(year, 1, 1)).days + 1

    instrument_folders = {
        'swi': [f"mvn_swi_l2_onboardsvymom_{date_path}", f"mvn_swi_l2_onboardsvyspec_{date_path}"],
        'swe': [f"mvn_swe_l2_svypad_{date_path}", f"mvn_swe_l2_svyspec_{date_path}"],
        'sta': [f"mvn_sta_l2_d0-32e4d16a8m_{date_path}",
                f"mvn_sta_l2_d1-32e4d16a8m_{date_path}",
                f"mvn_sta_l2_c6-32e64m_{date_path}"],
        'mag': [f"mvn_mag_l2_{year}{doy:03d}ss_{date_path}"],
        'lpw': [f"mvn_lpw_l2_lpnt_{date_path}"],
        'sep': [f"mvn_sep_l2_s1-cal-svy-full_{date_path}"]
    }

    for inst, prefixes in instrument_folders.items():
        full_url = f"{base_url}/{inst}/l2/{year}/{month:02d}/"
        print(f"访问 {full_url}")

        try:
            resp = requests.get(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            for prefix in prefixes:
                found = False
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href and href.startswith(prefix) and (href.endswith('.cdf') or href.endswith('.sts')):
                        if href.endswith('.sts') and not href.startswith("mvn_mag_l2_"):
                            continue
                        file_url = full_url + href
                        print(f"下载中: {file_url}")
                        file_path = os.path.join(save_path, href)
                        with requests.get(file_url, stream=True) as r:
                            r.raise_for_status()
                            with open(file_path, 'wb') as f:
                                for chunk in r.iter_content(chunk_size=8192):
                                    f.write(chunk)
                        found = True
                        break

                if not found:
                    print(f"未找到: {prefix}")

        except Exception as e:
            print(f"失败: {e}")

    return f"Files Downloaded: {len(os.listdir("./temp_files"))}", 200

@app.route("/api/download/<string:name>")
def download(name):
    if (not os.path.exists(os.path.join("temp_files", name))):
        return "file not found", 404
    
    return send_file(os.path.join("temp_files", name))

@app.route("/api/clean")
def clean():
    files = os.listdir("./temp_files")

    if len(files) == 0:
        return "no files to delete", 404

    for file in files:
        os.remove(os.path.join("temp_files", file))
    
    return "all_files_cleared", 200

@app.route("/api/check")
def check():
    files = os.listdir("./temp_files")

    return jsonify(files)

if __name__ == "__main__":
    os.makedirs("./temp_files", exist_ok=True)
    app.run(debug=True, port=8000)
