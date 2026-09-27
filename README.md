# vcp-demo-watch-notify

《駕馭程式代理人：從構想到成品》第 5 章的示範儲存庫：用 GitHub Actions 定時抓一個**虛構**的社大公告頁
（本儲存庫 `gh-pages` 分支的 GitHub Pages：https://feis.github.io/vcp-demo-watch-notify/news/ ），有新公告才通知。

- `抓公告.py`：抓取、比對、通知（沒有設定 `DISCORD_WEBHOOK` 機密設定時只印出、不發送）
- `看過的公告.json`：看過的公告，由工作流程存回
- `.github/workflows/watch.yml`：排程

不抓任何真實網站。
