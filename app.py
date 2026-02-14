from flask import Flask, request, render_template_string
import requests
import base64
import os

app = Flask(__name__)

# اسم الفريق
TEAM_NAME = "JA FAMILY"

# فك تشفير رابط API
def get_api_url(uid, server_name):
    try:
        encoded_url = "aHR0cHM6Ly9kdXJhbnRvLWxpa2UtcGVhcmwudmVyY2VsLmFwcC9saWtlP3VpZD17dWlkfSZzZXJ2ZXJfbmFtZT17c2VydmVyX25hbWV9"
        decoded_url = base64.b64decode(encoded_url).decode()
        return decoded_url.format(uid=uid, server_name=server_name)
    except:
        return None

# أسماء المناطق
regions = {
    'me': {'ar': 'الشرق الأوسط', 'en': 'Middle East'},
    'eu': {'ar': 'أوروبا', 'en': 'Europe'},
    'us': {'ar': 'أمريكا الشمالية', 'en': 'North America'},
    'in': {'ar': 'الهند', 'en': 'India'},
    'br': {'ar': 'البرازيل', 'en': 'Brazil'},
    'id': {'ar': 'إندونيسيا', 'en': 'Indonesia'},
    'tr': {'ar': 'تركيا', 'en': 'Turkey'},
    'th': {'ar': 'تايلاند', 'en': 'Thailand'}
}

# قالب HTML (كما هو دون تغيير)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KOSTA LIKES</title>
    <style>
        body {
            background-color: black;
            color: red;
            font-family: 'Arial', sans-serif;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: #1a1a1a;
            padding: 30px;
            border-radius: 15px;
            border: 2px solid red;
            box-shadow: 0 0 20px rgba(255,0,0,0.3);
        }
        h1 {
            color: red;
            text-shadow: 0 0 10px red;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        h2 {
            color: white;
            margin-bottom: 30px;
        }
        label {
            display: block;
            margin: 15px 0 5px;
            color: red;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            padding: 12px;
            background: black;
            border: 2px solid red;
            color: red;
            border-radius: 8px;
            font-size: 1.1em;
            margin-bottom: 15px;
            box-sizing: border-box;
        }
        input:focus, select:focus {
            outline: none;
            border-color: white;
        }
        button {
            background: red;
            color: black;
            border: none;
            padding: 15px 30px;
            font-size: 1.3em;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            transition: 0.3s;
            margin-top: 10px;
            width: 100%;
        }
        button:hover {
            background: #cc0000;
            box-shadow: 0 0 15px red;
            transform: scale(1.02);
        }
        .result-box {
            margin-top: 30px;
            padding: 20px;
            background: black;
            border: 2px solid red;
            border-radius: 10px;
            color: red;
            text-align: right;
        }
        .result-box pre {
            font-family: 'Courier New', monospace;
            color: white;
            background: #111;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 5px solid red;
        }
        .footer {
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }
        .lang-switch {
            margin-bottom: 20px;
        }
        .lang-switch a {
            color: red;
            text-decoration: none;
            margin: 0 10px;
            font-weight: bold;
        }
        .lang-switch a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>KOSTA LIKES</h1>
        <h2>{{ team_name }}</h2>

        <div class="lang-switch">
            <a href="?lang=ar">🇸🇦 العربية</a> | <a href="?lang=en">🇺🇸 English</a>
        </div>

        {% if error %}
        <div style="color: red; background: #330000; padding: 10px; border-radius: 5px; margin-bottom: 20px;">
            {{ error }}
        </div>
        {% endif %}

        <form method="POST" action="/send_likes">
            <input type="hidden" name="lang" value="{{ lang }}">

            <label>{% if lang == 'ar' %}🆔 UID الخاص بك{% else %}🆔 Your UID{% endif %}</label>
            <input type="text" name="uid" placeholder="مثال: 13708567247" required>

            <label>{% if lang == 'ar' %}🌍 المنطقة{% else %}🌍 Region{% endif %}</label>
            <select name="server">
                {% for code, names in regions.items() %}
                <option value="{{ code }}">{{ names[lang] }}</option>
                {% endfor %}
            </select>

            <button type="submit">
                {% if lang == 'ar' %}📥 إرسال لايكات{% else %}📥 Send Likes{% endif %}
            </button>
        </form>

        {% if result %}
        <div class="result-box">
            <h3 style="color: red; margin-top: 0;">
                {% if lang == 'ar' %}📊 النتيجة{% else %}📊 Result{% endif %}
            </h3>
            <pre>{{ result }}</pre>
        </div>
        {% endif %}

        <div class="footer">
            {{ team_name }} - KOSTA LIKES
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    lang = request.args.get('lang', 'ar')
    if lang not in ['ar', 'en']:
        lang = 'ar'
    return render_template_string(HTML_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang, error=None, result=None)

@app.route('/send_likes', methods=['POST'])
def send_likes():
    uid = request.form.get('uid', '').strip()
    server = request.form.get('server', 'me')
    lang = request.form.get('lang', 'ar')

    if not uid:
        return render_template_string(HTML_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error="⚠️ الرجاء إدخال UID" if lang=='ar' else "⚠️ Please enter UID",
                                       result=None)

    api_url = get_api_url(uid, server)
    if not api_url:
        return render_template_string(HTML_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error="❌ خطأ في النظام" if lang=='ar' else "❌ System error",
                                       result=None)

    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()

        likes_given = data.get('LikesGivenByAPI', 0)
        likes_after = data.get('LikesafterCommand', 0)
        likes_before = data.get('LikesbeforeCommand', 0)
        player_nickname = data.get('PlayerNickname', 'غير معروف' if lang=='ar' else 'Unknown')
        status = data.get('status', 0)

        if lang == 'ar':
            status_icons = {0: "❌ فشل", 1: "⚠️ محدود", 2: "✅ ناجح", 3: "🔒 مغلق"}
            region_name = regions.get(server, {}).get('ar', server.upper())
        else:
            status_icons = {0: "❌ Failed", 1: "⚠️ Limited", 2: "✅ Success", 3: "🔒 Locked"}
            region_name = regions.get(server, {}).get('en', server.upper())

        result_text = f"""
🎮 اللاعب: {player_nickname}
🔢 UID: {uid}
🌍 المنطقة: {region_name}

📊 اللايكات:
   قبل: {likes_before} 👍
   بعد: {likes_after} 👍
   أضيف: {likes_given} 🆕

📈 الحالة: {status_icons.get(status, '❓')}
"""
        if likes_given > 0:
            result_text += "\n✅ تمت الإضافة بنجاح"
        elif status == 2:
            result_text += "\nℹ️ الحد الأقصى متوفر"
        else:
            result_text += "\n❌ لم تتم الإضافة"

        return render_template_string(HTML_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error=None, result=result_text)

    except Exception as e:
        return render_template_string(HTML_TEMPLATE, team_name=TEAM_NAME, regions=regions, lang=lang,
                                       error="❌ فشل الاتصال بالخادم" if lang=='ar' else "❌ Connection failed",
                                       result=None)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)