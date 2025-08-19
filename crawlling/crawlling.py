import requests
from bs4 import BeautifulSoup
import os;
import tkinter as tk
from tkinter import ttk, messagebox

    # ▶ 종목 코드와 종목명 리스트
stock_dict = {
    '042700': '한미반도체',
    '489790': '한화비전',
    '022100': '포스코DX',
    '055550': '신한지주'
}

CHO_TABLE = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ',
    'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
    'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ',
    'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

def get_chosung(text):
    result = ''
    for char in text:
        code = ord(char) - 44032
        if 0 <= code < 11172:
            chosung_index = code // 588
            result += CHO_TABLE[chosung_index]
        else:
            result += char
    return result

# ▶ 종목명: 종목코드로 역변환 (value → key)
name_to_code = {v: k for k, v in stock_dict.items()}

def fetch_stock_data(stock_code, stock_name, page_count):



    save_dir = 'C:\Workspace\crawlling';

    hwv_open_path = os.path.join(save_dir, f'{stock_name} 시가.txt');
    hwv_close_path = os.path.join(save_dir, f'{stock_name} 종가.txt');

    # 2. 헤더 및 파일 오픈
    with open(hwv_open_path, 'w', newline='', encoding='utf-8-sig') as f: # 한화비전 시가

        # 3. page=1부터 page50까지 반복
        for page in range(1, page_count+1): 
            url = f'https://finance.naver.com/item/sise_day.naver?code={stock_code}&page={page}'
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
                    if oepn_price: 
                        line = f"{oepn_price}\n"               
                        f.write(line)


    with open(hwv_close_path, 'w', newline='', encoding='utf-8-sig') as f: # 한화비전 종가
            # 3. page=1부터 page50까지 반복
        for page in range(1, page_count+1):  # 1~50 페이지
            url = f'https://finance.naver.com/item/sise_day.naver?code={stock_code}&page={page}'
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
                    oepn_price = cols[1].text.strip()
                    if oepn_price: 
                        line = f"{oepn_price}\n"               
                        f.write(line)

    messagebox.showinfo("✅ 완료", f"[{stock_name}] {page_count}0일차 크롤링 완료!")


# ▶ GUI 시작
def start_gui():
    def on_submit():
        stock_name = stock_var.get()
        stock_code = name_to_code.get(stock_name)
        pages = page_entry.get().strip()

        if not stock_code:
            messagebox.showerror("❌ 입력 오류", "종목명을 선택하세요.")
            return

        if not (pages.isdigit() and int(pages) > 0):
            messagebox.showerror("❌ 입력 오류", "페이지 수는 1 이상의 숫자여야 합니다.")
            return

        fetch_stock_data(stock_code, stock_name, int(pages))

    def on_keyrelease(event):
            root.after(100, delayed_filter)

    def delayed_filter():
        typed = stock_var.get().lower()
        filtered = [name for name in stock_dict.values() if typed in name.lower()]
        stock_combo['values'] = filtered
        if filtered:
            stock_combo.event_generate('<Down>')


    root = tk.Tk()
    root.title("네이버 주식 크롤러")

    # 종목명 검색 가능한 콤보박스
    tk.Label(root, text="📌 종목명 검색 및 선택").pack(pady=5)
    stock_var = tk.StringVar()
    stock_combo = ttk.Combobox(root, textvariable=stock_var, values=list(stock_dict.values()), width=30)
    stock_combo.set('')  # 기본 선택
    stock_combo.pack(pady=5)
    stock_combo.bind('<KeyRelease>', on_keyrelease)  # 검색 기능 추가

    tk.Label(root, text="📄 페이지 수 (예: 10)").pack(pady=5)
    page_entry = tk.Entry(root, width=20)
    page_entry.pack(pady=5)

    tk.Button(root, text="크롤링 시작", command=on_submit).pack(pady=10)

    root.mainloop()
    
start_gui()