import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- לוגיקה: ניתוח עומק מילולי ---
def get_numerology_num(dob):
    if not dob: return 0
    nums = [int(d) for d in dob if d.isdigit()]
    res = sum(nums)
    while res > 9 and res not in [11, 22]:
        res = sum(int(digit) for digit in str(res))
    return res

def generate_full_analysis(data):
    num = get_numerology_num(data.get('dob', ''))
    counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for a in data.get('answers', []):
        counts[a['val']] = counts.get(a['val'], 0) + 1
    
    traits = {
        1: "מנהיגות וביצוע עצמאי. אדם שמוביל תהליכים ולא מחכה להוראות.",
        2: "שירותיות והכלה. זקוק לסביבה אנושית נעימה ופורח בשיתוף פעולה.",
        3: "תקשורת בין-אישית גבוהה. יודע לפתור בעיות מול לקוחות בצורה יצירתית.",
        4: "סדר ודיוק מופתי. מצטיין במשימות יסודיות שדורשות ריכוז גבוה.",
        5: "דינמיות וזריזות. נהנה מקצב עבודה גבוה ומסתגל מהר לשינויים.",
        6: "אחריות והרמוניה. רואה בחנות בית ודואג לאסתטיקה ולצוות.",
        7: "למידה עצמית ועומק. לומד נהלים מהר ומעדיף עבודה מחושבת.",
        8: "חוסן מנטלי. יודע לנהל לחצים כבדים ולעבוד בעומס רב.",
        9: "סבלנות ורצון לעזור. רואה בשירות שליחות וניחן באורך רוח.",
        11: "אינטואיציה חזקה. קולט את צרכי המנהל והלקוח עוד לפני שנאמרו.",
        22: "יכולת ביצוע מרשימה. מסוגל להרים פרויקטים מורכבים בשטח מאפס."
    }
    char_text = traits.get(num, "עובד ורסטילי בעל יכולת הסתגלות גבוהה.")

    if counts['A'] >= 7:
        inter_text = "העובד הפגין יוזמה גבוהה מאוד ('ראש גדול'). המנהל נדרש לתת לו אוטונומיה. הוא יזהה חוסרים ובלגן באופן עצמאי. מומלץ לנהל אותו דרך הגדרת יעדים ולא דרך פיקוח הדוק."
        recom = "מחלקות דינמיות: פלסטיקה, עונה, מחסן."
    elif counts['B'] >= 7:
        inter_text = "ביצועיסט שירותי מעולה. יבצע הוראות בצורה נאמנה עם חיוך. זקוק למשוב חיובי ותחושת שייכות. המנהל נדרש להגדיר משימות ברורות ולהודות לו על המאמץ."
        recom = "מחלקות שירותיות: ביוטי, דקורציה, כלי כתיבה."
    else:
        inter_text = "העובד זקוק למסגרת מובנית מאוד. המנהל נדרש לתת הנחיות שלב-אחרי-שלב ולבצע בקרה צמודה בתחילה. הוא יבצע עבודה מדויקת כל עוד הגבולות ברורים."
        recom = "מחלקות יציבות: קופות, יצירה, כלי מטבח."

    return {"character": char_text, "interaction": inter_text, "recommendation": recom}

INDEX_HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX Management</title>
    <style>
        :root { --max-red: #e31e24; --max-blue: #1e40af; --bg: #f8fafc; }
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: var(--bg); margin: 0; }
        .header { background: white; padding: 15px; text-align: center; border-bottom: 5px solid var(--max-red); }
        .container { max-width: 850px; margin: 20px auto; background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
        .hidden { display: none; }
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
        .btn-lang { padding: 10px 15px; cursor: pointer; border: 1px solid #ddd; background: white; border-radius: 20px; font-weight: bold; }
        .btn-lang.active { background: var(--max-red); color: white; border-color: var(--max-red); }
        .card { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 15px; border-radius: 12px; margin-bottom: 15px; }
        .insight-card { padding: 15px; border-radius: 10px; margin-bottom: 15px; border-right: 5px solid var(--max-red); background: #fef2f2; }
        input, select, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ccc; font-size: 16px; }
        .btn-main { background: var(--max-red); color: white; border: none; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header"><h1>MAX - כאן קונים בכיף</h1></div>
    <div class="container">
        <div id="login-view">
            <button class="btn-main" onclick="showSec()">כניסת מזכירה (שאלון)</button>
            <input type="password" id="mPass" placeholder="סיסמת מנהל" style="margin-top:20px;">
            <button class="btn-main" style="background:var(--max-blue);" onclick="showMan()">כניסת מנהל</button>
        </div>

        <div id="sec-view" class="hidden">
            <div class="lang-bar">
                <button class="btn-lang active" onclick="changeLang('he')">עברית</button>
                <button class="btn-lang" onclick="changeLang('en')">English</button>
                <button class="btn-lang" onclick="changeLang('ru')">Русский</button>
                <button class="btn-lang" onclick="changeLang('ar')">العربية</button>
                <button class="btn-lang" onclick="changeLang('th')">ไทย</button>
            </div>
            <div id="quizArea"></div>
            <div class="card">
                <input type="text" id="cName" placeholder="שם מלא">
                <input type="text" id="cDob" placeholder="תאריך לידה (DD.MM.YYYY)">
            </div>
            <button class="btn-main" onclick="submitQuiz()">שליחה למנהל</button>
        </div>

        <div id="man-view" class="hidden">
            <h3>ניתוח מועמד ופרוטוקול ניהול</h3>
            <select id="candSelect" onchange="render()"></select>
            <div id="insArea">
                <div class="insight-card"><b>דיוקן אופי:</b> <div id="cBox"></div></div>
                <div class="insight-card" style="border-right-color:var(--max-blue); background:#f0f7ff;"><b>אינטראקציה מומלצת:</b> <div id="iBox"></div></div>
                <div class="insight-card" style="border-right-color:#059669; background:#f0fdf4;"><b>המלצת שיבוץ:</b> <div id="rBox"></div></div>
            </div>
            <button onclick="location.reload()">התנתק</button>
        </div>
    </div>

    <script>
        const questionsDB = {
            he: [
                {q: "לקוח מחפש מוצר שחסר במדף, מה תעשה?", a: "אבדוק במחסן מיד ואנסה להביא לו", b: "אבדוק במחשב/אשאל אחראי", c: "אגיד לו שכרגע אין", d: "אמשיך בסידור המדף"},
                {q: "יש תור ארוך בקופות ואתה בסידור מדפים, מה תעשה?", a: "אגש מיד לעזור בלי שיבקשו ממני", b: "אחכה שיקראו לי לעזור", c: "אמשיך בסידור כי זה התפקיד שלי", d: "אלך להפסקה"},
                {q: "גילית מוצר שבור על הרצפה, מה התגובה?", a: "ארים, אנקה ואדווח מיד", b: "אשים בצד ואדווח בסוף המשמרת", c: "אקרא למנקה", d: "אעקוף את זה"},
                {q: "לקוח מתלונן בצעקות על המחיר, איך תגיב?", a: "אנסה להרגיע אותו בחיוך ולהסביר", b: "אקרא למנהל המשמרת", c: "אגיד לו שזה המחיר ואין מה לעשות", d: "אתעלם ואמשיך בעבודה"},
                {q: "המנהל נתן לך משימה שאתה לא אוהב, איך תפעל?", a: "אבצע אותה על הצד הטוב ביותר", b: "אבצע אבל אבקש לעבור למשהו אחר אחר כך", c: "אעשה אותה לאט", d: "אנסה להתחמק"},
                {q: "חבר לעבודה טעה בסידור, מה תעשה?", a: "אעזור לו לתקן בשקט", b: "אסב את תשומת ליבו", c: "אגיד למנהל", d: "זה לא ענייני"},
                {q: "הגעת לעבודה ויש בלאגן נוראי במחלקה, מה תעשה?", a: "אתחיל לסדר מיד לפי סדר עדיפויות", b: "אשאל את המנהל מאיפה להתחיל", c: "אסדר רק מה שאמרו לי", d: "אחכה לסוף המשמרת"},
                {q: "לקוח מבקש המלצה למתנה, מה תעשה?", a: "אשאל שאלות ואתאים לו מתנה מושלמת", b: "אראה לו את האזורים הפופולריים", c: "אגיד לו שכל אחד והטעם שלו", d: "אשלח אותו למחלקה אחרת"},
                {q: "מצאת שטר של 50 שח על הרצפה בחנות?", a: "אמסור מיד למנהל/קופה ראשית", b: "אשאל לקוחות מסביב אם איבדו", c: "אשים בקופת צדקה", d: "אשמור לעצמי"},
                {q: "איך אתה מעדיף לעבוד?", a: "באופן עצמאי עם יעדים", b: "בצוות עם חברים", c: "עם הוראות מדויקות מהמנהל", d: "לבד ובשקט"},
                {q: "לקוח מבקש הנחה שאינה קיימת?", a: "אסביר בנימוס את מדיניות הרשת", b: "אבדוק אם יש מבצע אחר רלוונטי", c: "אפנה אותו למנהל", d: "אגיד 'לא' קצר"},
                {q: "סימנת מוצרים במחיר טועה, מה תעשה?", a: "אתקן הכל מיד ואדווח על הטעות", b: "אדווח למנהל ואשאל מה לעשות", c: "אקווה שאף אחד לא ישים לב", d: "אשאיר ככה"},
                {q: "נגמר המשמרת ויש עוד לקוחות בחנות?", a: "אשאר עוד כמה דקות לעזור בלחץ", b: "אסיים את המשימה הנוכחית ואלך", c: "אלך מיד, השעון דופק", d: "אעלם למחסן"},
                {q: "מישהו מבקש ממך לעשות משהו בניגוד לנהלים?", a: "אסרב בנימוס ואסביר את הנוהל", b: "אדווח למנהל", c: "אעשה זאת באופן חד פעמי", d: "אזרום עם מה שאומרים לי"},
                {q: "מה הכי חשוב בעבודה לדעתך?", a: "יוזמה והצלחת החנות", b: "שירות מעולה ללקוח", c: "סדר וניקיון", d: "שקט ושלווה"}
            ],
            en: [
                {q: "Out of stock item, what do you do?", a: "Check warehouse immediately", b: "Check computer/ask manager", c: "Say not available", d: "Continue working"},
                {q: "Long lines at registers?", a: "Help immediately without being asked", b: "Wait to be called", c: "Keep shelving", d: "Go on break"},
                {q: "Broken product on floor?", a: "Clean and report", b: "Report later", c: "Call cleaner", d: "Walk around it"},
                {q: "Customer shouting about price?", a: "Calm them with a smile", b: "Call manager", c: "Say 'that is the price'", d: "Ignore"},
                {q: "Task you dislike?", a: "Do it perfectly", b: "Do it and ask for change later", c: "Do it slowly", d: "Avoid it"},
                {q: "Peer made a mistake?", a: "Help them fix it quietly", b: "Tell them", c: "Tell boss", d: "Not my business"},
                {q: "Messy department on arrival?", a: "Start organizing by priority", b: "Ask boss where to start", c: "Do only what I'm told", d: "Wait"},
                {q: "Gift recommendation request?", a: "Ask questions and find perfect gift", b: "Show popular items", c: "Say 'depends on taste'", d: "Send elsewhere"},
                {q: "Found 50 NIS on floor?", a: "Give to manager", b: "Ask customers nearby", c: "Charity", d: "Keep it"},
                {q: "Preferred work style?", a: "Independent with goals", b: "In a team", c: "With clear instructions", d: "Quiet and alone"},
                {q: "Non-existent discount request?", a: "Explain policy politely", b: "Check other deals", c: "Ask manager", d: "Say 'No'"},
                {q: "Wrong price tag error?", a: "Fix and report", b: "Ask manager", c: "Hope no one notices", d: "Leave it"},
                {q: "Shift ends, customers still inside?", a: "Stay a few minutes to help", b: "Finish task then leave", c: "Leave immediately", d: "Hide in back"},
                {q: "Asked to break a rule?", a: "Refuse and explain policy", b: "Tell manager", c: "Do it once", d: "Go with the flow"},
                {q: "Most important at work?", a: "Initiative & Success", b: "Customer service", c: "Order & Cleanliness", d: "Peace & Quiet"}
            ]
            // שאר השפות (רוסית, ערבית, תאילנדית) ימשיכו באותו מבנה בדיוק בקוד הסופי
        };

        function changeLang(l) {
            const langQs = questionsDB[l] || questionsDB['en'];
            document.body.dir = (l==='he'||l==='ar') ? 'rtl' : 'ltr';
            let html = "";
            langQs.forEach((item, i) => {
                html += `<div class="card"><b>${i+1}. ${item.q}</b>
                <select id="q${i}"><option value="A">${item.a}</option><option value="B">${item.b}</option><option value="C">${item.c}</option><option value="D">${item.d}</option></select></div>`;
            });
            document.getElementById('quizArea').innerHTML = html;
        }

        function showSec() { document.getElementById('login-view').classList.add('hidden'); document.getElementById('sec-view').classList.remove('hidden'); changeLang('he'); }
        async function showMan() {
            if(document.getElementById('mPass').value === 'admin456') {
                document.getElementById('login-view').classList.add('hidden');
                document.getElementById('man-view').classList.remove('hidden');
                const r = await fetch('/api/get'); window.cands = await r.json();
                document.getElementById('candSelect').innerHTML = window.cands.map((c,i)=>`<option value="${i}">${c.firstName}</option>`).join('');
                if(window.cands.length > 0) render();
            } else alert("Error");
        }

        async function submitQuiz() {
            const name = document.getElementById('cName').value;
            const dob = document.getElementById('cDob').value;
            if(!name || !dob) return alert("Fill all details");
            const answers = Array.from({length:15}, (_, i) => ({ val: document.getElementById('q'+i).value }));
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({firstName:name, dob, answers}) });
            alert("Sent!"); location.reload();
        }

        function render() {
            const c = window.cands[document.getElementById('candSelect').value];
            document.getElementById('cBox').innerText = c.full_analysis.character;
            document.getElementById('iBox').innerText = c.full_analysis.interaction;
            document.getElementById('rBox').innerText = c.full_analysis.recommendation;
        }
    </script>
</body>
</html>
"""

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
