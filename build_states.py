"""產生 mock-site 的三種狀態，並可切換 /news/ 目前顯示哪一種。

用法：
  python build_states.py            # 重新產生 states/*.html
  python build_states.py new        # 把「有一則新公告」放到 news/index.html

狀態：none（沒有新公告）、new（有一則新公告）、redesign（改版後結構變了）
"""
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

舊公告 = [
    ("09/18", "中秋節停課一天"),
    ("09/10", "二樓教室搬遷公告"),
    ("09/03", "秋季班課程手冊上架"),
    ("08/27", "颱風停課補課日期"),
    ("08/20", "志工招募說明會"),
    ("08/13", "八月份場地維修公告"),
    ("08/06", "夏季班成果展照片"),
    ("07/30", "暑假服務台時間調整"),
    ("07/23", "春季班學員滿意度調查結果"),
]
新公告 = ("09/25", "秋季班報名 10/1 上午 9 點開放")
改版後新增 = [("11/20", "冬季班報名 12/1 開放"), ("11/12", "網站改版說明")]

頁首 = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>最新消息｜青山社區大學（虛構示範網站）</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<header><a href="../">青山社區大學</a><span class="demo">虛構示範網站，僅供課程練習</span></header>
<main>
<h1>最新消息</h1>
"""
頁尾 = """</main>
<footer><a href="../terms.html">使用條款</a>　青山社區大學（虛構）</footer>
</body>
</html>
"""


def 舊版(items):
    rows = "\n".join(
        f'  <li class="news-item">\n    <span class="date">{d}</span>\n    {t}</li>' for d, t in items
    )
    return 頁首 + f'<ul class="news-list">\n{rows}\n</ul>\n' + 頁尾


def 新版(items):
    rows = "\n".join(
        f'  <article class="post">\n    <div class="post-title">\n'
        f'      <span class="date">{d}</span>\n      {t}</div>\n  </article>'
        for d, t in items
    )
    return 頁首 + f'<section class="posts">\n{rows}\n</section>\n' + 頁尾


def 產生全部():
    states = {
        "none": 舊版(舊公告),
        "new": 舊版([新公告] + 舊公告),
        # 改版後只列最新 10 則：多了兩則，最舊的兩則掉出畫面
        "redesign": 新版(改版後新增 + [新公告] + 舊公告[:7]),
    }
    for name, html in states.items():
        (HERE / "states" / f"{name}.html").write_text(html, encoding="utf-8", newline="\n")
    return states


def 切換(name):
    src = HERE / "states" / f"{name}.html"
    if not src.exists():
        sys.exit(f"沒有這個狀態：{name}（可用 none／new／redesign）")
    shutil.copyfile(src, HERE / "news" / "index.html")
    print(f"/news/ 現在是：{name}")


if __name__ == "__main__":
    產生全部()
    if len(sys.argv) > 1:
        切換(sys.argv[1])
