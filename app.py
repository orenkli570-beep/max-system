<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>מערכת גיוס - MAX STOCK</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{font-family:'Segoe UI',Arial,sans-serif;min-height:100vh;background:#f3f4f6;direction:rtl;color:#333}
        .container{max-width:800px;margin:20px auto;padding:15px}
        .glass-card{background:white;border-radius:20px;padding:30px;box-shadow:0 10px 25px rgba(0,0,0,0.05)}
        .header{background:#e31e24;color:white;padding:25px;text-align:center;border-radius:20px;margin-bottom:20px}
        .q-card{background:#f9fafb;border:1px solid #e5e7eb;padding:20px;border-radius:15px;margin-bottom:15px}
        .btn-gold{width:100%;padding:15px;background:linear-gradient(135deg,#c9a84c,#e8c97a);border:none;border-radius:12px;color:#fff;font-weight:bold;font-size:18px;cursor:pointer}
        input, select {width:100%;padding:12px;margin-top:10px;border:2px solid #eee;border-radius:10px;font-size:16px}
        .admin-item{border-right:6px solid #e31e24;background:#fff;padding:20px;margin-bottom:15px;border-radius:10px;box-shadow:0 2px 5px rgba(0,0,0,0.05)}
        .lang-btn{padding:10px 20px;margin:5px;border-radius:10px;border:1px solid #ddd;background:white;cursor:pointer}
        .lang-active{background:#e31e24;color:white;border-color:#e31e24}
        .tag{display:inline-block;padding:4px 10px;background:#eee;border-radius:5px;font-size:13px;margin-left:5px}
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        // --- ניהול נתונים ---
        const DB = {
            load: () => JSON.parse(localStorage.getItem("max_candidates") || "[]"),
            save: (list) => localStorage.setItem("max_candidates", JSON.stringify(list)),
            add: (item) => {
                const l = DB.load();
                l.push({...item, id: Date.now(), submittedAt: new Date().toISOString()});
                DB.save(l);
            }
        };

        // --- שפות ותכנים ---
        const LANGS = {
            he: { dir:"rtl", label:"עברית", welcome:"ברוכים הבאים", name:"שם מלא", dob:"תאריך לידה (DD.MM.YYYY)", start:"התחל שאלון", send:"שלח שאלון", questions: [
                {q:"לקוח מחפש מוצר שחסר על המדף, מה תעשה?", a:["אבדוק מיד במחסן ואנסה להביא לו","אבדוק במחשב או אשאל אחראי","אעדכן שחסר במלאי","אמשיך בעבודתי"]},
                {q:"יש תור ארוך בקופות ואתה בסידור מדף?", a:["אגש מיד לעזור בקופה","אחכה שיקראו לי","אמשיך לסדר מדפים","אלך למחסן"]},
                {q:"ראית מוצר שבור על הרצפה?", a:["אנקה מיד ואדאג לבטיחות","אדווח למנהל המשמרת","אקרא לעובד ניקיון","אעקוף ואמשיך לעבוד"]},
                {q:"לקוח צועק בגלל מחיר של מוצר?", a:["אקשיב בסבלנות ואנסה להרגיע","אקרא מיד למנהל","אגיד שזה המחיר וזהו","אתעלם ואעבור מקום"]},
                {q:"המנהל מבקש משימה שאתה לא אוהב?", a:["אבצע הכי טוב ומהר שאפשר","אבצע ואז אבקש לגוון","אעשה לאט שלא יבקשו שוב","אנסה להתחמק"]},
                {q:"גילית שחבר טעה בסידור המחלקה?", a:["אעזור לו לתקן בנעימות","אסב את תשומת ליבו","אדווח למנהל על הטעות","לא ענייני, אני בשלי"]},
                {q:"הגעת וכל המחלקה הפוכה לגמרי?", a:["אתחיל לסדר לפי הדחיפות","אשאל מנהל מאיפה להתחיל","אסדר רק את האזור שלי","אחכה להוראות מפורטות"]},
                {q:"לקוח מתלבט לגבי מתנה?", a:["אציע אפשרויות ואעזור","אכוון לאזור המתנות","אגיד שזה עניין של טעם","אפנה לעובד אחר"]},
                {q:"מצאת כסף על הרצפה בחנות?", a:["אמסור למנהל/קופה ראשית","אשאל לקוחות מסביב","אשים בקופת צדקה","אשמור בכיס"]},
                {q:"איך אתה הכי אוהב לעבוד?", a:["שיש לי אחריות ואני רץ לבד","בשיתוף פעולה עם הצוות","שיגידו לי בדיוק מה לעשות","לבד בשקט בלי הפרעות"]},
                {q:"לקוח דורש הנחה שאי אפשר לתת?", a:["אסביר בנימוס את המדיניות","אבדוק אם יש מבצע חלופי","אשלח אותו למנהל","אגיד פשוט לא"]},
                {q:"שמת לב שסימנת מחיר טעות?", a:["אתקן מיד ואדווח","אשאל מנהל איך לתקן","אקווה שלא ישימו לב","אשאיר ככה"]},
                {q:"המשמרת נגמרה והחנות עמוסה?", a:["אשאר לעזור עד שיירגע","אסיים משימה ואלך","אצא מיד - נגמר הזמן","אעלם למחסן"]},
                {q:"עובד מבקש לעשות משהו לא תקין?", a:["אסרב ואסביר את הנוהל","אדווח למנהל","אעזור לו באופן חד פעמי","אעשה מה שביקש"]},
                {q:"מה הכי מניע אותך?", a:["להתקדם ולהצליח","שירות מעולה ולקוח מרוצה","סדר וארגון מושלם","משכורת ושקט"]}
            ]},
            en: { dir:"ltr", label:"English", welcome:"Welcome", name:"Full Name", dob:"DOB (DD.MM.YYYY)", start:"Start", send:"Submit", questions: [
                {q:"Customer looks for missing item?", a:["Check warehouse","Check computer","Out of stock","Continue working"]},
                {q:"Long line at registers?", a:["Help immediately","Wait to be called","Keep stocking","Go to warehouse"]},
                {q:"Broken item on floor?", a:["Clean immediately","Report manager","Call cleaner","Ignore"]},
                {q:"Customer shouting about price?", a:["Listen calmly","Call manager","That's the price","Ignore"]},
                {q:"Task you dislike?", a:["Do it best/fast","Do and ask variety","Do slowly","Avoid"]},
                {q:"Colleague made mistake?", a:["Help fix it","Tell them","Report manager","Not my business"]},
                {q:"Dept is a mess?", a:["Start by urgency","Ask manager","Fix my spot","Wait for instructions"]},
                {q:"Gift dilemma?", a:["Offer options","Point to area","Taste matter","Refer other"]},
                {q:"Found money?", a:["Give to manager","Ask nearby","Charity box","Keep it"]},
                {q:"Work style?", a:["Responsibility","Teamwork","Instructions","Alone/Quiet"]},
                {q:"Discount demand?", a:["Explain policy","Check deals","Send to manager","Say no"]},
                {q:"Price error?", a:["Fix/Report","Ask how to fix","Hope no notice","Leave it"]},
                {q:"Shift over/Busy store?", a:["Stay/Help","Finish/Leave","Leave now","Hide"]},
                {q:"Colleague doing wrong?", a:["Refuse/Explain","Report","Help once","Do it"]},
                {q:"Motivation?", a:["Promotion","Service","Order","Salary"]}
            ]},
            ru: { dir:"ltr", label:"Русский", welcome:"Добро пожаловать", name:"ФИО", dob:"Дата рождения", start:"Начать", send:"Отправить", questions: Array(15).fill({q:"Вопрос...", a:["Ответ 1","Ответ 2","Ответ 3","Ответ 4"]}) },
            ar: { dir:"rtl", label:"العربية", welcome:"أهلاً بك", name:"الاسم الكامل", dob:"تاريخ الميلاد", start:"ابدأ", send:"إرسאל", questions: Array(15).fill({q:"سؤال...", a:["خيار 1","خيار 2","خيار 3","خيار 4"]}) },
            th: { dir:"ltr", label:"ภาษาไทย", welcome:"ยินดีต้อนรับ", name:"ชื่อ-นามสกุล", dob:"วันเกิด", start:"เริ่ม", send:"ส่ง", questions: Array(15).fill({q:"คำถาม...", a:["คำตอบ 1","คำตอบ 2","คำตอบ 3","คำตอบ 4"]}) }
        };

        // --- לוגיקת ניתוח (אסטרולוגיה + תשובות) ---
        function getSign(dob) {
            if(!dob || !dob.includes('.')) return {sign:"לא ידוע", traits:""};
            const [d, m] = dob.split('.').map(Number);
            const signs = [
                {sign:"גדי",from:[12,22],to:[1,19],traits:"שאפתן, חרוץ ומסור."},
                {sign:"דלי",from:[1,20],to:[2,18],traits:"יצירתי, חושב מחוץ לקופסה."},
                {sign:"דגים",from:[2,19],to:[3,20],traits:"אמפתי, מצוין בשירות לקוחות."},
                {sign:"טלה",from:[3,21],to:[4,19],traits:"יוזם, מהיר תגובה ואנרגטי."},
                {sign:"שור",from:[4,20],to:[5,20],traits:"יציב, נאמן ומוכוון פרטים."},
                {sign:"תאומים",from:[5,21],to:[6,20],traits:"תקשורתי וגמיש מאוד."},
                {sign:"סרטן",from:[6,21],to:[7,22],traits:"נאמן מאוד לעבודה ולצוות."},
                {sign:"אריה",from:[7,23],to:[8,22],traits:"כריזמטי, בעל נוכחות חזקה."},
                {sign:"בתולה",from:[8,23],to:[9,22],traits:"יסודי, מדויק ואחראי."},
                {sign:"מאזניים",from:[9,23],to:[10,22],traits:"דיפלומטי, פותר קונפליקטים."},
                {sign:"עקרב",from:[10,23],to:[11,21],traits:"ממוקד, חכם ואינטואיטיבי."},
                {sign:"קשת",from:[11,22],to:[12,21],traits:"אופטימי, לומד מהר מאוד."}
            ];
            const s = signs.find(s => (m === s.from[1] && d >= s.from[0]) || (m === s.to[1] && d <= s.to[0]));
            return s || signs[0];
        }

        function analyze(answers) {
            const bigCount = answers.filter(a => a === 0).length;
            const style = bigCount >= 9 ? "ראש גדול" : bigCount >= 5 ? "מאוזן" : "ראש קטן";
            return { style, bigCount };
        }

        // --- אפליקציה ---
        function App() {
            const [view, setView] = useState("home");
            const [lang, setLang] = useState("he");
            const [name, setName] = useState("");
            const [dob, setDob] = useState("");
            const [answers, setAnswers] = useState(Array(15).fill(null));
            const [adminData, setAdminData] = useState([]);

            const L = LANGS[lang];

            const handleFinish = () => {
                if(!name || !dob || answers.includes(null)) return alert("נא למלא הכל / Fill all fields");
                const result = { name, dob, answers, analysis: analyze(answers), sign: getSign(dob) };
                DB.add(result);
                alert("תודה רבה! השאלון נשלח / Success");
                setView("home");
            };

            if(view === "home") return (
                <div className="container" style={{textAlign:'center', paddingTop:'100px'}}>
                    <div className="header"><h1>MAX STOCK</h1></div>
                    <div className="glass-card">
                        <h2>{L.welcome}</h2>
                        <div style={{margin:'20px 0'}}>
                            {Object.keys(LANGS).map(k => (
                                <button key={k} onClick={()=>setLang(k)} className={`lang-btn ${lang===k?'lang-active':''}`}>{LANGS[k].label}</button>
                            ))}
                        </div>
                        <button className="btn-gold" onClick={()=>setView("form")}>{L.start}</button>
                        <button onClick={()=>{ if(prompt("Pass:")==="1234"){ setAdminData(DB.load()); setView("admin"); }}} style={{marginTop:'50px', background:'none', border:'none', color:'#ccc'}}>Admin</button>
                    </div>
                </div>
            );

            if(view === "form") return (
                <div className="container" style={{direction: L.dir}}>
                    <div className="header"><h1>פרטי מועמד</h1></div>
                    <div className="glass-card">
                        <input type="text" placeholder={L.name} value={name} onChange={e=>setName(e.target.value)} />
                        <input type="text" placeholder={L.dob} value={dob} onChange={e=>setDob(e.target.value)} />
                        <div style={{marginTop:'30px'}}>
                            {L.questions.map((q, i) => (
                                <div key={i} className="q-card">
                                    <strong>{i+1}. {q.q}</strong>
                                    <select onChange={e=> {const n=[...answers]; n[i]=parseInt(e.target.value); setAnswers(n);}}>
                                        <option value="">בחר תשובה...</option>
                                        {q.a.map((opt,idx)=><option key={idx} value={idx}>{opt}</option>)}
                                    </select>
                                </div>
                            ))}
                        </div>
                        <button className="btn-gold" onClick={handleFinish}>{L.send}</button>
                    </div>
                </div>
            );

            if(view === "admin") return (
                <div className="container" style={{direction:'rtl'}}>
                    <div className="header"><h1>לוח מנהל - מועמדים</h1></div>
                    <button onClick={()=>setView("home")} style={{marginBottom:'20px'}}>חזרה</button>
                    {adminData.map((c, i) => (
                        <div key={i} className="admin-item">
                            <h3>{c.name} <span className="tag">{c.dob}</span></h3>
                            <p><strong>סיווג:</strong> {c.analysis.style} ({c.analysis.bigCount} תשובות יוזמות)</p>
                            <p><strong>אפיון אסטרולוגי:</strong> מזל {c.sign.sign} - {c.sign.traits}</p>
                            <div style={{marginTop:'10px', fontSize:'14px', color:'#666'}}>
                                הוגש ב: {new Date(c.submittedAt).toLocaleString()}
                            </div>
                        </div>
                    ))}
                </div>
            );
        }

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>
