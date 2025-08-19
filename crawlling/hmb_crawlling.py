import requests
from bs4 import BeautifulSoup
import csv;
import os;

save_dir = 'C:\Workspace\crawlling';

file_path = os.path.join(save_dir, 'hmb_stock_prices.csv');

# 2. 헤더 및 파일 오픈
with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['시가', '종가'])  # CSV 헤더 작성

    # 3. page=1부터 page50까지 반복
    for page in range(1, 51):  # 1~50 페이지
        url = f'https://finance.naver.com/item/sise_day.naver?code=042700&page={page}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }

        # 4. 요청 및 파싱
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        rows = soup.select('table.type2 tr')

        # 5. 데이터 추출
        for row in rows:
            cols = row.select('td')
            if len(cols) > 1:
                oepn_price = cols[3].text.strip()
                close_price = cols[1].text.strip()
                writer.writerow([oepn_price, close_price])

        print(f"[INFO] 페이지 {page} 완료")

print(f"\n[완료] 50페이지 데이터가 저장되었습니다: {file_path}")