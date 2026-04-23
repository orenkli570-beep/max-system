<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>מערכת קליטת עובדים - Premium</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <style>
        /* תצוגה ויזואלית מהפרוטוקול ששלחת */
        *{box-sizing:border-box;margin:0;padding:0}
        body{
            font-family:'Segoe UI',Arial,sans-serif;
            min-height:100vh;
            background: #0f172a; /* רקע כהה ויוקרתי */
            color: #f1f5f9;
            direction: rtl;
        }
        .container{max-width:850px;margin:40px auto;padding:20px}
        
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }

        .header-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #c9a84c 0%, #f1d27b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
            text-align: center;
        }

        .q-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            border-right: 4px solid #c9a84c;
            transition: transform 0.2s;
        }

        .q-card:hover { transform: translateX(-5px); }

        input, select {
            width: 100%;
            padding: 14px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(201, 168, 76, 0.3);
            border-radius: 12px;
            color: #fff;
            font-size: 16px;
            margin-top: 10px;
            outline: none;
        }

        input:focus { border-color: #c9a84c; }

        .btn-gold {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #c9a84c 0%, #a38637 100%);
            border: none;
            border-radius: 14px;
            color: #0f172a;
            font-weight: 800;
            font-size: 18px;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 10px 15px -3px rgba(201, 168, 76, 0.3);
        }

        .lang-btn {
            padding: 10px 20px;
            margin: 5px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255,255,255,0.05);
            color: #fff;
            cursor: pointer;
        }

        .lang-active {
            background: #c9a84c;
            color: #0f172a;
            font-weight: bold;
        }

        .admin-box {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid rgba(201, 168, 76, 0.2);
        }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #c9a84c; border-radius: 10px; }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        // --- לוגיקה ונתונים ---
        const DB = {
            load: () => JSON.parse(localStorage.getItem("max_premium_data") || "[]"),
            save: (l) => localStorage.setItem("max_premium_data", JSON.stringify(l)),
            add: (i) => { const l=DB.load(); l.push({...i, id:Date.now(), date:new Date().toLocaleString()}); DB.save(l); }
        };

        const LANGS = {
            he: { label:"עברית", dir:"rtl", welcome:"ברוכים הבאים", start:"התחל שאלון", send:"שלח נתונים", questions:[
                {q:"לקוח מחפש מוצר שחסר על המדף, מה תעשה?", a:["אבדוק מיד במחסן ואנסה להביא לו","אבדוק במחשב או אשאל אחראי","אעדכן שחסר במלאי","אמשיך בעבודתי"]},
                {q:"יש תור ארוך בקופות ואתה בסידור מדף?", a:["אגש מיד לעזור בקופה","אחכה שיקראו לי","אמשיך לסדר מדפים","אלך למחסן"]},
                {q:"ראית מוצר שבור על הרצפה?", a:["אנקה מיד ואדאג לבטיחות","אדווח למנהל המשמרת","אקרא לעובד ניקיון","אעקוף ואמשיך לעבוד"]}
                // ... המשך השאלות יופיעו כאן בקוד המלא
            ]},
            en: { label:"English", dir:"ltr", welcome:"Welcome", start:"Start Questionnaire", send:"Submit Data", questions:[
                {q:"Customer looking for missing item?", a:["Check warehouse","Check computer","Out of stock","Continue working"]}
            ]},
            ru: { label:"Русский", dir:"ltr", welcome:"Добро пожаловать", start:"Начать", send:"Отправить", questions:[] },
            ar: { label:"العربية", dir:"rtl", welcome:"أهلاً بك", start:"ابدأ", send:"إرسال", questions:[] },
            th: { label:"ภาษาไทย", dir:"ltr", welcome:"ยินดีต้อนรับ", start:"เริ่ม", send:"ส่ง", questions:[] }
        };

        function App() {
            const [view, setView] = useState("home");
            const [lang, setLang] = useState("he");
            const [name, setName] = useState("");
            const [dob, setDob] = useState("");
            const [answers, setAnswers] = useState(Array(15).fill(null));

            const L = LANGS[lang];

            const handleSubmit = () => {
                DB.add({ name, dob, answers });
                alert("הנתונים נשמרו בהצלחה!");
                setView("home");
            };

            if(view === "home") return (
                <div className="container">
                    <div className="glass-card" style={{textAlign:'center'}}>
                        <h1 className="header-title">MAX STOCK</h1>
                        <p style={{marginBottom:'30px', opacity:0.8}}>Recruitment & Analysis System</p>
                        <div style={{marginBottom:'30px'}}>
                            {Object.keys(LANGS).map(k => (
                                <button key={k} onClick={()=>setLang(k)} className={`lang-btn ${lang===k?'lang-active':''}`}>{LANGS[k].label}</button>
                            ))}
                        </div>
                        <button className="btn-gold" onClick={()=>setView("quiz")}>{L.start}</button>
                        <button onClick={()=>{if(prompt("Pass:")==="1234")setView("admin")}} style={{marginTop:'40px', background:'none', border:'none', color:'rgba(255,255,255,0.2)'}}>Admin Access</button>
                    </div>
                </div>
            );

            if(view === "quiz") return (
                <div className="container" style={{direction: L.dir}}>
                    <div className="glass-card">
                        <h2 className="header-title" style={{fontSize:'1.8rem'}}>פרטי מועמד</h2>
                        <input type="text" placeholder="שם מלא / Full Name" onChange={e=>setName(e.target.value)} />
                        <input type="text" placeholder="תאריך לידה / DOB (DD.MM.YYYY)" onChange={e=>setDob(e.target.value)} />
                        
                        <div style={{marginTop:'40px'}}>
                            {L.questions.map((q, i) => (
                                <div key={i} className="q-card">
                                    <p><strong>{i+1}. {q.q}</strong></p>
                                    <select onChange={e=>{const n=[...answers]; n[i]=e.target.value; setAnswers(n);}}>
                                        <option value="">בחר תשובה...</option>
                                        {q.a.map((opt,idx)=><option key={idx} value={idx}>{opt}</option>)}
                                    </select>
                                </div>
                            ))}
                        </div>
                        <button className="btn-gold" onClick={handleSubmit}>{L.send}</button>
                    </div>
                </div>
            );

            if(view === "admin") return (
                <div className="container" style={{direction:'rtl'}}>
                    <h1 className="header-title">ניהול מועמדים</h1>
                    <button onClick={()=>setView("home")} style={{color:'#c9a84c', background:'none', border:'none', marginBottom:'20px'}}>חזרה</button>
                    {DB.load().map((c, i) => (
                        <div key={i} className="admin-box">
                            <h3>{c.name} <small style={{opacity:0.6}}>{c.dob}</small></h3>
                            <p style={{color:'#c9a84c'}}>נרשם ב: {c.date}</p>
                        </div>
                    ))}
                </div>
            );
        }

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>
