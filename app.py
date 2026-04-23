import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- רשימות ניהוליות ---
DEPARTMENTS = ["פלסטיקה", "ביוטי", "דקורציה", "עונה", "כלי מטבח", "יצירה", "צעצועים", "טקסטיל", "ניקיון", "חזרה לבית הספר", "מחסן", "חשמל", "קופות"]
ROLES = ["סדרן/ית", "קופאי/ת", "מחסנאי/ת", "סגן/ית מנהל", "אחראי/ת משמרת", "אחראי/ת מחלקה", "מלגזן/ית", "עובד/ת ניקיון", "נציג/ת שירות", "בודק/ת חשבוניות", "אחראי/ת החזרות", "סופר/ת מלאי", "מתפעל/ת מבצעים", "עובד/ת לילה", "תומך/ת טכני"]

# --- מנוע הניתוח המילולי ---
def generate_full_analysis(data):
    # ספירת סוגי תשובות
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for a in data.get('answers', []):
        counts[a['val']] = counts.get(a['val'], 0) + 1
    
    # 1. ניתוח אופי (דיוקן)
    if counts['A'] >= 8:
        char_text = "מדובר במועמד בעל יוזמה יוצאת דופן. הוא לא מחכה להוראות ומזהה לבד מקומות שצריכים טיפול. אדם אנרגטי שמתאים למחלקות 'קשות' ודינמיות."
    elif counts['B'] >= 8:
        char_text = "מועמד שירותי מאוד שרואה את הלקוח במרכז. הוא סבלני, אדיב וניחן ביכולת הקשבה גבוהה. עובד יציב שנעים לעבוד איתו."
    else:
        char_text = "עובד משימתי מאוד. הוא מצטיין בביצוע פעולות שגרתיות הדורשות סדר, דיוק והתמדה. הוא לא מתפזר וממוקד במה שהוגדר לו."

    # 2. אינטראקציה חברתית (מול הצוות)
    if counts['B'] + counts['A'] >= 10:
        social_text = "עובד צוות מצוין. הוא תורם לאווירה טובה, עוזר לחברים לעבודה בשקט ומעדיף שיתוף פעולה על פני תחרות."
    else:
        social_text = "עובד עצמאי. הוא מעדיף לקבל את הגיזרה שלו ולעבוד בה לבד בשקט. הוא פחות מתערב בעניינים של אחרים וממוקד במטרה."

    # 3. אינטראקציה מול מנהל (פרוטוקול ניהול)
    if counts['A'] >= 7:
        manager_text = "ניהול באוטונומיה: תן לו את המשימה הכללית ושחרר אותו לעבוד. הוא יביא תוצאות טובות יותר אם לא ירגיש ש'יושבים לו על הראש'."
    else:
        manager_text = "ניהול מובנה: זקוק לסדר יום ברור. מומלץ לתת לו רשימת משימות (צ'ק ליסט) ולבצע איתו בקרה קצרה בסוף כל משמרת."

    return {"character": char_text, "social": social_text, "manager_protocol": manager_text}

# --- דף הממשק (HTML + JS) ---
INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX Management PRO</title>
    <style>
        :root { --max-red: #e31e24; --max-blue: #1e40af; }
        body { font-family: 'Segoe UI', sans-serif; background: #f4f7f6; margin: 0; }
        .header { background: var(--max-red); color: white; padding: 20px; text-align: center; font-size: 26px; font-weight: bold; border-bottom: 4px solid #b91c1c; }
        .container { max-width: 850px; margin: 20px auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .card { background: #ffffff; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-bottom: 20px; transition: 0.2s; }
        .card:hover { border-color: var(--max-red); }
        .insight-card { padding: 20px; border-radius: 10px; margin-bottom: 20px; border-right: 6px solid var(--max-red); background: #fef2f2; font-size: 1.1em; }
        select, input, button { width: 100%; padding: 14px; margin: 10px 0; border-radius: 10px; border: 1px solid #cbd5e1; font-size: 16px; }
        .btn-main { background: var(--max-red); color: white; border: none; cursor: pointer; font-weight: bold; font-size: 18px; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="header">MAX STOCK - ניהול וגיוס כוח אדם</div>
    <div class="container">
        
        <div id="login-view">
            <button class="btn-main" onclick="showSec()">התחל שאלון מועמד (מזכירה)</button>
            <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee;">
                <input type="password" id="mPass" placeholder="סיסמת מנהל">
                <button class="btn-main" style="background:var(--max-blue);" onclick="showMan()">כניסת מנהל לניתוח</button>
            </div>
        </div>

        <div id="sec-view" class="hidden">
            <h3 style="text-align:center;">שאלון התאמה לרשת MAX</h3>
            <div id="quizArea"></div>
            <div class="card" style="background: #edf2f7;">
                <input type="text" id="cName" placeholder="שם מלא של המועמד">
                <input type="text" id="cDob" placeholder="תאריך לידה (DD.MM.YYYY)">
            </div>
            <button class="btn-main" onclick="submitQuiz()">סיים ושלח למנהל</button>
        </div>

        <div id="man-view" class="hidden">
            <h3>פרוטוקול ניתוח מלא</h3>
            <select id="candSelect" onchange="render()"></select>
            
            <div id="insArea">
                <div class="insight-card"><b>דיוקן אישיותי:</b> <div id="cBox"></div></div>
                <div class="insight-card" style="border-color:var(--max-blue); background:#eff6ff;"><b>אינטראקציה חברתית:</b> <div id="sBox"></div></div>
                <div class="insight-card" style="border-color:#059669; background:#f0fdf4;"><b>אינטראקציה מול מנהל:</b> <div id="mBox"></div></div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                <select id="dSet">""" + "".join([f"<option>{d}</option>" for d in DEPARTMENTS]) + """</select>
                <select id="jSet">""" + "".join([f"<option>{r}</option>" for r in ROLES]) + """</select>
            </div>
            <button class="btn-main" style="background:#059669; margin-top:20px;">שמור שיבוץ סופי במערכת</button>
            <button onclick="location.reload()" style="background:none; color:gray; border:none; text-decoration:underline;">יציאה</button>
        </div>
    </div>

    <script>
        const questions = [
            {q: "לקוח מחפש מוצר שחסר על המדף, מה תעשה?", a: "אבדוק מיד במחסן ואנסה להביא לו", b: "אבדוק במחשב או אשאל את האחראי", c: "אעדכן אותו שכרגע חסר במלאי", d: "אמשיך בעבודה שלי כרגיל"},
            {q: "יש תור ארוך בקופות ואתה בסידור מדף, מה תגובתך?", a: "אגש מיד לעזור בקופה בלי שיבקשו", b: "אחכה שיקראו לי לעזור לעמיתים", c: "אמשיך לסדר כי זה התפקיד שהוגדר לי", d: "אלך למחסן כדי להימנע מהעומס"},
            {q: "ראית מוצר שבור שנשפך על הרצפה במעבר?", a: "אנקה מיד ואדאג שהמעבר יהיה בטוח", b: "אשים סימון ואדווח למנהל המשמרת", c: "אקרא לעובד הניקיון שיגיע לטפל בזה", d: "אעקוף את זה ואמשיך בסידור המדף"},
            {q: "לקוח צועק עליך בגלל מחיר של מוצר?", a: "אקשיב לו בסבלנות ואנסה להרגיע בחיוך", b: "אקרא מיד למנהל שיפתור את הבעיה", c: "אגיד לו שזה המחיר ואין לי מה לעשות", d: "אתעלם ואעבור לעבוד באזור אחר"},
            {q: "המנהל מבקש ממך לעשות משימה שאתה לא אוהב?", a: "אבצע אותה הכי טוב שאפשר ובמהירות", b: "אבצע את המשימה ואז אבקש לגוון", c: "אעשה אותה לאט כדי שלא יבקשו שוב", d: "אנסה להסביר למה עדיף שמישהו אחר יעשה"},
            {q: "גילית שחבר לעבודה טעה בסידור המחלקה שלו?", a: "אעזור לו לתקן את הטעות בנעימות", b: "אסב את תשומת ליבו לטעות שעשה", c: "אלך לעדכן את המנהל על חוסר הדיוק", d: "זה לא ענייני, אני מרוכז רק בשלי"},
            {q: "הגעת למשמרת והמחלקה הפוכה לגמרי?", a: "אתחיל לסדר מיד לפי מה שהכי דחוף", b: "אשאל את המנהל מאיפה הכי כדאי להתחיל", c: "אסדר רק את החלק הקטן שבו אני עובד", d: "אחכה שהמנהל ייתן לי הוראות מפורטות"},
            {q: "לקוח מתלבט לגבי מתנה ולא יודע מה לבחור?", a: "אציע לו כמה אפשרויות ואעזור לו להחליט", b: "אכוון אותו לאזור המתנות הפופולריות", c: "אגיד לו שקשה להמליץ כי זה עניין של טעם", d: "אפנה אותו לעובד אחר שפנוי לזה"},
            {q: "מצאת שטר כסף על הרצפה באמצע החנות?", a: "אמסור אותו מיד למנהל או לקופה הראשית", b: "אשאל לקוחות קרובים אם איבדו כסף", c: "אשים בקופת צדקה ליד הקופה", d: "אכניס לכיס ואחליט מה לעשות בסוף"},
            {q: "איך אתה הכי אוהב שעובדים איתך?", a: "שנותנים לי משימה ואחריות ואני רץ לבד", b: "בשיתוף פעולה מלא עם כל הצוות", c: "שיש מנהל שאומר לי בדיוק מה לעשות", d: "לעבוד לבד בשקט ובלי שאף אחד יפריע"},
            {q: "לקוח דורש הנחה שאתה יודע שאי אפשר לתת?", a: "אסביר לו בנימוס את מדיניות הרשת", b: "אבדוק אם יש מבצע אחר שיוכל לעזור לו", c: "אשלח אותו למנהל שיחליט בעצמו", d: "אגיד לו 'לא' בצורה קצרה ופשוטה"},
            {q: "שמת לב שסימנת מחירים לא נכונים על סחורה?", a: "אתקן הכל מיד ואדווח על הטעות שלי", b: "אשאל את המנהל איך כדאי לתקן את זה", c: "אקווה שזה יעבור בשקט בלי שירגישו", d: "אשאיר את זה ככה, זה לא נורא"},
            {q: "המשמרת נגמרה אבל החנות מלאה בלקוחות?", a: "אשאר לעזור עוד קצת עד שהלחץ יירד", b: "אסיים את מה שהתחלתי ואז אלך הביתה", c: "אחתים כרטיס ואצא מיד, העבודה נגמרה", d: "אעלם למחסן כדי שלא יבקשו ממני להישאר"},
            {q: "עובד אחר מבקש ממך לעשות משהו לא תקין?", a: "אסרב ואסביר לו למה זה נגד הנהלים", b: "אדווח למנהל על הבקשה הלא תקינה", c: "אעזור לו הפעם באופן יוצא מן הכלל", d: "אעשה מה שהוא ביקש כדי לא לריב איתו"},
            {q: "מה הדבר שהכי מניע אותך בעבודה?", a: "להצליח, להתקדם ולהיות הכי טוב בסניף", b: "לתת שירות מעולה ולראות לקוח מרוצה", c: "לראות מחלקה מסודרת, נקייה ומתוקתקת", d: "לסיים את היום בשקט ולקבל משכורת"}
        ];

        function showSec() { document.getElementById('login-view').classList.add('hidden'); document.getElementById('sec-view').classList.remove('hidden'); renderQuiz(); }
        
        function renderQuiz() {
            let h = "";
            questions.forEach((item, i) => {
                h += `<div class="card"><b>${i+1}. ${item.q}</b>
                <select id="q${i}"><option value="A">${item.a}</option><option value="B">${item.b}</option><option value="C">${item.c}</option><option value="D">${item.d}</option></select></div>`;
            });
            document.getElementById('quizArea').innerHTML = h;
        }

        async function showMan() {
            if(document.getElementById('mPass').value === 'admin456') {
                document.getElementById('login-view').classList.add('hidden');
                document.getElementById('man-view').classList.remove('hidden');
                const r = await fetch('/api/get'); window.cands = await r.json();
                document.getElementById('candSelect').innerHTML = window.cands.map((c,i)=>`<option value="${i}">${c.firstName}</option>`).join('');
                if(window.cands.length > 0) render();
            } else alert("סיסמה שגויה");
        }

        function render() {
            const c = window.cands[document.getElementById('candSelect').value];
            document.getElementById('cBox').innerText = c.full_analysis.character;
            document.getElementById('sBox').innerText = c.full_analysis.social;
            document.getElementById('mBox').innerText = c.full_analysis.manager_protocol;
        }

        async function submitQuiz() {
            const name = document.getElementById('cName').value;
            const dob = document.getElementById('cDob').value;
            if(!name || !dob) return alert("נא למלא שם ותאריך לידה");
            const answers = Array.from({length:15}, (_, i) => ({ val: document.getElementById('q'+i).value }));
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({firstName:name, dob, answers}) });
            alert("השאלון נשלח למנהל!"); location.reload();
        }
    </script>
</body>
</html>
"""

# --- Routes API ---
@app.route('/')
def index(): return render_template_string(INDEX_HTML)

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['full_analysis'] = generate_full_analysis(d)
    db = []
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f:
            try: db = json.load(f)
            except: db = []
    db.append(d)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)
    return jsonify({"ok": True})

@app.route('/api/get')
def get_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r', encoding='utf-8') as f: return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
