# vcp-demo-watch-notify

《程式代理人應用實戰》第 6 章的示範儲存庫：用 GitHub Actions 定時抓一個**虛構**的社大公告頁
（本儲存庫 `gh-pages` 分支的 GitHub Pages：https://feis.github.io/vcp-demo-watch-notify/news/ ），有新公告才通知。

- `抓公告.py`：抓取、比對、通知（沒有設定 `DISCORD_WEBHOOK` 機密設定時只印出、不發送）
- `看過的公告.json`：看過的公告，由工作流程存回
- `抓取時間.json`：每次嘗試前記時間；失敗也存回，避免一小時內重複抓取
- `.github/workflows/watch.yml`：排程

不抓任何真實網站。

2026-09-27 曾觀察三小時沒有排程觸發，原因未確認。2026-10-22 補驗新版限速與失敗狀態；本輪工作流程固定只印通知、不連 Discord。驗證結束後停用排程。
