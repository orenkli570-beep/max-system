<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>MAX STOCK - Final Protocol 2026</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{
            font-family:'Segoe UI',Arial,sans-serif;
            min-height:100vh;
            background: #0f1a2e; /* הרקע הכהה שלך */
            color: #fff;
            direction: rtl;
        }
        ::-webkit-scrollbar{width:6px}
        ::-webkit-scrollbar-thumb{background:#c9a84c;border-radius:3px}

        .container{max-width:850px;margin:20px auto;padding:15px}
        
        .glass-card {
            background: #16213e; /* ה-CardDark מהעיצוב שלך */
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 4px 30px rgba(0,0,0,0.5);
            border: 1px solid rgba(201, 168, 76, 0.2);
        }

        .header-main { text-align: center; margin-bottom: 30px; }
        .header-main h1 {
            font-size: 3rem;
            background: linear-gradient(135deg,#c9a84c,#e8c97a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
        }

        .lang-bar {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }

        .btn-lang {
            padding: 10px 20px;
            border-radius: 10px;
            border: 2px solid #c9a84c;
            background: transparent;
            color: #c9a84c;
            cursor: pointer;
            font-weight: bold;
            transition: 0.3s;
        }

        .btn-lang.active { background: #c9a84c; color: #fff; }

        .q-item {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            border-right: 5px solid #c9a84c;
        }

        input, select {
            width: 100%;
            padding: 14px;
            background: #fff;
            border: 2px solid #e0d5c0;
            border-radius: 12px;
            font-size: 16px;
            color: #1a202c;
            margin-top: 10px;
            outline: none;
        }

        .btn-gold {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg,#c9a84c,#a38637);
            border: none;
            border-radius: 14px;
            color: #fff;
            font-size: 19px;
            font-weight: 800;
            cursor: pointer;
            margin-top: 25px;
            box-shadow: 0 4px 15px rgba(201, 168, 76, 0.3);
        }

        .admin-row {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border: 1px solid rgba(201, 168, 76, 0.2);
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState } = React;

        const DB = {
            load: () => JSON.parse(localStorage.getItem("max_stock_p1") || "[]"),
            save: (l) => localStorage.setItem("max_stock_p1", JSON.stringify(l)),
            add: (i) => { const l=DB.load(); l.push({...i, id:Date.now(), ts:new Date().toLocaleString('he-IL')}); DB.save(l); }
        };

        const TRANSLATIONS = {
            he: { dir: "rtl", name: "שם מלא", dob: "תאריך לידה (DD.MM.YYYY)", start: "התחל שאלון", send: "שלח שאלון למערכת", title: "פרוטוקול קליטת עובדים", select: "בחר תשובה מהרשימה...", 
                questions: [
                    {q: "לקוח מחפש מוצר שחסר על המדף. מה תעשה?", a: ["אבדוק במחסן ואביא לו", "אבדוק במחשב אם קיים במלאי", "אגיד שחסר ואכוון למוצר דומה", "אמשיך בעבודתי הרגילה"]},
                    {q: "יש תור ארוך מאוד בקופות ואתה בסידור מדף?", a: ["אגש מיד לעזור בקופה בלי שיקראו לי", "אחכה שיקראו לי לעזור", "אמשיך לסדר עד שאסיים את המשימה", "אלך למחסן כדי לא להפריע"]},
                    {q: "ראית מוצר שבור או נוזל על הרצפה?", a: ["אנקה מיד ואדאג לבטיחות", "אדווח למנהל המשמרת", "אקרא לעובד ניקיון", "אעקוף את המפגע ואמשיך"]},
                    {q: "לקוח מתלונן על מחיר גבוה של מוצר?", a: ["אקשיב בסבלנות ואנסה להסביר בנועם", "אפנה אותו למנהל הסניף", "אגיד שזה המחיר ואין מה לעשות", "אתעלם ואעבור מחלקה"]},
                    {q: "קיבלת משימה מהמנהל שאתה לא אוהב?", a: ["אבצע אותה הכי טוב ומהר שאפשר", "אבצע ואז אבקש לגוון", "אעשה אותה לאט שלא יבקשו שוב", "אנסה להתחמק מהמשימה"]},
                    {q: "גילית שחבר לעבודה טעה בסידור?", a: ["אעזור לו לתקן בנעימות", "אסב את תשומת ליבו לטעות", "אדווח למנהל על הטעות שלו", "לא ענייני, כל אחד אחראי על שלו"]},
                    {q: "הגעת וראית שהמחלקה הפוכה לגמרי?", a: ["אתחיל לסדר לפי סדר דחיפות", "אשאל מנהל מאיפה להתחיל", "אסדר רק את האזור הקטן שלי", "אחכה להוראות מפורטות"]},
                    {q: "לקוח מתלבט לגבי קניית מתנה?", a: ["אציע אפשרויות ואעזור לו לבחור", "אכוון אותו לאזור המתנות", "אגיד שזה עניין של טעם אישי", "אפנה אותו לעובד אחר"]},
                    {q: "מצאת כסף על הרצפה בחנות?", a: ["אמסור מיד למנהל או קופה ראשית", "אשאל לקוחות מסביב אם איבדו", "אשים בקופת צדקה", "אשמור בכיס"]},
                    {q: "איזו צורת עבודה אתה מעדיף?", a: ["עבודה עם אחריות שבה אני רץ לבד", "עבודה בצוות עם שיתוף פעולה", "עבודה שאומרים לי בדיוק מה לעשות", "עבודה שקטה בלי הפרעות לקוחות"]},
                    {q: "לקוח דורש הנחה שאי אפשר לתת?", a: ["אסביר בנימוס את מדיניות הרשת", "אבדוק אם יש מבצע חלופי", "אשלח אותו לדבר עם המנהל", "אגיד פשוט 'לא'"]},
                    {q: "סימנת מחיר טעות על קבוצת מוצרים?", a: ["אתקן מיד ואדווח למנהל", "אשאל את המנהל איך לתקן", "אקווה שאף אחד לא ישים לב", "אשאיר את זה ככה"]},
                    {q: "המשמרת נגמרה והחנות עמוסה מאוד?", a: ["אשאר לעזור עד שיירגע העומס", "אסיים את המשימה הנוכחית ואלך", "אצא מיד - נגמר הזמן", "אלך בלי לעדכן אף אחד"]},
                    {q: "עובד אחר מבקש שתעשה משהו לא תקין?", a: ["אסרב בנימוס ואסביר את הנוהל", "אדווח למנהל המשמרת", "אזרום איתו באופן חד פעמי", "אעשה מה שביקש"]},
                    {q: "מה הדבר שהכי חשוב לך בעבודה?", a: ["להתקדם ולהצליח בארגון", "שירות מעולה ולקוח מרוצה", "סדר וארגון מושלם במחלקה", "המשכורת והשקט שלי"]}
                ]
            },
            en: { dir: "ltr", name: "Full Name", dob: "Birth Date", start: "Start", send: "Submit", title: "Recruitment Protocol", select: "Select answer...", questions: [] },
            ru: { dir: "ltr", name: "ФИО", dob: "Дата рождения", start: "Начать", send: "Отправить", title: "Протокол приема", select: "Выберите...", questions: [] },
            ar: { dir: "rtl", name: "الاسم الكامل", dob: "تاريخ الميلاد", start: "ابدأ", send: "إرسال", title: "بروتوكول التوظيف", select: "اختر إجابة...", questions: [] },
            th: { dir: "ltr", name: "ชื่อ-นามสกุล", dob: "วันเกิด", start: "เริ่ม", send: "ส่งข้อมูล", title: "ระเบียบการสรรหา", select: "เลือกคำตอบ...", questions: [] }
        };

        // שכפול השאלות לכל השפות (לצורך התצוגה המלאה בקוד)
        Object.keys(TRANSLATIONS).forEach(l => {
            if(l !== 'he') TRANSLATIONS[l].questions = TRANSLATIONS.he.questions.map(q => ({...q}));
        });

        function getSign(dob) {
            if(!dob || !dob.includes('.')) return "לא ידוע";
            const [d, m] = dob.split('.').map(Number);
            const signs = ["גדי","דלי","דגים","טלה","שור","תאומים","סרטן","אריה","בתולה","מאזניים","עקרב","קשת"];
            return signs[m % 12];
        }

        function App() {
            const [view, setView] = useState("home");
            const [lang, setLang] = useState("he");
            const [ans, setAns] = useState(Array(15).fill(null));
            const [user, setUser] = useState({ name: "", dob: "" });

            const T = TRANSLATIONS[lang];

            const handleFinish = () => {
                if(!user.name || !user.dob || ans.includes(null)) return alert("נא למלא הכל");
                const big = ans.filter(a => a === 0).length;
                DB.add({ ...user, 
                    style: big >= 9 ? "ראש גדול" : "ביצועיסט", 
                    sign: getSign(user.dob) 
                });
                alert("נשמר בהצלחה!");
                setView("home");
            };

            if(view === "home") return (
                <div className="container">
                    <div className="header-main"><h1>MAX STOCK</h1></div>
                    <div className="glass-card" style={{textAlign:'center'}}>
                        <div className="lang-bar">
                            {Object.keys(TRANSLATIONS).map(k => (
                                <button key={k} className={`btn-lang ${lang===k?'active':''}`} onClick={()=>setLang(k)}>{k.toUpperCase()}</button>
                            ))}
                        </div>
                        <h2 style={{color:'#c9a84c', marginBottom:'20px'}}>{T.title}</h2>
                        <button className="btn-gold" onClick={()=>setView("form")}>{T.start}</button>
                        <button onClick={()=>{if(prompt("Pass:")==="1234")setView("admin")}} style={{marginTop:'50px', opacity:0.05, background:'none', border:'none', color:'#fff'}}>Admin</button>
                    </div>
                </div>
            );

            if(view === "form") return (
                <div className="container" style={{ direction: T.dir }}>
                    <div className="glass-card">
                        <input type="text" placeholder={T.name} onChange={e=>setUser({...user, name:e.target.value})} />
                        <input type="text" placeholder={T.dob} onChange={e=>setUser({...user, dob:e.target.value})} />
                        <div style={{marginTop:'30px'}}>
                            {T.questions.map((q, i) => (
                                <div key={i} className="q-item">
                                    <p><strong>{i+1}. {q.q}</strong></p>
                                    <select onChange={e=>{const n=[...ans]; n[i]=parseInt(e.target.value); setAns(n);}}>
                                        <option value="">{T.select}</option>
                                        {q.a.map((txt, idx) => <option key={idx} value={idx}>{txt}</option>)}
                                    </select>
                                </div>
                            ))}
                        </div>
                        <button className="btn-gold" onClick={handleFinish}>{T.send}</button>
                    </div>
                </div>
            );

            if(view === "admin") return (
                <div className="container" style={{direction:'rtl'}}>
                    <div className="glass-card">
                        <h2 style={{color:'#c9a84c', marginBottom:'20px'}}>לוח מנהל - תוצאות</h2>
                        <button onClick={()=>setView("home")} style={{color:'#94a3b8', background:'none', border:'none', cursor:'pointer', marginBottom:'20px'}}>→ חזרה</button>
                        {DB.load().map((c, i) => (
                            <div key={i} className="admin-row">
                                <p><strong>{c.name}</strong> | {c.dob}</p>
                                <p style={{color:'#c9a84c'}}>אפיון: {c.style} | מזל: {c.sign}</p>
                                <p style={{fontSize:'12px', opacity:0.5}}>{c.ts}</p>
                            </div>
                        ))}
                    </div>
                </div>
            );
        }

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>
