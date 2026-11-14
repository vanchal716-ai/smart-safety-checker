from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def check_smart(url, phone):
    score = 100
    reasons = []

    url = url.lower()

    # 1. No HTTPS
    if not url.startswith("https://"):
        score -= 30
        reasons.append("⚠️ No HTTPS - Not secure")

    # 2. Scam keywords
    scam_words = ["lottery", "prize", "winner", "free", "urgent", "claim", "gift", "bonus", "win"]
    for w in scam_words:
        if w in url:
            score -= 25
            reasons.append(f"🚨 Scam word found: '{w}'")
            break

    # 3. IP address instead of domain
    if re.search(r"\d+\.\d+\.\d+\.\d+", url):
        score -= 30
        reasons.append("🚨 Link uses IP address, not real website")

    # 4. Too long URL
    if len(url) > 75:
        score -= 15
        reasons.append("⚠️ Suspiciously long URL")

    # 5. Too many dots or @ symbol
    if url.count(".") > 4 or "@" in url:
        score -= 20
        reasons.append("⚠️ Fake URL pattern detected")

    # 6. Phone check
    if phone:
        if not (phone.isdigit() and len(phone)==10):
            score -= 20
            reasons.append("❌ Invalid phone format")

    if score < 0: score = 0
    if score >= 80:
        status = "✅ SAFE"
    elif score >= 50:
        status = "⚠️ SUSPICIOUS"
    else:
        status = "❌ SCAM / UNSAFE"
    
    if not reasons:
        reasons.append("Looks clean and safe")

    return score, status, reasons

@app.route('/')
def home():
    return """
<html>
<head><title>Smart Safety Checker</title></head>
<body style="font-family:Arial; text-align:center; padding:40px; background:#eef2ff;">
<h1 style="color:#2c3e50;">🛡️ SMART SAFETY CHECKER</h1>
<p>Your Paper to Real Website - AI Version</p>
<div style="background:white; padding:30px; border-radius:15px; max-width:600px; margin:auto; box-shadow:0 4px 20px rgba(0,0,0,0.1);">

<h3>Check Link + Phone</h3>
<input id="link" placeholder="Enter https://google.com" style="width:80%; padding:12px; border-radius:8px; border:1px solid #ccc;">
<br><br>
<input id="phone" placeholder="Enter 10 digit number (optional)" style="width:80%; padding:12px; border-radius:8px; border:1px solid #ccc;">
<br><br>
<button onclick="checkSmart()" style="padding:12px 30px; background:#4f46e5; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">Check Smart AI</button>

<div id="result" style="margin-top:25px; text-align:left; background:#f9fafb; padding:20px; border-radius:10px; display:none;"></div>

</div>
<script>
async function checkSmart(){
 let link = document.getElementById('link').value;
 let phone = document.getElementById('phone').value;
 if(!link){ alert('Enter link'); return; }
 
 let resBox = document.getElementById('result');
 resBox.style.display='block';
 resBox.innerHTML='Checking with AI...';

 let resp = await fetch('/check', {
   method:'POST',
   headers:{'Content-Type':'application/json'},
   body: JSON.stringify({url:link, phone:phone})
 });
 let data = await resp.json();
 
 resBox.innerHTML = `<h2>${data.status} - ${data.score}/100</h2><hr>` + data.reasons.map(r=>`<p>${r}</p>`).join('');
}
</script>
</body>
</html>
"""

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    url = data.get('url','')
    phone = data.get('phone','')
    score, status, reasons = check_smart(url, phone)
    return jsonify({"score":score, "status":status, "reasons":reasons})

if __name__ == '__main__':
    import os
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)