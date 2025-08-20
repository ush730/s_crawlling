import requests
from bs4 import BeautifulSoup
import os
import tkinter as tk
from tkinter import ttk, messagebox

CHO_TABLE = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ',
    'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ',
    'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ',
    'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

# === 설정: 파일 경로 ===
BASE_DIR = r'C:\Workspace\crawlling'   # 윈도우 경로는 r'' 또는 \\ 사용
STOCKS_FILE = os.path.join(BASE_DIR, 'stocks.txt')

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

def load_stock_dict_from_file(path):
    """
    stocks.txt에서 '코드:종목명' 형식을 읽어 dict로 변환
    공백 허용, # 으로 시작하는 라인은 주석 처리
    """
    d = {}
    if not os.path.exists(path):
        return d

    with open(path, encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            # 콜론(:) 기준으로 1번만 분리 (좌: 코드, 우: 종목명)
            if ':' in line:
                code, name = line.split(':', 1)
            elif ',' in line:  # 콜론 대신 쉼표를 쓴 경우도 느슨히 허용
                code, name = line.split(',', 1)
            else:
                continue
            code = code.strip()
            name = name.strip()
            # 6자리 숫자 코드만 수용
            if len(code) == 6 and code.isdigit() and name:
                d[code] = name
    return d

def fetch_stock_data(stock_code, stock_name, page_count):
    # 저장 디렉토리 준비
    os.makedirs(BASE_DIR, exist_ok=True)

    save_dir = BASE_DIR
    hwv_open_path = os.path.join(save_dir, f'{stock_code} 시가.txt')
    hwv_close_path = os.path.join(save_dir, f'{stock_code} 종가.txt')

    # 시가 저장
    with open(hwv_open_path, 'w', encoding='utf-8-sig') as f:
        f.write(stock_name + "\n")  # 첫 줄에 종목명 삽입
        for page in range(1, page_count + 1):
            url = f'https://finance.naver.com/item/sise_day.naver?code={stock_code}&page={page}'
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/73.0.3683.86 Safari/537.36')
            }
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('table.type2 tr')

            for row in rows:
                cols = row.select('td')
                if len(cols) > 3:
                    open_price = cols[3].text.strip()   # 시가 (4번째 칸)
                    if open_price:
                        f.write(f"{open_price}\n")

    # 종가 저장
    with open(hwv_close_path, 'w', encoding='utf-8-sig') as f:
        f.write(stock_name + "\n")  # 첫 줄에 종목명 삽입
        for page in range(1, page_count + 1):
            url = f'https://finance.naver.com/item/sise_day.naver?code={stock_code}&page={page}'
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/73.0.3683.86 Safari/537.36')
            }
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.select('table.type2 tr')

            for row in rows:
                cols = row.select('td')
                if len(cols) > 1:
                    close_price = cols[1].text.strip()  # 종가 (2번째 칸)
                    if close_price:
                        f.write(f"{close_price}\n")

    messagebox.showinfo("✅ 완료", f"[{stock_name}] {page_count}0일차 크롤링 완료!\n\n"
                                   f"시가: {hwv_open_path}\n종가: {hwv_close_path}")

def start_gui():
    root = tk.Tk()
    root.title("네이버 주식 크롤러")

    # 파일에서 종목 사전 로드
    stock_dict = load_stock_dict_from_file(STOCKS_FILE)
    if not stock_dict:
        messagebox.showerror(
            "종목 목록 없음",
            f"종목 목록 파일이 없거나 비어 있습니다.\n\n"
            f"경로: {STOCKS_FILE}\n"
            f"예시:\n042700: 한미반도체\n489790: 한화비전\n022100: 포스코DX\n055550: 신한지주"
        )
        root.destroy()
        return

    # 역매핑 (종목명 → 코드)
    name_to_code = {v: k for k, v in stock_dict.items()}

    def on_submit():
        stock_name = stock_var.get().strip()
        stock_code = name_to_code.get(stock_name)
        pages = page_entry.get().strip()

        if not stock_code:
            messagebox.showerror("❌ 입력 오류", "종목명을 선택(또는 정확히 입력)하세요.")
            return
        if not (pages.isdigit() and int(pages) > 0):
            messagebox.showerror("❌ 입력 오류", "페이지 수는 1 이상의 숫자여야 합니다.")
            return

        fetch_stock_data(stock_code, stock_name, int(pages))

    def on_keyrelease(event):
        # 한글 조합 문제 회피: 약간 지연 후 필터
        root.after(120, delayed_filter)

    def delayed_filter():
        typed = stock_var.get().lower()
        all_names = list(stock_dict.values())
        if not typed:
            stock_combo['values'] = all_names
            return
        filtered = [name for name in all_names if typed in name.lower()]
        stock_combo['values'] = filtered
        if filtered:
            stock_combo.event_generate('<Down>')

    # 종목명 검색 가능한 콤보박스
    tk.Label(root, text="📌 종목명 선택").pack(pady=5)
    stock_var = tk.StringVar()
    stock_combo = ttk.Combobox(root, textvariable=stock_var,
                               values=list(stock_dict.values()), width=30)
    stock_combo.set('')  # 기본 선택 없음
    stock_combo.pack(pady=5)
    stock_combo.bind('<KeyRelease>', on_keyrelease)

    tk.Label(root, text="📄 페이지 수 (예: 10)").pack(pady=5)
    page_entry = tk.Entry(root, width=20)
    page_entry.pack(pady=5)

    tk.Button(root, text="크롤링 시작", command=on_submit).pack(pady=10)

    root.mainloop()

start_gui()
