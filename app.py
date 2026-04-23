<!DOCTYPE html>
<html lang="he">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>MAX STOCK - 5 Languages Protocol</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.2/babel.min.js"></script>
    <style>
        *{box-sizing:border-box;margin:0;padding:0}
        body{
            font-family:'Segoe UI',Arial,sans-serif;
            min-height:100vh;
            background: #0f1a2e;
            color: #fff;
            transition: all 0.3s;
        }
        ::-webkit-scrollbar{width:6px}
        ::-webkit-scrollbar-thumb{background:#c9a84c;border-radius:3px}

        .container{max-width:850px;margin:20px auto;padding:15px}
        .glass-card {
            background: #16213e;
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 4px 30px rgba(0,0,0,0.5);
            border: 1px solid rgba(201, 168, 76, 0.2);
        }
        
        .main-header { text-align: center; margin-bottom: 30px; }
        .main-header h1 {
            font-size: 2.8rem;
            background: linear-gradient(135deg,#c9a84c,#e8c97a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
        }

        .lang-bar {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }

        .btn-lang {
            padding: 8px 15px;
            border-radius: 8px;
            border: 1px solid #c9a84c;
            background: transparent;
            color: #c9a84c;
            cursor: pointer;
            font-weight: bold;
        }

        .btn-lang.active { background: #c9a84c; color: #fff; }

        .q-item {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 15px;
            border-right: 4px solid #c9a84c;
        }

        input, select {
            width: 100%;
            padding: 12px;
            background: #fff;
            border: 2px solid #e0d5c0;
            border-radius: 10px;
            font-size: 16px;
            color: #1a202c;
            margin-top: 8px;
        }

        .btn-gold {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg,#c9a84c,#a38637);
            border: none;
            border-radius: 12px;
            color: #fff;
            font-size: 18px;
            font-weight: 800;
            cursor: pointer;
            margin-top: 20px;
        }

        .admin-box {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 1px solid rgba(201, 168, 76, 0.2);
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState } = React;

        const DB = {
            load: () => JSON.parse(localStorage.getItem("max_5lang_v1") || "[]"),
            save: (l) => localStorage.setItem("max_5lang_v1", JSON.stringify(l)),
            add: (i) => { const l=DB.load(); l.push({...i, id:Date.now(), ts:new Date().toLocaleString('he-IL')}); DB.save(l); }
        };

        const TRANSLATIONS = {
            he: { dir: "rtl", name: "שם מלא", dob: "תאריך לידה", start: "התחל שאלון", send: "שלח שאלון", title: "פרוטוקול גיוס", select: "בחר תשובה...", 
                questions: [
                    {q: "לקוח מחפש מוצר שחסר על המדף. מה תעשה?", a: ["אבדוק במחסן ואביא לו", "אבדוק במחשב", "אגיד שחסר", "אמשיך בעבודתי"]},
                    {q: "יש תור ארוך בקופות?", a: ["אגש מיד לעזור", "אחכה שיקראו לי", "אמשיך בסידור", "אלך למחסן"]},
                    {q: "ראית מוצר שבור?", a: ["אנקה מיד", "אדווח למנהל", "אקרא לניקיון", "אעקוף"]}
                    // (כאן יופיעו שאר 15 השאלות בעברית)
                ]
            },
            en: { dir: "ltr", name: "Full Name", dob: "Date of Birth", start: "Start", send: "Submit", title: "Recruitment Protocol", select: "Select...",
                questions: [
                    {q: "Customer looking for missing item?", a: ["Check warehouse", "Check computer", "Say out of stock", "Continue working"]},
                    {q: "Long line at checkout?", a: ["Help immediately", "Wait to be called", "Continue sorting", "Go to warehouse"]},
                    {q: "Product broken on floor?", a: ["Clean immediately", "Tell manager", "Call cleaner", "Ignore"]}
                ]
            },
            ru: { dir: "ltr", name: "ФИО", dob: "Дата рождения", start: "Начать", send: "Отправить", title: "Протокол приема", select: "Выберите...",
                questions: [
                    {q: "Клиент ищет товар, которого нет?", a: ["Проверю склад", "Проверю компьютер", "Скажу нет в наличии", "Продолжу работу"]},
                    {q: "Очередь на кассе?", a: ["Помогу сразу", "Подожду вызова", "Продолжу выкладку", "Уйду на склад"]},
                    {q: "Разбитый товар?", a: ["Уберу сразу", "Скажу менеджеру", "Вызову уборку", "Пройду мимо"]}
                ]
            },
            ar: { dir: "rtl", name: "الاسم الكامل", dob: "تاريخ الميلاد", start: "ابدأ", send: "إرسال", title: "بروتوكول التوظيف", select: "اختر إجابة...",
                questions: [
                    {q: "زبون يبحث عن منتج مفقود؟", a: ["سأتحقق من المستودع", "سأتحقق من الكمبيوتر", "سأقول إنه غير متوفر", "سأواصل عملي"]},
                    {q: "طابور طويل عند الكاشير؟", a: ["سأذهب للمساعدة فورا", "سأنتظر من يناديني", "سأواصل ترتيب الرفوف", "سأذهب للمستودع"]},
                    {q: "منتج مكسور على الأرض؟", a: ["سأنظفه فورا", "سأخبر المدير", "سأطلب التنظيف", "سأتجاهله"]}
                ]
            },
            th: { dir: "ltr", name: "ชื่อ-นามสกุล", dob: "วันเกิด", start: "เริ่ม", send: "ส่งข้อมูล", title: "ระเบียบการสรรหา", select: "เลือกคำตอบ...",
                questions: [
                    {q: "ลูกค้าหาสินค้าไม่เจอ?", a: ["ไปเช็คที่คลังสินค้า", "เช็คในคอมพิวเตอร์", "บอกว่าของหมด", "ทำงานต่อ"]},
                    {q: "คิวยาวที่แคชเชียร์?", a: ["ไปช่วยทันที", "รอเรียก", "จัดของต่อ", "ไปที่คลังสินค้า"]},
                    {q: "สินค้าแตกบนพื้น?", a: ["ทำความสะอาดทันที", "บอกผู้จัดการ", "เรียกแม่บ้าน", "เดินผ่าน"]}
                ]
            }
        };

        function getAnalysis(dob, answers) {
            const bigCount = answers.filter(a => a === 0).length;
            const signs = ["גדי","דלי","דגים","טלה","שור","תאומים","סרטן","אריה","בתולה","מאזניים","עקרב","קשת"];
            const m = parseInt((dob || "01.01").split('.')[1]) || 1;
            return {
                style: bigCount >= 9 ? "ראש גדול" : "ביצועיסט",
                sign: signs[m % 12]
            };
        }

        function App() {
            const [page, setPage] = useState("home");
            const [lang, setLang] = useState("he");
            const [ans, setAns] = useState(Array(15).fill(null));
            const [info, setInfo] = useState({ name: "", dob: "" });

            const T = TRANSLATIONS[lang];

            const save = () => {
                DB.add({ ...info, answers: ans, analysis: getAnalysis(info.dob, ans) });
                alert("Saved / נשמר");
                setPage("home");
            };

            return (
                <div className="container" style={{ direction: T.dir }}>
                    <div className="main-header"><h1>MAX STOCK</h1></div>
                    
                    {page === "home" && (
                        <div className="glass-card" style={{textAlign:'center'}}>
                            <div className="lang-bar">
                                {Object.keys(TRANSLATIONS).map(k => (
                                    <button key={k} className={`btn-lang ${lang===k?'active':''}`} onClick={()=>setLang(k)}>
                                        {k.toUpperCase()}
                                    </button>
                                ))}
                            </div>
                            <h2 style={{color:'#c9a84c', marginBottom:'20px'}}>{T.title}</h2>
                            <button className="btn-gold" onClick={()=>setPage("form")}>{T.start}</button>
                            <button onClick={()=>setPage("admin")} style={{marginTop:'40px', opacity:0.1, background:'none', border:'none', color:'#fff'}}>Admin</button>
                        </div>
                    )}

                    {page === "form" && (
                        <div className="glass-card">
                            <input type="text" placeholder={T.name} onChange={e=>setInfo({...info, name:e.target.value})} />
                            <input type="text" placeholder={T.dob + " (DD.MM.YYYY)"} onChange={e=>setInfo({...info, dob:e.target.value})} />
                            <div style={{marginTop:'20px'}}>
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
                            <button className="btn-gold" onClick={save}>{T.send}</button>
                        </div>
                    )}

                    {page === "admin" && (
                        <div className="glass-card" style={{direction:'rtl'}}>
                            <h2 style={{color:'#c9a84c', marginBottom:20}}>ניהול מועמדים (עברית)</h2>
                            {DB.load().map((item, index) => (
                                <div key={index} className="admin-box">
                                    <p><strong>{item.name}</strong> | {item.dob}</p>
                                    <p style={{color:'#c9a84c'}}>אפיון: {item.analysis.style} | מזל: {item.analysis.sign}</p>
                                </div>
                            ))}
                            <button className="btn-gold" onClick={()=>setPage("home")}>חזרה</button>
                        </div>
                    )}
                </div>
            );
        }

        ReactDOM.createRoot(document.getElementById('root')).render(<App />);
    </script>
</body>
</html>
