import streamlit as st
import google.generativeai as genai
import json
import base64
import os
from datetime import date

# ─── إعدادات الصفحة ───────────────────────────────────────────────────────────
st.set_page_config(page_title="مولد المبادرات", layout="wide", page_icon="💡")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.stApp, html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl;
    text-align: right;
    background: #f0f2f5;
}

/* ── الرأس ── */
.app-header {
    background: linear-gradient(135deg, #1a0a2e 0%, #3d1a6b 50%, #1a0a2e 100%);
    border-radius: 20px;
    padding: 40px 50px;
    margin-bottom: 30px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(61,26,107,0.4);
}
.app-header::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 30% 50%, rgba(0,200,160,0.15) 0%, transparent 60%),
                radial-gradient(ellipse at 70% 50%, rgba(93,58,119,0.3) 0%, transparent 60%);
}
.app-header h1 {
    color: #ffffff !important;
    font-size: 2.4rem !important;
    font-weight: 900 !important;
    margin: 0 0 10px 0 !important;
    position: relative; z-index: 1;
    text-shadow: 0 2px 20px rgba(0,0,0,0.3);
}
.app-header p {
    color: rgba(255,255,255,0.75) !important;
    font-size: 1.05rem; margin: 0;
    position: relative; z-index: 1;
}

/* ── تذييل التطبيق ── */
.app-footer {
    text-align: center;
    margin-top: 50px;
    padding: 20px;
    color: #aaa;
    font-size: 0.85rem;
    border-top: 1px solid #e2e6ed;
}
.app-footer a {
    color: #3d1a6b;
    font-weight: 700;
    text-decoration: none;
}

/* ── البطاقات ── */
.card {
    background: #ffffff;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
}
.card-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #3d1a6b;
    border-right: 4px solid #00c8a0;
    padding-right: 12px;
    margin-bottom: 20px;
}

/* ── إصلاح لون النص في حقول الإدخال ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stDateInput > div > div > input {
    background-color: #ffffff !important;
    border: 1.5px solid #c8d0de !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    font-family: 'Tajawal', sans-serif !important;
    color: #1c1c2e !important;
    transition: border-color .2s, box-shadow .2s;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: #9aa0b4 !important;
    opacity: 1 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #3d1a6b !important;
    box-shadow: 0 0 0 3px rgba(61,26,107,0.12) !important;
    background: #fff !important;
    color: #1c1c2e !important;
}

/* ── الأزرار ── */
.stButton > button {
    background: linear-gradient(135deg, #3d1a6b 0%, #1a0a2e 100%) !important;
    color: #fff !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 14px 28px !important;
    width: 100% !important;
    transition: transform .2s, box-shadow .2s !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(61,26,107,0.4) !important;
}

/* ── حاوية النتائج ── */
.result-box {
    background: #fff;
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.08);
    border-top: 5px solid #00c8a0;
    margin-top: 30px;
}
.result-title {
    text-align: center;
    font-size: 1.3rem;
    font-weight: 900;
    color: #1a0a2e;
    border-bottom: 2px solid #00c8a0;
    padding-bottom: 14px;
    margin-bottom: 24px;
}

/* ── تسميات ── */
label, .stLabel { font-weight: 600 !important; color: #2e2e4a !important; }

/* ── زر التحميل ── */
.download-btn {
    display: block; text-align: center;
    background: linear-gradient(135deg, #00c8a0 0%, #00957a 100%);
    color: #fff; padding: 18px; border-radius: 14px;
    text-decoration: none; font-size: 1.15rem; font-weight: 900;
    box-shadow: 0 6px 20px rgba(0,200,160,0.35);
    margin-top: 10px;
}

/* ── الشريط الجانبي ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a0a2e 0%, #2d1155 100%) !important;
}
section[data-testid="stSidebar"] * { color: #e8e0f0 !important; }

/* إصلاح لون النص في الشريط الجانبي */
section[data-testid="stSidebar"] .stTextInput > div > div > input,
section[data-testid="stSidebar"] .stTextArea > div > div > textarea,
section[data-testid="stSidebar"] .stSelectbox > div > div > div,
section[data-testid="stSidebar"] .stDateInput > div > div > input {
    background: #ffffff !important;
    border-color: #c8d0de !important;
    color: #1a0a2e !important;
}
section[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder,
section[data-testid="stSidebar"] .stTextArea > div > div > textarea::placeholder {
    color: #9aa0b4 !important;
}

/* تسميات الشريط الجانبي */
section[data-testid="stSidebar"] label {
    color: #d4c8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── قراءة مفتاح API من البيئة أو من المستخدم ────────────────────────────────
ENV_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ─── الشريط الجانبي ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")

    if not ENV_API_KEY:
        api_key_input = st.text_input("🔑 مفتاح Google Gemini API:", type="password",
                                       help="أدخل مفتاحك هنا للاستخدام المحلي")
        st.caption("💡 للنشر على Streamlit Cloud: أضف المفتاح في Secrets باسم GEMINI_API_KEY")
    else:
        api_key_input = ""
        st.success("✅ مفتاح API محمّل من الإعدادات")

    st.markdown("---")
    st.markdown("### 📋 بيانات الوثيقة الرسمية")
    teacher_name   = st.text_input("👤 اسم المعلم / المنفذ:")
    school_name    = st.text_input("🏫 اسم المدرسة:")
    education_dept = st.text_input("🏢 إدارة التعليم:")
    academic_year  = st.text_input("📅 العام الدراسي:", value="1446-1447هـ")
    semester       = st.selectbox("📖 الفصل الدراسي:", ["الفصل الأول", "الفصل الثاني"])
    doc_date       = st.date_input("🗓️ تاريخ الوثيقة:", value=date.today())

api_key = ENV_API_KEY if ENV_API_KEY else api_key_input

# ─── الرأس ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <h1>💡 المولد الذكي للمبادرات</h1>
  <p>أدخل الفكرة الأساسية، واترك الذكاء الاصطناعي يصوغها بأسلوب تربوي معتمد</p>
</div>
""", unsafe_allow_html=True)

# ─── عناصر الأداء ─────────────────────────────────────────────────────────────
evaluation_elements = [
    "أداء الواجبات الوظيفية", "التفاعل مع المجتمع المهني", "التفاعل مع أولياء الأمور",
    "التنويع في استراتيجيات التدريس", "تحسين نتائج المتعلمين", "إعداد وتنفيذ خطة التعلم",
    "توظيف تقنيات ووسائل التعلم", "تهيئة بيئة تعليمية", "الإدارة الصفية",
    "تحليل نتائج المتعلمين وتشخيص مستوياتهم", "تنوع أساليب التقويم"
]

# ─── بطاقة الإدخال ────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">📌 معلومات المبادرة</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    initiative_title = st.text_input("عنوان المبادرة:", placeholder="مثال: نجوم القراءة")
with col2:
    selected_element = st.selectbox("عنصر الأداء الوظيفي المستهدف:", evaluation_elements)
with col3:
    grade_level = st.selectbox("المرحلة الدراسية:", ["ابتدائي", "متوسط", "ثانوي", "جميع المراحل"])

col4, col5 = st.columns(2)
with col4:
    subject_area = st.text_input("المادة الدراسية / المجال:", placeholder="مثال: اللغة العربية")
with col5:
    duration = st.selectbox("مدة تنفيذ المبادرة:", ["أسبوع", "شهر", "فصل دراسي", "عام دراسي", "مستمرة"])

initiative_hint = st.text_area(
    "✍️ فكرة مبدئية أو ملاحظات توجيهية (اختياري):",
    placeholder="مثال: أريد المبادرة أن تركز على استخدام التقنية في تحفيز الطلاب الضعاف...",
    height=90
)
st.markdown('</div>', unsafe_allow_html=True)

# ─── الجلسة ───────────────────────────────────────────────────────────────────
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None

# ─── زر التوليد ───────────────────────────────────────────────────────────────
if st.button("🚀 صياغة المبادرة باحترافية"):
    if not api_key:
        st.error("⚠️ يرجى إدخال مفتاح API في القائمة الجانبية أولاً.")
    elif not initiative_title.strip():
        st.warning("⚠️ يرجى إدخال عنوان المبادرة للبدء.")
    else:
        with st.spinner("⏳ جاري تحليل الفكرة وصياغتها بأسلوب تربوي معتمد..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # إعداد ديناميكية الأوامر بناءً على مدة التنفيذ
                if duration == "أسبوع":
                    goals_count = 2
                    steps_count = 3
                    indicators_count = 2
                    scope_hint = "نظراً لأن مدة التنفيذ قصيرة جداً (أسبوع واحد فقط)، اجعل المبادرة سريعة التطبيق، محددة النطاق، وخطواتها يومية أو سريعة الإنجاز."
                elif duration == "شهر":
                    goals_count = 3
                    steps_count = 4
                    indicators_count = 3
                    scope_hint = "بما أن مدة التنفيذ شهر، اجعل المبادرة متوسطة النطاق مع خطوات موزعة لتلائم أسابيع الشهر."
                else: # فصل دراسي، عام دراسي، مستمرة
                    goals_count = 4
                    steps_count = 6
                    indicators_count = 4
                    scope_hint = "نظراً لأن مدة التنفيذ طويلة وممتدة، اجعل المبادرة عميقة، شاملة، وذات خطوات مرحلية تغطي فترات زمنية ممتدة."

                prompt = f"""
أنت خبير تربوي في وزارة التعليم السعودية، لديك خبرة واسعة في صياغة المبادرات المدرسية الإبداعية وخطط التحسين.
بناءً على المعطيات التالية:
- عنوان المبادرة: {initiative_title}
- عنصر الأداء الوظيفي المرتبط: {selected_element}
- المرحلة الدراسية: {grade_level}
- المادة / المجال: {subject_area if subject_area else 'عام'}
- مدة التنفيذ: {duration} ({scope_hint})
- ملاحظات إضافية: {initiative_hint if initiative_hint else 'لا يوجد'}

توجيهات إجبارية للصياغة:
1. الفئة المستفيدة: يجب أن تكون واقعية، محددة جداً ومباشرة (مثال: طلاب الصف الأول متوسط المتعثرين في القراءة، وليس "الطلاب" بشكل عام).
2. التنسيق والتعداد: عند كتابة المشكلة المعالجة، الأهداف، وخطوات التنفيذ، **يجب** وضع علامة السطر الجديد (\\n) بين كل نقطة ونقطة، لتظهر العناصر تحت بعضها بشكل مرتب وليس بجانب بعضها المتصل.

قم بتأليف مبادرة مدرسية متكاملة. يجب أن يكون الرد **فقط** بصيغة JSON صالح
(بدون أي نصوص إضافية أو علامات تنسيق مثل ```json) ويحتوي على المفاتيح التالية حصراً:
{{
    "type": "نوع المبادرة (مثال: تربوية / تقنية / علمية / اجتماعية... إلخ)",
    "exec_desc": "الوصف التنفيذي (جملة واحدة جذابة تصف آلية العمل)",
    "full_desc": "وصف المبادرة (شرح مفصل بأسلوب احترافي لا يقل عن 4 أسطر)",
    "problems": "المشكلة المعالجة (اكتب 3 نقاط واستخدم \\n بين كل نقطة والأخرى للنزول لسطر جديد)",
    "solution": "الحل المبتكر (شرح إبداعي كيف تعالج المبادرة هذه المشكلة ضمن فترة {duration})",
    "goals": "الأهداف الاستراتيجية ({goals_count} أهداف، واستخدم \\n بين كل هدف والآخر)",
    "steps": "خطوات التنفيذ ({steps_count} خطوات عملية، واستخدم \\n بين كل خطوة والأخرى)",
    "indicators": "مؤشرات النجاح ({indicators_count} مؤشرات، واستخدم \\n بين كل مؤشر والآخر)",
    "resources": "الموارد المطلوبة (البشرية والمادية والتقنية بإيجاز)",
    "target": "الفئة المستفيدة (محددة وواقعية جداً مع دورها المباشر، وتجنب التعميم المطلق)"
}}
"""
                response = model.generate_content(prompt)
                result_text = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.generated_data = json.loads(result_text)

            except Exception as e:
                st.error(f"⚠️ حدث خطأ. تأكد من صحة مفتاح API واتصالك بالإنترنت.\n\nالتفاصيل: {e}")

# ─── عرض وتعديل النتائج ───────────────────────────────────────────────────────
if st.session_state.generated_data:
    data = st.session_state.generated_data

    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown('<div class="result-title">📝 مسودة المبادرة — قابلة للتعديل قبل التصدير</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        ed_type      = st.text_input("نوع المبادرة:", value=data.get('type', ''))
        ed_exec      = st.text_area("الوصف التنفيذي:", value=data.get('exec_desc', ''), height=110)
        ed_desc      = st.text_area("وصف المبادرة:", value=data.get('full_desc', ''), height=160)
        ed_target    = st.text_area("الفئة المستفيدة:", value=data.get('target', ''), height=110)
        ed_resources = st.text_area("الموارد المطلوبة:", value=data.get('resources', ''), height=110)
    with col_b:
        ed_problems   = st.text_area("المشكلة المعالجة:", value=data.get('problems', ''), height=160)
        ed_solution   = st.text_area("الحل المبتكر:", value=data.get('solution', ''), height=110)
        ed_goals      = st.text_area("الأهداف الاستراتيجية:", value=data.get('goals', ''), height=110)
        ed_steps      = st.text_area("خطوات التنفيذ:", value=data.get('steps', ''), height=130)
        ed_indicators = st.text_area("مؤشرات النجاح:", value=data.get('indicators', ''), height=110)

    st.markdown('</div>', unsafe_allow_html=True)

    # ─── توليد HTML احترافي ───────────────────────────────────────────────────
    def nl2br(text):
        return text.replace('\n', '<br>')

    def meta_item(label, value):
        if value:
            return f'<div class="meta-item"><div class="mi-label">{label}</div><div class="mi-value">{value}</div></div>'
        return ''

    def generate_html():
        formatted_date = doc_date.strftime("%Y/%m/%d") if doc_date else ""

        meta_items = "".join([
            meta_item("اسم المنفذ", teacher_name),
            meta_item("المدرسة", school_name),
            meta_item("إدارة التعليم", education_dept),
            meta_item("العام الدراسي", academic_year),
            meta_item("الفصل الدراسي", semester),
            meta_item("المرحلة", grade_level),
            meta_item("مدة التنفيذ", duration),
            meta_item("تاريخ الوثيقة", formatted_date),
        ])

        return f"""<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>مبادرة – {initiative_title}</title>
<style>
  @import url('[https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap](https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&display=swap)');

  :root {{
    --purple-dark:  #1a0a2e;
    --purple-main:  #3d1a6b;
    --purple-light: #6b3fa0;
    --teal:         #00c8a0;
    --teal-dark:    #00957a;
    --bg:           #f4f6fb;
    --text:         #1c1c2e;
    --border:       #dde2f0;
    --section-bg:   #fafbff;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Tajawal', sans-serif;
    background: #e8eaf2;
    color: var(--text);
    font-size: 13pt;
    line-height: 1.9;
  }}

  .page {{
    max-width: 870px;
    margin: 20px auto;
    background: #fff;
    box-shadow: 0 8px 40px rgba(0,0,0,0.15);
    border-radius: 4px;
    overflow: hidden;
  }}

  /* ── Banner ── */
  .banner {{
    background: linear-gradient(135deg, var(--purple-dark) 0%, var(--purple-main) 55%, #5d2a8b 100%);
    padding: 36px 44px 30px;
    position: relative;
    overflow: hidden;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .banner::after {{
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 80% 50%, rgba(0,200,160,0.18) 0%, transparent 55%);
  }}
  .banner-inner {{ position: relative; z-index: 1; }}
  .ministry-label {{
    font-size: 10.5pt; color: rgba(255,255,255,0.55);
    margin-bottom: 8px; letter-spacing: .5px;
  }}
  .banner h1 {{
    font-size: 24pt; font-weight: 900; color: #fff;
    text-shadow: 0 2px 12px rgba(0,0,0,0.3);
    margin-bottom: 5px;
  }}
  .banner .subtitle {{
    font-size: 12pt; color: rgba(255,255,255,0.65);
  }}
  .type-badge {{
    display: inline-block;
    background: var(--teal);
    color: #fff; font-weight: 800;
    padding: 3px 16px; border-radius: 30px;
    font-size: 10.5pt; margin-top: 10px;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  /* ── Meta Bar ── */
  .meta-bar {{
    background: #2a1050;
    display: flex; flex-wrap: wrap;
    border-bottom: 3px solid var(--teal);
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .meta-item {{
    flex: 1 1 130px;
    padding: 10px 16px;
    border-left: 1px solid rgba(255,255,255,0.07);
  }}
  .meta-item:last-child {{ border-left: none; }}
  .mi-label {{
    font-size: 8.5pt; color: rgba(255,255,255,0.45);
    margin-bottom: 2px; white-space: nowrap;
  }}
  .mi-value {{
    font-size: 10.5pt; font-weight: 700; color: #fff;
    white-space: nowrap;
  }}

  /* ── Body ── */
  .body {{ padding: 32px 40px 24px; }}

  /* ── Exec Highlight ── */
  .exec-box {{
    background: linear-gradient(135deg, #f0ebff 0%, #e8f9f5 100%);
    border: 2px solid var(--purple-light);
    border-right: 5px solid var(--teal);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 24px;
    white-space: pre-line; /* لضمان نزول السطر في التعداد */
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .exec-box .eb-title {{
    font-weight: 900; font-size: 12pt; color: var(--purple-main); margin-bottom: 5px;
  }}
  .exec-box .eb-body {{
    font-size: 12pt; color: #333; line-height: 1.9;
  }}

  /* ── Section ── */
  .section {{
    margin-bottom: 20px;
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .sec-header {{
    display: flex; align-items: center; gap: 10px; margin-bottom: 8px;
  }}
  .sec-icon {{
    width: 32px; height: 32px; border-radius: 8px;
    background: linear-gradient(135deg, var(--purple-main), var(--purple-light));
    display: flex; align-items: center; justify-content: center;
    font-size: 14pt; flex-shrink: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .sec-label {{
    font-size: 12pt; font-weight: 800; color: var(--purple-main);
    border-bottom: 2.5px solid var(--teal); padding-bottom: 3px; flex: 1;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .sec-body {{
    background: var(--section-bg);
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 12pt; color: var(--text); line-height: 2;
    white-space: pre-line; /* لضمان نزول السطر في التعداد */
  }}

  /* ── Grid Layouts ── */
  .grid-2 {{
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 16px; margin-bottom: 20px;
  }}
  .grid-3 {{
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: 16px; margin-bottom: 20px;
  }}

  /* ── Full-width description ── */
  .full-section {{ margin-bottom: 20px; break-inside: avoid; page-break-inside: avoid; }}

  /* ── Steps ── */
  .steps-body {{
    background: var(--section-bg);
    border: 1.5px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 12pt; line-height: 2.1;
    white-space: pre-line; /* لضمان نزول السطر في التعداد */
  }}

  /* ── Indicator Cards ── */
  .ind-card {{
    background: linear-gradient(135deg, var(--purple-main), var(--purple-light));
    border-radius: 12px; padding: 18px 14px;
    text-align: center; color: #fff;
    break-inside: avoid; page-break-inside: avoid;
    white-space: pre-line;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .ind-icon {{ font-size: 20pt; margin-bottom: 6px; }}
  .ind-text {{ font-size: 10.5pt; opacity: .9; line-height: 1.6; }}

  /* ── Footer ── */
  .footer {{
    background: var(--purple-dark);
    padding: 14px 40px;
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 8px;
    border-top: 3px solid var(--teal);
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .footer-text {{ color: rgba(255,255,255,0.45); font-size: 9.5pt; }}
  .footer-badge {{
    background: var(--teal); color: #fff;
    padding: 4px 14px; border-radius: 20px;
    font-size: 9.5pt; font-weight: 700;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  /* ── Print Settings ── */
  @media print {{
    @page {{ size: A4 portrait; margin: 8mm 10mm; }}
    body {{ background: #fff; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .page {{ margin: 0; max-width: 100%; box-shadow: none; border-radius: 0; }}
    .grid-2 {{ grid-template-columns: 1fr 1fr; }}
    .grid-3 {{ grid-template-columns: 1fr 1fr 1fr; }}
    .section, .full-section, .ind-card, .exec-box {{
      break-inside: avoid; page-break-inside: avoid;
    }}
    .body {{ padding: 20px 28px 16px; }}
  }}
</style>
</head>
<body>
<div class="page">

  <div class="banner">
    <div class="banner-inner">
      <div class="ministry-label">🏫 وزارة التعليم – المملكة العربية السعودية</div>
      <h1>💡 {initiative_title}</h1>
      <div class="subtitle">{selected_element}</div>
      <span class="type-badge">{ed_type}</span>
    </div>
  </div>

  <div class="meta-bar">{meta_items}</div>

  <div class="body">

    <div class="exec-box">
      <div class="eb-title">📌 الوصف التنفيذي</div>
      <div class="eb-body">{nl2br(ed_exec)}</div>
    </div>

    <div class="full-section">
      <div class="sec-header">
        <div class="sec-icon">📄</div>
        <div class="sec-label">وصف المبادرة</div>
      </div>
      <div class="sec-body">{nl2br(ed_desc)}</div>
    </div>

    <div class="grid-2">
      <div class="section">
        <div class="sec-header">
          <div class="sec-icon">⚠️</div>
          <div class="sec-label">المشكلة المعالجة</div>
        </div>
        <div class="sec-body">{nl2br(ed_problems)}</div>
      </div>
      <div class="section">
        <div class="sec-header">
          <div class="sec-icon">💡</div>
          <div class="sec-label">الحل المبتكر</div>
        </div>
        <div class="sec-body">{nl2br(ed_solution)}</div>
      </div>
    </div>

    <div class="full-section">
      <div class="sec-header">
        <div class="sec-icon">🎯</div>
        <div class="sec-label">الأهداف الاستراتيجية</div>
      </div>
      <div class="sec-body">{nl2br(ed_goals)}</div>
    </div>

    <div class="full-section">
      <div class="sec-header">
        <div class="sec-icon">📋</div>
        <div class="sec-label">خطوات التنفيذ</div>
      </div>
      <div class="steps-body">{nl2br(ed_steps)}</div>
    </div>

    <div class="grid-2">
      <div class="section">
        <div class="sec-header">
          <div class="sec-icon">👥</div>
          <div class="sec-label">الفئة المستفيدة</div>
        </div>
        <div class="sec-body">{nl2br(ed_target)}</div>
      </div>
      <div class="section">
        <div class="sec-header">
          <div class="sec-icon">🛠️</div>
          <div class="sec-label">الموارد المطلوبة</div>
        </div>
        <div class="sec-body">{nl2br(ed_resources)}</div>
      </div>
    </div>

    <div class="sec-header" style="margin-bottom:12px;">
      <div class="sec-icon">📊</div>
      <div class="sec-label">مؤشرات النجاح</div>
    </div>
    <div class="grid-3" style="margin-bottom:8px;">
      <div class="ind-card">
        <div class="ind-icon">✅</div>
        <div class="ind-text">{nl2br(ed_indicators.split(chr(10))[0] if ed_indicators else '')}</div>
      </div>
      <div class="ind-card">
        <div class="ind-icon">📈</div>
        <div class="ind-text">{nl2br(ed_indicators.split(chr(10))[1] if len(ed_indicators.split(chr(10))) > 1 else '')}</div>
      </div>
      <div class="ind-card">
        <div class="ind-icon">🏆</div>
        <div class="ind-text">{nl2br(ed_indicators.split(chr(10))[2] if len(ed_indicators.split(chr(10))) > 2 else '')}</div>
      </div>
    </div>

  </div><div class="footer">
    <div class="footer-text">وثيقة مبادرة مدرسية • المولد الذكي للمبادرات</div>
    <div class="footer-badge">✅ {ed_type}</div>
  </div>

</div><script>window.onload = function() {{ window.print(); }};</script>
</body>
</html>"""

    html_out = generate_html()
    b64 = base64.b64encode(html_out.encode('utf-8')).decode()
    file_name = f"مبادرة_{initiative_title.replace(' ', '_')}.html"

    st.markdown(f"""
    <a class="download-btn"
       href="data:text/html;charset=utf-8;base64,{b64}"
       download="{file_name}">
      🖨️ تحميل وثيقة المبادرة — جاهزة للطباعة A4
    </a>
    """, unsafe_allow_html=True)

# ─── تذييل التطبيق ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
  صُمِّم بـ ❤️ بواسطة <strong>مقابل دعوة في ظهر الغيب</strong> &nbsp;|&nbsp;
  مدعوم بالذكاء الاصطناعي Google Gemini
</div>
""", unsafe_allow_html=True)
