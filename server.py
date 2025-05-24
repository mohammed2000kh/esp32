from flask import Flask, request, jsonify
import os
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

# تحميل بيانات حساب الخدمة من متغير بيئة
SERVICE_ACCOUNT_INFO = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES
)

# توليد Access Token
def get_access_token():
    credentials.refresh(Request())
    return credentials.token

@app.route('/')
def index():
    return '🚀 FCM Server is running'

# إشعارات عادية (flutter_local_notifications)
@app.route('/notify', methods=['POST'])
def send_standard_notification():
    data = request.get_json()
    token = data['token']
    title = data.get('title', '📢 إشعار')
    body = data.get('body', 'لديك تنبيه جديد')
    extra_data = data.get("data", {})

    access_token = get_access_token()

    message = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            },
            "data": extra_data,
            "android": {
                "priority": "high",
                "notification": {
                    "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    "channel_id": "alarm_channel"
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

# إشعارات Data-only لتفعيل MyFirebaseMessagingService وفتح AlarmActivity
@app.route('/notify-alarm', methods=['POST'])
def send_alarm_notification():
    data = request.get_json()
    token = data['token']
    title = data.get('title', '🚨 إنذار!')
    body = data.get('body', 'تم رصد حركة')
    extra_data = data.get("data", {})

    # نضيف title و body داخل data (وليس notification!)
    data_payload = {
        "type": "alarm",
        "title": title,
        "body": body,
        **extra_data
    }

    access_token = get_access_token()

    message = {
        "message": {
            "token": token,
            "data": data_payload,
            "android": {
    "priority": "high",
    "notification": {
        "click_action": "ALARM_ACTION",
        "channel_id": "alarm_channel",
        "full_screen_intent": True,
        "priority": "PRIORITY_MAX",
        "visibility": "PUBLIC",
        "sound": "alarm"
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
