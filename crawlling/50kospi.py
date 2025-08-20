import os
import requests
from bs4 import BeautifulSoup

# 저장 디렉토리
SAVE_DIR = r'C:\Workspace\crawlling'
os.makedirs(SAVE_DIR, exist_ok=True)

# 크롤링 대상 URL (코스피, page=1)
URL = "https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page=1"

def fetch_top50_kospi():
    res = requests.get(URL)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # 기업 리스트
    items = soup.select("tbody tr")

    result = []
    for row in items:
        link = row.select_one("td:nth-child(2) a")
        if not link:
            continue
        href = link.get("href", "")
        code = href.split("code=")[-1]
        name = link.get_text(strip=True)
        if code and name:
            result.append((code, name))
        if len(result) >= 50:
            break

    return result

def save_to_txt(data):
    path = os.path.join(SAVE_DIR, "stocks.txt")
    with open(path, "w", encoding="utf-8-sig") as f:
        for code, name in data:
            f.write(f"{code}:{name}\n")
    return path

def main():
    print("크롤링 중...")
    data = fetch_top50_kospi()
    if not data:
        print("데이터를 가져오지 못했습니다.")
        return

    filepath = save_to_txt(data)
    print(f"[완료] '{filepath}'에 저장됨")
    for i, (c, n) in enumerate(data, 1):
        print(f"{i:2d}. {c}:{n}")

if __name__ == "__main__":
    main()
