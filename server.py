from flask import Flask, request, jsonify
import os
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

app = Flask(__name__)

# 👇 لازم يكون قبل الاستخدام
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

# 👇 تحميل بيانات الخدمة من متغير البيئة
# ✅ أولاً: عرف SCOPES

# ✅ ثم: حمّل بيانات الحساب من متغير البيئة
SERVICE_ACCOUNT_INFO = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES
)

# ✅ دالة توليد Access Token
def get_access_token():
    credentials.refresh(Request())
    return credentials.token
@app.route('/')
def index():
    return 'FCM Server is running ✅'

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.get_json()
    token = data['token']
    title = data.get('title', '🚨 تنبيه')
    body = data.get('body', 'تم اكتشاف حركة')

    access_token = get_access_token()

    message = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": data.get("data", {}),
            "android": {
                "notification": {
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    "channel_id": "high_importance_channel"
                }
            }
        }
    }

    response = requests.post(
        "https://fcm.googleapis.com/v1/projects/alarm-db751/messages:send",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        data=json.dumps(message)
    )

    return jsonify({"status": response.status_code, "response": response.text})
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
