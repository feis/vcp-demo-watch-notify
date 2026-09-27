"""青山社大公告小幫手：抓「最新消息」，跟上次看過的比，有新公告才傳到 Discord。

只用 Python 標準函式庫，不必另外安裝套件。

執行：python 抓公告.py（macOS 可能要打 python3）

環境變數：
  DISCORD_WEBHOOK  Discord 網路鉤子網址。沒設定時只印出、不發送。
                   這串網址等於密碼：不要寫進任何檔案，GitHub 上放在機密設定。
  NEWS_URL         要抓的公告頁（選填，測試時換成自己的示範網站）。
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

公告網址 = os.environ.get("NEWS_URL") or "https://qingshan-cc.example.org/news"
公告格子 = "news-item"  # 每一則公告標題所在格子的 class；網站改版時改這裡
紀錄檔 = Path(__file__).resolve().parent / "看過的公告.json"
身分 = "qingshan-news-watcher/1.0 (personal, hourly)"  # 告訴對方是誰在抓
訊息上限 = 2000  # Discord 一則訊息最多 2000 字


def 抓網頁(網址):
    請求 = urllib.request.Request(網址, headers={"User-Agent": 身分})
    with urllib.request.urlopen(請求, timeout=30) as 回應:
        編碼 = 回應.headers.get_content_charset() or "utf-8"
        return 回應.read().decode(編碼, errors="replace")


def 允許抓取(網址):
    """讀網域最上層的 robots.txt，看這一頁准不准抓。沒有 robots.txt 就當作沒有限制。"""
    規則 = urllib.robotparser.RobotFileParser()
    try:
        規則.parse(抓網頁(urljoin(網址, "/robots.txt")).splitlines())
    except urllib.error.HTTPError as 錯誤:
        if 錯誤.code in (401, 403):
            return False
        return True  # 404 等：沒有 robots.txt
    return 規則.can_fetch(身分, 網址)


class 標題挑選器(HTMLParser):
    """把 class 含有「公告格子」的元素裡的文字挑出來，一則一行。"""

    def __init__(self, 格子):
        super().__init__()
        self.格子 = 格子
        self.深度 = 0  # 0 表示不在公告格子裡
        self.目前 = []
        self.標題 = []

    def handle_starttag(self, tag, attrs):
        if self.深度:
            self.深度 += 1
        elif self.格子 in (dict(attrs).get("class") or "").split():
            self.深度 = 1
            self.目前 = []

    def handle_endtag(self, tag):
        if self.深度:
            self.深度 -= 1
            if self.深度 == 0:
                文字 = " ".join("".join(self.目前).split())
                if 文字:
                    self.標題.append(文字)

    def handle_data(self, data):
        if self.深度:
            self.目前.append(data)


def 挑出公告(html):
    挑選器 = 標題挑選器(公告格子)
    挑選器.feed(html)
    return 挑選器.標題


def 讀紀錄():
    if not 紀錄檔.exists():
        return None
    return json.loads(紀錄檔.read_text(encoding="utf-8"))["公告"]


def 存紀錄(公告):
    資料 = {"網址": 公告網址, "公告": 公告}
    紀錄檔.write_text(json.dumps(資料, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def 切成多則(開頭, 各行):
    """Discord 一則最多 2000 字；太長就拆成好幾則，不從一行中間切斷。"""
    訊息 = []
    目前 = 開頭
    for 行 in 各行:
        行 = 行[: 訊息上限 - 10]  # 單一行本身就超長時截短
        if len(目前) + 1 + len(行) > 訊息上限:
            訊息.append(目前)
            目前 = "（續）"
        目前 += "\n" + 行
    訊息.append(目前)
    return 訊息


def 發通知(內容):
    網路鉤子 = os.environ.get("DISCORD_WEBHOOK", "").strip()
    if not 網路鉤子:
        print("［沒有設定 DISCORD_WEBHOOK，只印出不發送］")
        print(內容)
        return
    資料 = json.dumps({"content": 內容}).encode("utf-8")
    for 第幾次 in range(3):
        請求 = urllib.request.Request(
            網路鉤子,
            data=資料,
            method="POST",
            # 不帶 User-Agent 時，Discord 前面的防護可能直接拒絕 Python 預設的身分
            headers={"Content-Type": "application/json", "User-Agent": 身分},
        )
        try:
            with urllib.request.urlopen(請求, timeout=30):
                return
        except urllib.error.HTTPError as 錯誤:
            if 錯誤.code == 429 and 第幾次 < 2:  # 發太快，照對方說的秒數等一下再送
                等 = json.loads(錯誤.read() or b"{}").get("retry_after", 1)
                time.sleep(float(等))
                continue
            raise SystemExit(f"Discord 拒絕了這則通知：HTTP {錯誤.code}。網路鉤子是不是被刪了？")


def main():
    if not 允許抓取(公告網址):
        raise SystemExit(f"robots.txt 不允許抓 {公告網址}，停手。")

    try:
        公告 = 挑出公告(抓網頁(公告網址))
    except (urllib.error.URLError, TimeoutError) as 錯誤:
        raise SystemExit(f"打不開公告頁：{錯誤}")
    print(f"抓到 {len(公告)} 則公告")

    if not 公告:
        # 一則都沒有，多半是網頁改版、格子換了名字。出聲，而且不要蓋掉舊紀錄。
        發通知(f"抓不到公告，網頁可能改版了：{公告網址}")
        return

    看過的 = 讀紀錄()
    if 看過的 is None:
        存紀錄(公告)
        print(f"第一次執行：找不到 {紀錄檔.name}，先記下 {len(公告)} 則，不通知")
        return

    新的 = [則 for 則 in 公告 if 則 not in 看過的]
    print(f"新公告 {len(新的)} 則")
    for 則 in 切成多則("青山社大有新公告：", 新的) if 新的 else []:
        發通知(則)

    if 公告 != 看過的:
        存紀錄(公告)  # 通知都送出去之後才存，送失敗下次會再試


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")  # 終端機不支援的字不要讓程式當掉
    main()
