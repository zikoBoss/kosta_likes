from flask import Flask, request, jsonify, send_file, render_template_string
import requests
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
main_key = os.getenv("MAIN_KEY", "CTX-TEAM")  # قراءة المفتاح من المتغيرات البيئية
executor = ThreadPoolExecutor(max_workers=20)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
}

IMAGE_CACHE = {}

# -------------------------------
#    جلب الصور مع التخزين المؤقت
# -------------------------------
def fetch_and_process_image(url, size=None):
    try:
        key = f"{url}_{size}"
        if key in IMAGE_CACHE:
            return IMAGE_CACHE[key].copy()

        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=7, verify=False)
        if resp.status_code != 200:
            print(f"[Warn] Can't load image {url}")
            return None

        img = Image.open(BytesIO(resp.content)).convert("RGBA")
        if size:
            img = img.resize(size)

        IMAGE_CACHE[key] = img
        return img.copy()
    except Exception as e:
        print(f"[Error] fetch image failed: {e}")
        return None

# -------------------------------
#    جلب معلومات اللاعب
# -------------------------------
def fetch_player_info(uid):
    try:
        url = f"http://45.67.15.190:50034/info={uid}"
        resp = requests.get(url, timeout=5, headers=DEFAULT_HEADERS, verify=False)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        print(f"[Error] fetch player info failed: {e}")
        return None

# -------------------------------
#    تحميل الخلفية الثابتة مرة واحدة
# -------------------------------
BACKGROUND = fetch_and_process_image(
    "https://iili.io/fIeZoDG.png",
    size=(1024, 1024)
)

if BACKGROUND is None:
    raise RuntimeError("❌ فشل تحميل صورة الخلفية")

# -------------------------------
#    الصفحة الرئيسية (HTML)
# -------------------------------
@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zakaria Outfit</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            body {
                min-height: 100vh;
                background: linear-gradient(145deg, #0a0000 0%, #1a0000 100%);
                position: relative;
                overflow-x: hidden;
                display: flex;
                justify-content: center;
                align-items: center;
                direction: rtl;
            }
            /* خلفية رقمية */
            body::before {
                content: "";
                position: absolute;
                width: 100%;
                height: 100%;
                background-image: 
                    radial-gradient(circle at 20% 30%, rgba(255, 0, 0, 0.1) 2px, transparent 2px),
                    radial-gradient(circle at 80% 70%, rgba(255, 0, 0, 0.1) 2px, transparent 2px),
                    radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                    radial-gradient(circle at 70% 20%, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
                background-size: 50px 50px, 50px 50px, 30px 30px, 30px 30px;
                pointer-events: none;
            }
            .container {
                background: rgba(10, 0, 0, 0.7);
                backdrop-filter: blur(10px);
                border: 2px solid #ff0000;
                border-radius: 30px;
                padding: 40px;
                width: 90%;
                max-width: 600px;
                box-shadow: 0 20px 40px rgba(255, 0, 0, 0.3);
                position: relative;
                z-index: 10;
            }
            h1 {
                color: #ff0000;
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
                letter-spacing: 2px;
            }
            .subtitle {
                color: #aaa;
                text-align: center;
                margin-bottom: 30px;
                font-size: 0.9em;
                border-bottom: 1px solid #ff0000;
                padding-bottom: 15px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                color: #ff5555;
                margin-bottom: 8px;
                font-weight: 600;
                font-size: 1.1em;
            }
            input {
                width: 100%;
                padding: 15px 20px;
                background: #1a0000;
                border: 2px solid #ff0000;
                border-radius: 50px;
                color: white;
                font-size: 1em;
                outline: none;
                transition: 0.3s;
            }
            input:focus {
                box-shadow: 0 0 15px #ff0000;
                background: #200000;
            }
            input::placeholder {
                color: #550000;
            }
            button {
                width: 100%;
                padding: 15px;
                background: linear-gradient(45deg, #ff0000, #990000);
                border: none;
                border-radius: 50px;
                color: black;
                font-weight: bold;
                font-size: 1.3em;
                cursor: pointer;
                transition: 0.3s;
                border: 1px solid #ff5555;
                margin-top: 10px;
                letter-spacing: 1px;
            }
            button:hover {
                transform: scale(1.02);
                box-shadow: 0 0 20px #ff0000;
                background: linear-gradient(45deg, #ff2222, #aa0000);
            }
            .result {
                margin-top: 30px;
                text-align: center;
                min-height: 300px;
                display: flex;
                justify-content: center;
                align-items: center;
                border-radius: 30px;
                background: rgba(0, 0, 0, 0.5);
                border: 1px dashed #ff0000;
                padding: 20px;
            }
            .result img {
                max-width: 100%;
                max-height: 600px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(255, 0, 0, 0.5);
            }
            .loading {
                color: #ff8888;
                font-size: 1.2em;
            }
            .error {
                color: #ff5555;
                font-size: 1.2em;
            }
            footer {
                margin-top: 20px;
                text-align: center;
                color: #660000;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ZAKARIA OUTFIT</h1>
            <div class="subtitle">أنشئ صورة الزي الخاص بلاعب فري فاير</div>
            
            <div class="form-group">
                <label>🔴 معرف اللاعب (UID)</label>
                <input type="text" id="uid" placeholder="أدخل UID ..." value="5106803793">
            </div>
            
            <div class="form-group">
                <label>⚫ مفتاح API</label>
                <input type="text" id="key" placeholder="المفتاح الرئيسي" value="CTX-TEAM">
            </div>
            
            <button onclick="generateOutfit()">توليد الصورة</button>
            
            <div class="result" id="result">
                <span class="loading">انتظر ...</span>
            </div>
            
            <footer>Zakaria Outfit • تصميم أحمر/أسود</footer>
        </div>

        <script>
            async function generateOutfit() {
                const uid = document.getElementById('uid').value.trim();
                const key = document.getElementById('key').value.trim();
                const resultDiv = document.getElementById('result');
                
                if (!uid || !key) {
                    resultDiv.innerHTML = '<span class="error">❌ الرجاء إدخال UID والمفتاح</span>';
                    return;
                }
                
                resultDiv.innerHTML = '<span class="loading">⏳ جاري تحميل الصورة ...</span>';
                
                try {
                    const response = await fetch(`/outfit-image?uid=${encodeURIComponent(uid)}&key=${encodeURIComponent(key)}`);
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        resultDiv.innerHTML = `<span class="error">❌ خطأ: ${errorText}</span>`;
                        return;
                    }
                    
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    resultDiv.innerHTML = `<img src="${url}" alt="Outfit Image">`;
                } catch (error) {
                    resultDiv.innerHTML = `<span class="error">❌ فشل الاتصال: ${error.message}</span>`;
                }
            }
            
            // تنفيذ تلقائي عند تحميل الصفحة (اختياري)
            window.onload = function() {
                // يمكنك تفعيل هذا إذا أردت تحميل صورة افتراضية
                // generateOutfit();
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

# -------------------------------
#    مسار إنشاء الصورة (نفس الكود القديم)
# -------------------------------
@app.route('/outfit-image', methods=['GET'])
def outfit_image():
    uid = request.args.get("uid")
    key = request.args.get("key")

    if not uid:
        return jsonify({"error": "Missing UID"}), 400
    if key != main_key:
        return jsonify({"error": "Invalid API key"}), 403

    data = fetch_player_info(uid)
    if not data:
        return jsonify({"error": "Failed to fetch player info"}), 500

    background_image = BACKGROUND.copy()

    equipped = data.get("profileInfo", {}).get("equipedSkills", [])
    avatar_id = data.get("profileInfo", {}).get("avatarId", 102000005)
    weapon_ids = data.get("basicInfo", {}).get("weaponSkinShows", [])
    weapon_id = weapon_ids[0] if weapon_ids else None

    required_starts = ["214", "211", "211", "203", "204", "205", "203"]
    fallback_ids = ["214000000", "211000000", "211000000", "203000000",
                    "204000000", "205000000", "203000000"]

    used_ids = set()
    outfit_tasks = []

    def get_outfit(idx, code):
        match = None
        for oid in equipped:
            if str(oid).startswith(code) and oid not in used_ids:
                match = oid
                used_ids.add(oid)
                break

        if match is None:
            match = fallback_ids[idx]

        url = f"https://iconapi.wasmer.app/{match}"
        return fetch_and_process_image(url, size=(170, 170))

    for i, c in enumerate(required_starts):
        outfit_tasks.append(executor.submit(get_outfit, i, c))

    positions = [
        {'x': 130, 'y': 138, 'w': 170, 'h': 170},
        {'x': 727, 'y': 180, 'w': 170, 'h': 170},
        {'x': 820, 'y': 380, 'w': 170, 'h': 170},
        {'x': 45,  'y': 345, 'w': 170, 'h': 170},
        {'x': 55,  'y': 590, 'w': 170, 'h': 170},
        {'x': 180, 'y': 760, 'w': 170, 'h': 170},
        {'x': 714, 'y': 730, 'w': 170, 'h': 170},
    ]

    for i, t in enumerate(outfit_tasks):
        outfit = t.result()
        if outfit:
            p = positions[i]
            resized = outfit.resize((p["w"], p["h"]))
            background_image.paste(resized, (p["x"], p["y"]), resized)

    # الصورة الرمزية (avatar)
    avatar_url = f"https://raw.githubusercontent.com/saarthak703/character-api-danger/main/pngs/{avatar_id}.png"
    avatar = fetch_and_process_image(avatar_url, size=(650, 780))
    if avatar:
        cx = (1024 - 650) // 2
        background_image.paste(avatar, (cx, 145), avatar)

    # السلاح
    if weapon_id:
        w_url = f"https://iconapi.wasmer.app/{weapon_id}"
        weapon = fetch_and_process_image(w_url, size=(330, 200))
        if weapon:
            background_image.paste(weapon, (670, 564), weapon)

    img_io = BytesIO()
    background_image.save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)