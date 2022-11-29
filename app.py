from flask import Flask
from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, PostbackEvent, FollowEvent, UnfollowEvent, TextMessage
from urllib.parse import parse_qs
import global_variable.globals as g

import controller.reply_controller as reply_controller
import controller.user_controller as user_controller
import controller.action_controller as action_controller
import controller.sheet_controller as sheet_controller
import controller.user_follow_controller as user_follow_controller
import controller.alloc_result_controller as alloc_result_controller

line_bot_api = LineBotApi(g.GlobalVar.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(g.GlobalVar.CHANNEL_SECRET)
line_bot_api.set_webhook_endpoint(g.GlobalVar.WEBHOOK_URL)

app = Flask(__name__)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handler_message(event):
    """文字訊息設定"""
    command = event.message.text  # 取得文字訊息
    if not command.startswith('@'):
        return

    user_id = user_controller.user_id(event.source.user_id)

    if command.startswith('@使用說明'):
        action_controller.action_illustrate(line_bot_api, event)
    elif command.startswith('@關於我們'):
        action_controller.action_about_us(line_bot_api, event)
    elif user_controller.read_risk_free_rate(user_id):
        """遮罩，阻止尚未做問卷的用戶"""
        if command.startswith('@開始計算'):
            action_controller.action_calculate(line_bot_api, event)
        elif command.startswith('@關注清單'):
            action_controller.action_user_follow(line_bot_api, event, command)
        elif command.startswith('@風險設定'):
            action_controller.set_risk_and_bound(line_bot_api, event, command)
        elif command.startswith('@模型選擇'):
            action_controller.action_model_type(line_bot_api, event)
    else:
        message = []
        message += reply_controller.message_sheet_undone()
        message += action_controller.action_sheet_skip(user_id)
        reply_controller.reply_message(line_bot_api, event, message)


@handler.add(PostbackEvent)
def handler_postback(event):
    """回呼訊息設定"""
    postback = parse_qs(event.postback.data)
    user_id = user_controller.user_id(event.source.user_id)

    if postback["action"][0] == "sheet":
        message = []
        user_controller.update_update_time(user_id)
        if not user_controller.read_risk_free_rate(user_id):
            if "option" not in postback:
                message += action_controller.action_sheet_skip(user_id)

            elif postback["option"][0] == "skip":
                message += action_controller.action_sheet_skip(user_id, postback)

            elif postback["option"][0] == "continue":
                message += action_controller.action_sheet_answer(user_id, postback)
        else:
            message += reply_controller.message_sheet_complete()
        reply_controller.reply_message(line_bot_api, event, message)

    elif postback["action"][0] == "model":
        action_controller.action_model_type(line_bot_api, event, postback)
    elif postback["action"][0] == "illustrate":
        action_controller.action_illustrate(line_bot_api, event, postback)


@handler.add(FollowEvent)
def handler_follow(event):
    """使用者加入好友設定"""
    user_controller.create(event.source.user_id)
    user_id = user_controller.user_id(event.source.user_id)
    sheet_controller.create(user_id, g.GlobalVar.QUESTION_NUM)
    action_controller.action_welcome(line_bot_api, event)
    alloc_result_controller.create(user_id)


@handler.add(UnfollowEvent)
def handler_unfollow(event):
    """使用者刪除好友(封鎖)設定"""
    user_id = user_controller.user_id(event.source.user_id)
    user_controller.delete(user_id)
    sheet_controller.delete(user_id)
    user_follow_controller.delete(user_id)
    alloc_result_controller.delete(user_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
