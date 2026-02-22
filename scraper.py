
import requests
import re
import concurrent.futures

class XSportScraper:
    def __init__(self):
        self.base_pattern = "https://www.xsportv{}.xyz/"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        self.channel_ids = [
            "xbeinsports-1", "xbeinsports-2", "xbeinsports-3", "xbeinsports-4", "xbeinsports-5",
            "xbeinsportsmax-1", "xbeinsportsmax-2", "xtivibuspor-1", "xtivibuspor-2",
            "xtivibuspor-3", "xtivibuspor-4", "xssport", "xssport2", "xtabiispor1",
            "xtabiispor2", "xtabiispor3", "xtabiispor4", "xtabiispor5", "xtabiispor6", "xtabiispor7"
        ]
        self.logo = "https://i.hizliresim.com/b6xqz10.jpg"

    def check_domain(self, index):
        url = self.base_pattern.format(index)
        try:
            response = self.session.head(url, timeout=3)
            if response.status_code in [200, 302]:
                return url
        except requests.RequestException:
            return None

    def find_active_domain(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = [executor.submit(self.check_domain, i) for i in range(56, 250)]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    executor.shutdown(wait=False, cancel_futures=True)
                    return result
        return None

    def get_stream_url(self, player_url, stream_id):
        try:
            res = self.session.get(player_url, timeout=5)
            match = re.search(r"baseStreamUrl\s*=\s*['\"](.*?)['\"]", res.text)
            if match:
                base = match.group(1)
                return f"{base}{stream_id}/playlist.m3u8"
        except requests.RequestException:
            return None

    def run(self):
        domain = self.find_active_domain()
        if not domain:
            print("Aktif domain bulunamadı.")
            return

        print(f"Aktif domain: {domain}")
        try:
            response = self.session.get(domain, timeout=5)
        except requests.RequestException:
            print("Ana sayfa alınamadı.")
            return

        m3u_content = "#EXTM3U\n"

        for cid in self.channel_ids:
            pattern = rf'data-url="(.*?id={cid}.*?)"'
            match = re.search(pattern, response.text)

            if match:
                player_link = match.group(1)
                final_url = self.get_stream_url(player_link, cid)

                if final_url:
                    name = cid.replace("x", "").replace("-", " ").upper()
                    m3u_content += f'#EXTINF:-1 tvg-id="" tvg-logo="{self.logo}" group-title="XSPORT", TR: {name} HD\n'
                    m3u_content += f"#EXTVLCOPT:http-referer={domain}\n"
                    m3u_content += f"{final_url}\n"

        with open("deathless-xsportv.m3u", "w", encoding="utf-8") as f:
            f.write(m3u_content)

        print("M3U dosyası oluşturuldu.")

if __name__ == "__main__":
    bot = XSportScraper()
    bot.run()
