import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)
app.secret_key = 'max_secure_key_2026'

def get_num(val):
    if not val: return 0
    num = sum([int(d) for d in str(val) if d.isdigit()])
    while num > 9 and num not in [11, 22]:
        num = sum(int(digit) for digit in str(num))
    return num

def deep_analysis(data):
    num = get_num(data['dob'])
    high_quality = sum(1 for a in data['answers'] if a['idx'] == "1")
    traits = {1: "מנהיגות", 2: "שירות", 3: "תקשורת", 4: "סדר", 5: "דינמיות", 6: "אחריות", 7: "עומק", 8: "חוסן", 9: "עזרה", 11: "אינטואיציה", 22: "ביצוע"}
    analysis = f"ניתוח עבור {data['firstName']}:\nתכונה דומיננטית: {traits.get(num, 'ורסטיליות')}.\n"
    analysis += f"ציון שירותיות: {int((high_quality/15)*100)}%\n"
    analysis += "שיבוץ מומלץ: " + ("מחלקות אינטנסיביות" if num in [1, 5, 8, 22] else "מחלקות שירות ואסתטיקה")
    return analysis

HTML = r"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>MAX Global Recruitment</title>
    <style>
        :root { --red: #e31e24; --bg: #f1f5f9; }
        body { font-family: 'Assistant', sans-serif; background: var(--bg); margin: 0; transition: all 0.3s; }
        .header { background: white; padding: 15px; text-align: center; border-bottom: 4px solid var(--red); }
        .container { max-width: 850px; margin: 20px auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .hidden { display: none; }
        .card { background: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; margin-bottom: 15px; }
        select, input, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 16px; }
        .btn-main { background: var(--red); color: white; border: none; font-weight: bold; cursor: pointer; }
        .lang-bar { display: flex; justify-content: center; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
        .lang-btn { background: white; border: 1px solid #ddd; padding: 10px 15px; cursor: pointer; border-radius: 5px; font-weight: bold; }
        .lang-btn.active { background: var(--red); color: white; }
        .q-text { font-weight: bold; display: block; margin-bottom: 8px; color: #334155; }
    </style>
</head>
<body>
    <div class="header"><h1 id="mainTitle">MAX - כאן קונים בכיף</h1></div>
    <div class="container">
        
        <div id="login-section">
            <input type="text" id="username" placeholder="שם משתמש">
            <input type="password" id="password" placeholder="סיסמה">
            <button class="btn-main" onclick="login()">כניסה / Login</button>
        </div>

        <div id="sec-section" class="hidden">
            <div class="lang-bar" id="lBar">
                <button class="lang-btn active" onclick="changeL('he')">עברית</button>
                <button class="lang-btn" onclick="changeL('en')">English</button>
                <button class="lang-btn" onclick="changeL('th')">ไทย</button>
                <button class="lang-btn" onclick="changeL('ru')">Русский</button>
                <button class="lang-btn" onclick="changeL('ar')">العربية</button>
            </div>
            
            <div id="quizContainer"></div>

            <div class="card">
                <label><b id="lblFname">שם המועמד:</b></label>
                <input type="text" id="firstName">
                <label><b id="lblDob">תאריך לידה:</b></label>
                <input type="text" id="dob" placeholder="DD.MM.YYYY">
            </div>
            <button class="btn-main" id="btnSubmit" onclick="submitForm()">שליחה למנהל</button>
        </div>

        <div id="man-section" class="hidden">
            <div class="card">
                <h3>ניהול מועמדים</h3>
                <select id="selCand" onchange="runAnalysis()"></select>
                <div id="analysisResult" style="margin-top:15px; background: #fff3f3; padding: 15px; border-right: 5px solid red; white-space: pre-wrap; font-weight: bold;"></div>
            </div>
            <button onclick="location.reload()">התנתק</button>
        </div>
    </div>

    <script>
        let currentLang = 'he';
        const content = {
            he: {
                title: "MAX - שאלון גיוס", fname: "שם המועמד:", dob: "תאריך לידה:", send: "שליחה למנהל",
                questions: [
                    {q: "לקוח מבקש עזרה בעומס?", opt: ["אפסיק הכל ואעזור", "אסביר לו איפה המוצר", "אבקש שימתין", "אפנה לעובד אחר"]},
                    {q: "חבר לצוות חסר ויש לחץ?", opt: ["אגביר קצב ואעזור לכולם", "אעשה רק את שלי", "אתלונן למנהל", "אחכה להוראות"]},
                    {q: "ראית לקוח חשוד?", opt: ["אגש בחיוך ואציע עזרה", "אתעלם", "אצעק עליו", "אלך למחסן"]},
                    {q: "שינוי מחלקה דחוף?", opt: ["אעבור בחיוך", "אעבור לזמן קצר", "אראה חוסר שביעות רצון", "אסרב"]},
                    {q: "אין עומס כרגע?", opt: ["אנקה ואסדר מדפים", "אנוח בצד", "אדבר עם חברים", "בטלפון"]},
                    {q: "התכונה החשובה ביותר?", opt: ["שירותיות", "מהירות", "עבודה לבד", "דייקנות"]},
                    {q: "לקוח צועק על מחיר?", opt: ["אקשיב בסבלנות", "אגיד שלא יקנה", "אתעלם", "אתווכח"]},
                    {q: "מוצר פגום על המדף?", opt: ["אוריד ואדווח", "אשאיר שם", "אחביא מאחורה", "אזרוק לפח"]},
                    {q: "משימה פיזית קשה?", opt: ["אעבוד בקצב קבוע", "אבקש שמישהו אחר יעשה", "אעבוד לאט", "חצי עבודה"]},
                    {q: "עובד אחר טועה?", opt: ["אעזור לו בפרטיות", "אלשין", "אצחק עליו", "אשמח"]},
                    {q: "הגעה למשמרת?", opt: ["10 דקות לפני", "בדיוק בזמן", "מותר לאחר", "מתי שנוח"]},
                    {q: "נוהל חדש?", opt: ["אקשיב ואנסה", "שאחרים יעשו", "אגיד שהבנתי", "אנחש"]},
                    {q: "מוצר חסר במלאי?", opt: ["אבדוק ואציע חלופי", "אגיד 'אין'", "אשלח למתחרים", "תבוא מחר"]},
                    {q: "ביקורת מהמנהל?", opt: ["אקבל ואשתפר", "אעלב", "אתווכח", "אתעלם"]},
                    {q: "כסף על הרצפה?", opt: ["אמסור למנהל/קופה", "לכיס", "אשאיר שם", "אקנה משהו"]}
                ]
            },
            en: {
                title: "MAX - Recruitment Quiz", fname: "Full Name:", dob: "Date of Birth:", send: "Submit to Manager",
                questions: [
                    {q: "Customer needs help during rush?", opt: ["Stop everything and help", "Explain where it is", "Ask to wait", "Send to someone else"]},
                    {q: "Teammate missing?", opt: ["Speed up and help all", "Do only my part", "Complain", "Wait for orders"]},
                    {q: "Suspicious customer?", opt: ["Approach with a smile", "Ignore", "Shout", "Go to warehouse"]},
                    {q: "Urgent dept change?", opt: ["Move with a smile", "Move for short time", "Show annoyance", "Refuse"]},
                    {q: "No rush right now?", opt: ["Clean and organize", "Rest", "Chat", "Phone"]},
                    {q: "Key trait?", opt: ["Service-oriented", "Speed", "Solo work", "Punctuality"]},
                    {q: "Customer shouting?", opt: ["Listen patiently", "Tell them don't buy", "Ignore", "Argue"]},
                    {q: "Damaged item?", opt: ["Remove and report", "Leave it", "Hide it", "Trash it"]},
                    {q: "Physical task?", opt: ["Steady pace", "Ask others", "Work slow", "Half job"]},
                    {q: "Peer making mistake?", opt: ["Help privately", "Tell manager", "Laugh", "Be happy"]},
                    {q: "Arrival time?", opt: ["10 mins early", "Exactly on time", "Occasional late", "Anytime"]},
                    {q: "New procedure?", opt: ["Listen and try", "Others do it", "Pretend to know", "Guess"]},
                    {q: "Out of stock?", opt: ["Check and offer alt", "Say 'None'", "Send to competitors", "Come tomorrow"]},
                    {q: "Manager criticism?", opt: ["Accept and improve", "Get offended", "Argue", "Ignore"]},
                    {q: "Money on floor?", opt: ["Hand to manager", "Pocket it", "Leave it", "Buy something"]}
                ]
            },
            th: {
                title: "MAX - แบบทดสอบการสรรหา", fname: "ชื่อ-นามสกุล:", dob: "วันเกิด:", send: "ส่งให้ผู้จัดการ",
                questions: [
                    {q: "ลูกค้าขอความช่วยเหลือตอนยุ่ง?", opt: ["หยุดทุกอย่างและช่วย", "บอกทาง", "ให้รอ", "ส่งต่อคนอื่น"]},
                    {q: "เพื่อนร่วมงานไม่มา?", opt: ["เร่งมือช่วยทุกคน", "ทำแค่ส่วนตัว", "บ่น", "รอสั่ง"]},
                    {q: "ลูกค้ามีพิรุธ?", opt: ["ยิ้มและช่วย", "เมิน", "ตะโกนใส่", "ไปหลังร้าน"]},
                    {q: "เปลี่ยนแผนกด่วน?", opt: ["ไปทันทีด้วยยิ้ม", "ไปแป๊บเดียว", "แสดงความไม่พอใจ", "ปฏิเสธ"]},
                    {q: "ตอนร้านว่าง?", opt: ["ทำความสะอาดจัดของ", "พัก", "คุย", "เล่นมือถือ"]},
                    {q: "คุณสมบัติสำคัญ?", opt: ["ใจรักบริการ", "ความเร็ว", "ทำงานเดี่ยว", "ตรงเวลา"]},
                    {q: "ลูกค้าโวยวาย?", opt: ["ฟังอย่างอดทน", "บอกไม่ต้องซื้อ", "เมิน", "เถียง"]},
                    {q: "สินค้าชำรุด?", opt: ["เก็บออกแจ้งหัวหน้า", "วางไว้ที่เดิม", "ซ่อนไว้หลัง", "ทิ้งถังขยะ"]},
                    {q: "งานหนักแรง?", opt: ["ทำสม่ำเสมอ", "ให้คนอื่นทำ", "ทำช้าๆ", "ทำครึ่งเดียว"]},
                    {q: "เพื่อนทำผิด?", opt: ["ช่วยบอกส่วนตัว", "ฟ้อง", "หัวเราะเยาะ", "ดีใจ"]},
                    {q: "การมาทำงาน?", opt: ["ก่อน 10 นาที", "ตรงเวลาเป๊ะ", "สายได้นิดหน่อย", "ตามสะดวก"]},
                    {q: "ระเบียบใหม่?", opt: ["ฟังและลองทำ", "รอคนอื่นทำ", "แกล้งทำเป็นรู้", "เดาเอา"]},
                    {q: "ของหมด?", opt: ["เช็คและเสนอตัวอื่น", "บอกว่าไม่มี", "ไล่ไปร้านอื่น", "มาพรุ่งนี้"]},
                    {q: "คำวิจารณ์จากนาย?", opt: ["ยอมรับปรับปรุง", "งอน", "เถียง", "เมิน"]},
                    {q: "เจอเงินที่พื้น?", opt: ["ส่งคืนหัวหน้า", "เก็บเอง", "วางไว้ที่เดิม", "เอาไปซื้อของ"]}
                ]
            },
            ru: {
                title: "MAX - Тест для кандидатов", fname: "Имя:", dob: "Дата рождения:", send: "Отправить менеджеру",
                questions: [
                    {q: "Клиент просит помощи в спешке?", opt: ["Все брошу и помогу", "Объясню где", "Попрошу подождать", "Передам другому"]},
                    {q: "Напарника нет?", opt: ["Ускорюсь и помогу всем", "Только свое", "Жаловаться", "Ждать приказа"]},
                    {q: "Подозрительный клиент?", opt: ["Улыбнусь и помогу", "Игнор", "Крикнуть", "Уйти"]},
                    {q: "Смена отдела?", opt: ["С улыбкой", "Ненадолго", "Недоволен", "Отказ"]},
                    {q: "Нет работы?", opt: ["Уборка и полки", "Отдых", "Болтать", "Телефон"]},
                    {q: "Главное качество?", opt: ["Сервис", "Скорость", "Одиночка", "Точность"]},
                    {q: "Клиент кричит?", opt: ["Слушать терпеливо", "Пусть не берет", "Игнор", "Спорить"]},
                    {q: "Брак на полке?", opt: ["Убрать и отчет", "Оставить", "Спрятать", "В мусор"]},
                    {q: "Тяжелый труд?", opt: ["Стабильный темп", "Пусть другие", "Медленно", "Кое-как"]},
                    {q: "Коллега ошибся?", opt: ["Помогу лично", "Сдам", "Смеяться", "Рад"]},
                    {q: "Приход на смену?", opt: ["За 10 мин", "Вовремя", "Опоздаю", "Как удобно"]},
                    {q: "Новое правило?", opt: ["Слушать и пробовать", "Пусть другие", "Притворюсь", "Угадаю"]},
                    {q: "Нет товара?", opt: ["Проверю и замену", "Просто 'Нет'", "К конкурентам", "Завтра"]},
                    {q: "Критика босса?", opt: ["Принять и исправить", "Обида", "Спор", "Игнор"]},
                    {q: "Деньги на полу?", opt: ["Отдать боссу", "В карман", "Оставить", "Купить что-то"]}
                ]
            },
            ar: {
                title: "MAX - اختبار التوظيف", fname: "الاسم الكامل:", dob: "تاريخ الميلاد:", send: "إرسال للمدير",
                questions: [
                    {q: "زبون يطلب مساعدة وقت الزحمة؟", opt: ["أترك كل شيء وأساعده", "أشرح له مكانه", "أطلب منه الانتظار", "أوجهه لموظف آخر"]},
                    {q: "زميل غائب وهناك ضغط؟", opt: ["أزيد سرعتي وأساعد الكل", "أقوم بعملي فقط", "أشتكي للمدير", "أنتظر الأوامر"]},
                    {q: "زبون مشتبه به؟", opt: ["أقترب بابتسامة وأساعده", "أتجاهل", "أصرخ عليه", "أذهب للمخزن"]},
                    {q: "تغيير قسم طارئ؟", opt: ["أنتقل بابتسامة", "أنتقل لفترة قصيرة", "أظهر عدم الرضا", "أرفض"]},
                    {q: "لا يوجد زحمة حالياً؟", opt: ["أنظف وأرتب الأرفف", "أرتاح جانباً", "أتحدث مع زملائي", "على الهاتف"]},
                    {q: "أهم صفة؟", opt: ["الخدمة", "السرعة", "العمل الفردي", "الدقة"]},
                    {q: "زبون يصرخ بسبب السعر؟", opt: ["أستمع بصبر", "أقول له لا تشتري", "أتجاهل", "أجادل"]},
                    {q: "منتج تالف على الرف؟", opt: ["أزيله وأبلغ المسؤول", "أتركه مكانه", "أخبئه في الخلف", "أرميه"]},
                    {q: "مهمة بدنية شاقة؟", opt: ["أعمل بوتيرة ثابتة", "أطلب من غيري", "أعمل ببطء", "نصف عمل"]},
                    {q: "زميل يخطئ؟", opt: ["أساعده بخصوصية", "أبلغ عنه", "أضحك عليه", "أفرح"]},
                    {q: "الوصول للمناوبة؟", opt: ["قبل 10 دقائق", "بالوقت تماماً", "مسموح التأخير", "متى شئت"]},
                    {q: "إجراء جديد؟", opt: ["أستمع وأجرب", "أنتظر غيري", "أدعي الفهم", "أخمن"]},
                    {q: "منتج مفقود؟", opt: ["أبحث وأعرض بديل", "أقول 'لا يوجد'", "أرسله للمنافسين", "تعال غداً"]},
                    {q: "نقد من المدير؟", opt: ["أقبل وأتحسن", "أزعل", "أجادل", "أتجاهل"]},
                    {q: "مال على الأرض؟", opt: ["أسلمه للمدير", "في جيبي", "أتركه", "أشتري شيئاً"]}
                ]
            }
        };

        function changeL(l) {
            currentLang = l;
            const t = content[l];
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('mainTitle').innerText = t.title;
            document.getElementById('lblFname').innerText = t.fname;
            document.getElementById('lblDob').innerText = t.dob;
            document.getElementById('btnSubmit').innerText = t.send;
            
            const cont = document.getElementById('sec-section');
            cont.style.direction = (l==='he'||l==='ar') ? 'rtl' : 'ltr';
            
            document.getElementById('quizContainer').innerHTML = t.questions.map((q, i) => `
                <div class="card">
                    <span class="q-text">${i+1}. ${q.q}</span>
                    <select id="q${i}">
                        ${q.opt.map((o, idx) => `<option value="${idx+1}">${o}</option>`).join('')}
                    </select>
                </div>
            `).join('');
        }

        function login() {
            const u = document.getElementById('username').value;
            if(u==='secretary') { document.getElementById('login-section').classList.add('hidden'); document.getElementById('sec-section').classList.remove('hidden'); changeL('he'); }
            else if(u==='manager') { document.getElementById('login-section').classList.add('hidden'); document.getElementById('man-section').classList.remove('hidden'); loadManager(); }
        }

        async function submitForm() {
            const answers = content[currentLang].questions.map((_, i) => ({ idx: document.getElementById('q'+i).value }));
            const data = { firstName: document.getElementById('firstName').value, dob: document.getElementById('dob').value, answers };
            if(!data.firstName || !data.dob) return alert("אנא מלא שם ותאריך לידה");
            await fetch('/api/save', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data) });
            alert("נשמר בהצלחה!"); location.reload();
        }

        async function loadManager() {
            const res = await fetch('/api/get');
            const data = await res.json();
            document.getElementById('selCand').innerHTML = data.map((c, i) => `<option value="${i}">${c.firstName}</option>`).join('');
            runAnalysis();
        }

        async function runAnalysis() {
            const idx = document.getElementById('selCand').value;
            const res = await fetch('/api/get');
            const data = await res.json();
            document.getElementById('analysisResult').innerText = data[idx].analysis;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    d['analysis'] = deep_analysis(d)
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
        with open('data.json', 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
