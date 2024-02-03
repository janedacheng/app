from flask_ngrok import run_with_ngrok
from flask import Flask, request

import requests
import pandas as pd
from flask import Flask, request, abort



# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


app = Flask(__name__)

# 用你的 Channel access token 和 Channel secret 替換下面的值
line_bot_api = LineBotApi('md/F4owNkiFhXiVOYu09vtODPRT3jt93sN3gQg30n7KAInTLU9q3oA8GIDBZ8v00b+RJ+uXBYbwmucYGJbHd0uATQRopvzfR4Yg8MHRrE/pzsdnuHnB13+j2b/QEA/BvQTdME1dCyyhJWaZk4ebkzAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d6ffc16bb68c2f37522de7533921d202')

def get_stock_price(stock_id):
    # 你的爬取股票价格代码
    res = requests.get(f"https://tw.stock.yahoo.com/_td-stock/api/resource/FinanceChartService.ApacLibraCharts;autoRefresh=1660056015780;symbols=%5B%22"+stock_id+".TW%22%5D;type=tick?bkt=&device=desktop&ecma=modern&feature=ecmaModern%2CuseNewQuoteTabColor&intl=tw&lang=zh-Hant-TW&partner=none&prid=0oq7ot9hf4ro4&region=TW&site=finance&tz=Asia%2FTaipei&ver=1.2.1452&returnMeta=true")# 检查响应状态码
    if res.status_code != 200:
        print(f"请求失败，状态码：{res.status_code}")
        print("响应内容：", res.text)
        return "请求失败"

    try:
        jd = res.json()["data"]
        # ... 余下的处理 ...
    except ValueError:
        # JSON 解析失败
        print("JSON 解析失败")
        print("响应内容：", res.text)
        return "解析失败"
    x=res.json()
    jd=res.json()["data"]
    open=jd[0]["chart"]["indicators"]["quote"][0]["open"]


    close=jd[0]["chart"]["indicators"]["quote"][0]["close"]
    volume=jd[0]["chart"]["indicators"]["quote"][0]["volume"]
    timestamp=jd[0]["chart"]["timestamp"]

    df=pd.DataFrame({"timestamp":timestamp,"open":open,"close":close,"volume":volume})
    price = str(close[-1])  # 获取最后一个收盘价
    return price



@app.route("/callback", methods=['POST'])
def callback():
    # 從請求中獲取 X-Line-Signature 頭部的值
    signature = request.headers['X-Line-Signature']

    # 從請求體獲取文本
    body = request.get_data(as_text=True)

    # 處理 webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

    





# 處理傳送到 /callback 的訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    price = get_stock_price(user_message)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"{user_message} 的收盤價是: {price}")
    )

if __name__ == "__main__":
  run_with_ngrok(app)           # 串連 ngrok 服務
  app.run()