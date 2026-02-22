
import json
import requests
from typing import List, Dict

class AutoM3U:
    def __init__(self, json_file="channels.json", output="playlist.m3u"):
        self.json_file = json_file
        self.output = output

    def load_channels(self) -> List[Dict]:
        with open(self.json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def check_stream(self, url: str) -> bool:
        try:
            r = requests.head(url, timeout=5)
            return r.status_code in [200, 302]
        except requests.RequestException:
            return False

    def generate(self):
        channels = self.load_channels()
        content = "#EXTM3U\n"

        for ch in channels:
            name = ch.get("name")
            url = ch.get("url")
            logo = ch.get("logo", "")
            group = ch.get("group", "GENEL")
            check = ch.get("check", False)

            if check:
                if not self.check_stream(url):
                    print(f"Atlandı (çalışmıyor): {name}")
                    continue

            content += (
                f'#EXTINF:-1 tvg-id="" tvg-logo="{logo}" '
                f'group-title="{group}", {name}\n'
            )
            content += f"{url}\n"

        with open(self.output, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"{self.output} oluşturuldu.")

if __name__ == "__main__":
    bot = AutoM3U()
    bot.generate()
