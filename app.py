import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os
from dotenv import load_dotenv

# Konfiguracja strony
st.set_page_config(
    page_title="AutoWise",
    page_icon="🚘",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Ładowanie klucza API
# Próbuje pobrać z pliku .env (lokalnie) LUB z sekretów Streamlit Cloud
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("Brak klucza API Google Gemini. Ustaw GOOGLE_API_KEY w zmiennych środowiskowych lub .streamlit/secrets.toml")
    st.stop()

genai.configure(api_key=api_key)

# --- TŁUMACZENIA ---
TRANSLATIONS = {
    "pl": {
        "title": "AutoWise",
        "subtitle_diag": "Zaawansowana Diagnostyka Pojazdowa",
        "subtitle_tune": "Inżynieria Motorsportu & Tuning",
        "tab_diag": "Diagnostyka",
        "tab_tune": "Tuning",
        "vehicle": "Pojazd",
        "engine": "Silnik",
        "desc_label_diag": "Opis Usterki",
        "desc_label_tune": "Cele / Budżet",
        "placeholder_diag": "Opisz problem. Staraj się jak najdokładniej opisać usterkę i wszystko co jej towarzyszy (dźwięki, wibracje).",
        "placeholder_tune": "Np. Silnik 2.0 TDI, celuję w 200KM+. Budżet 5000 zł.",
        "analyze_btn_diag": "Rozpocznij Diagnozę",
        "analyze_btn_tune": "Generuj Plan Tuningu",
        "upload_label": "Dodaj zdjęcie (opcjonalnie)",
        "analyzing": "Analiza techniczna...",
        "refine_label": "Doprecyzuj / Dodaj szczegóły",
        "refine_btn": "Aktualizuj",
        "result_severity": "Powaga",
        "result_safety": "Bezpieczeństwo",
        "result_causes": "Potencjalne Przyczyny",
        "result_tip": "Porada Eksperta",
        "tune_power": "Przyrost Mocy",
        "tune_cost": "Szacowany Koszt",
        "tune_rel": "Wpływ na Trwałość",
        "tune_parts": "Rekomendowane Części",
        "tune_pros": "Zalety",
        "tune_cons": "Wady i Ryzyka",
        "vehicles": {"Car": "Samochód", "Motorcycle": "Motocykl", "Truck": "Ciężarówka", "Other": "Inny"},
        "engines": {"Petrol": "Benzyna", "Diesel": "Diesel", "LPG": "LPG", "Hybrid": "Hybryda", "Electric": "Elektryczny"},
        "off_topic": "Pytanie nie jest związane z motoryzacją. Proszę zapytać ponownie."
    },
    "en": {
        "title": "AutoWise",
        "subtitle_diag": "Advanced Vehicle Diagnostics",
        "subtitle_tune": "Motorsport Engineering & Tuning",
        "tab_diag": "Diagnostics",
        "tab_tune": "Tuning",
        "vehicle": "Vehicle",
        "engine": "Engine",
        "desc_label_diag": "Fault Description",
        "desc_label_tune": "Goals / Budget",
        "placeholder_diag": "Describe the problem accurately (sounds, vibrations, context).",
        "placeholder_tune": "E.g. 2.0 TDI engine, aiming for 200HP+. Budget $1500.",
        "analyze_btn_diag": "Start Diagnosis",
        "analyze_btn_tune": "Generate Tuning Plan",
        "upload_label": "Add photo (optional)",
        "analyzing": "Technical Analysis...",
        "refine_label": "Refine / Add Details",
        "refine_btn": "Update",
        "result_severity": "Severity",
        "result_safety": "Safety",
        "result_causes": "Potential Causes",
        "result_tip": "Expert Tip",
        "tune_power": "Power Gain",
        "tune_cost": "Est. Cost",
        "tune_rel": "Durability Impact",
        "tune_parts": "Recommended Parts",
        "tune_pros": "Pros",
        "tune_cons": "Cons",
        "vehicles": {"Car": "Car", "Motorcycle": "Motorcycle", "Truck": "Truck", "Other": "Other"},
        "engines": {"Petrol": "Petrol", "Diesel": "Diesel", "LPG": "LPG", "Hybrid": "Hybrid", "Electric": "Electric"},
        "off_topic": "The question is not related to automotive topics. Please ask again."
    },
    "de": {
        "title": "AutoWise",
        "subtitle_diag": "Erweiterte Fahrzeugdiagnose",
        "subtitle_tune": "Motorsporttechnik & Tuning",
        "tab_diag": "Diagnose",
        "tab_tune": "Tuning",
        "vehicle": "Fahrzeug",
        "engine": "Motor",
        "desc_label_diag": "Fehlerbeschreibung",
        "desc_label_tune": "Ziele / Budget",
        "placeholder_diag": "Beschreiben Sie das Problem so genau wie möglich.",
        "placeholder_tune": "Z.B. 2.0 TDI Motor, Ziel 200PS+. Budget 1500€.",
        "analyze_btn_diag": "Diagnose starten",
        "analyze_btn_tune": "Tuning-Plan erstellen",
        "upload_label": "Foto hinzufügen (optional)",
        "analyzing": "Technische Analyse...",
        "refine_label": "Präzisieren / Details hinzufügen",
        "refine_btn": "Aktualisieren",
        "result_severity": "Schweregrad",
        "result_safety": "Sicherheit",
        "result_causes": "Mögliche Ursachen",
        "result_tip": "Experten-Tipp",
        "tune_power": "Leistungssteigerung",
        "tune_cost": "Geschätzte Kosten",
        "tune_rel": "Einfluss auf Haltbarkeit",
        "tune_parts": "Empfohlene Teile",
        "tune_pros": "Vorteile",
        "tune_cons": "Nachteile",
        "vehicles": {"Car": "Auto", "Motorcycle": "Motorrad", "Truck": "LKW", "Other": "Andere"},
        "engines": {"Petrol": "Benzin", "Diesel": "Diesel", "LPG": "LPG", "Hybrid": "Hybrid", "Electric": "Elektrisch"},
        "off_topic": "Die Frage bezieht sich nicht auf Kraftfahrzeuge. Bitte fragen Sie erneut."
    }
}

# --- LOGIKA AI ---

def get_gemini_model():
    # Używamy bezpieczniejszego parsowania
    return genai.GenerativeModel('gemini-1.5-flash')

def analyze_request(mode, vehicle, engine, desc, lang, image=None, context_history=""):
    model = get_gemini_model()
    lang_name = {"pl": "POLISH", "en": "ENGLISH", "de": "GERMAN"}[lang]
    
    t = TRANSLATIONS[lang]

    base_instruction = f"""
    You are a WORLD-CLASS AUTOMOTIVE ENGINEER.
    Output Language: {lang_name}.
    IMPORTANT: Respond ONLY with valid JSON. Do not include markdown formatting like ```json ... ```.
    
    CRITICAL RULE: If the user asks about NON-AUTOMOTIVE topics (cooking, weather, politics), 
    return a JSON with 'summary': '{t['off_topic']}' and empty lists/nulls for other fields.
    """

    if mode == "Diagnosis":
        system_instruction = base_instruction + f"""
        Focus on mechanical diagnosis for a {vehicle} with {engine} engine.
        Return JSON structure:
        {{
            "summary": "Technical summary",
            "severity": "Low/Medium/High/Critical (translated)",
            "safetyWarning": "Safety advice",
            "potentialCauses": [
                {{
                    "name": "Part name",
                    "description": "Technical description",
                    "solution": "How to fix",
                    "likelihood": 80,
                    "estimatedCost": "Cost estimate",
                    "difficulty": "Easy/Medium/Hard (translated)"
                }}
            ],
            "maintenanceTip": "Tip"
        }}
        """
    else: # Tuning
        system_instruction = base_instruction + f"""
        Focus on tuning/modification for a {vehicle} with {engine} engine.
        Return JSON structure:
        {{
            "summary": "Tuning plan summary",
            "expectedPowerIncrease": "e.g. +30HP",
            "drivingCharacteristics": "Handling changes",
            "estimatedTotalCost": "Total cost",
            "reliabilityImpact": "Impact description",
            "partsRecommendation": [
                {{
                    "name": "Part Name",
                    "type": "Type",
                    "description": "Why this part",
                    "estimatedPrice": "Price",
                    "powerGain": "Gain"
                }}
            ],
            "pros": ["Pro 1", "Pro 2"],
            "cons": ["Con 1", "Con 2"]
        }}
        """

    prompt = f"""
    Context/Previous Info: {context_history}
    Vehicle: {vehicle}
    Engine: {engine}
    User Input: {desc}
    """

    content = [prompt]
    if image:
        content.append(image)

    try:
        response = model.generate_content(
            contents=content,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                system_instruction=system_instruction
            )
        )
        
        # --- ZABEZPIECZENIE PRZED BŁĘDAMI JSON ---
        text_response = response.text.strip()
        # Czasami model zwraca ```json na początku, musimy to usunąć
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        return json.loads(text_response)
        
    except Exception as e:
        st.error(f"Błąd parsowania odpowiedzi AI: {e}")
        return None

# --- INTERFEJS UŻYTKOWNIKA ---

# Sidebar settings
with st.sidebar:
    st.header("Ustawienia / Settings")
    lang_code = st.selectbox("Język / Language", ["pl", "en", "de"], format_func=lambda x: x.upper())

t = TRANSLATIONS[lang_code]

# Header
col1, col2 = st.columns([1, 5])
with col1:
    st.header("🚘") 
with col2:
    st.title("AutoWise")
    mode = st.radio("Tryb / Mode", ["Diagnosis", "Tuning"], horizontal=True, 
                    format_func=lambda x: t["tab_diag"] if x == "Diagnosis" else t["tab_tune"])

st.markdown(f"*{t['subtitle_diag'] if mode == 'Diagnosis' else t['subtitle_tune']}*")
st.divider()

# Formularz
col_v, col_e = st.columns(2)
with col_v:
    vehicle_type = st.selectbox(t["vehicle"], list(t["vehicles"].keys()), format_func=lambda x: t["vehicles"][x])
with col_e:
    engine_type = st.selectbox(t["engine"], list(t["engines"].keys()), format_func=lambda x: t["engines"][x])

description = st.text_area(
    t["desc_label_diag"] if mode == "Diagnosis" else t["desc_label_tune"],
    placeholder=t["placeholder_diag"] if mode == "Diagnosis" else t["placeholder_tune"],
    height=150
)

uploaded_file = st.file_uploader(t["upload_label"], type=["jpg", "jpeg", "png", "webp"])
image_data = None
if uploaded_file:
    image_data = Image.open(uploaded_file)
    st.image(image_data, caption="Podgląd / Preview", width=200)

# Stan aplikacji
if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = ""

# Przycisk Główny
analyze_btn_text = t["analyze_btn_diag"] if mode == "Diagnosis" else t["analyze_btn_tune"]
if st.button(analyze_btn_text, type="primary", use_container_width=True):
    if not description and not image_data:
        st.warning("Opisz problem lub dodaj zdjęcie.")
    else:
        with st.spinner(t["analyzing"]):
            st.session_state.history = description # Reset historii przy nowym zapytaniu
            response = analyze_request(mode, vehicle_type, engine_type, description, lang_code, image_data)
            st.session_state.result = response

# Wyświetlanie Wyników
if st.session_state.result:
    res = st.session_state.result
    
    st.divider()
    
    # Sprawdzenie Off-topic
    if "potentialCauses" not in res and "partsRecommendation" not in res:
         st.warning(res.get("summary", "Error"))
    
    # Wyniki Diagnostyki
    elif mode == "Diagnosis":
        sev_color = "red" if res.get("severity") in ["Critical", "Krytyczny", "Kritisch"] else "orange"
        st.subheader(f"🔍 {t['result_severity']}: :{sev_color}[{res.get('severity')}]")
        
        st.info(f"**{t['result_safety']}:** {res.get('safetyWarning')}")
        st.markdown(f"### {res.get('summary')}")
        
        st.markdown(f"#### {t['result_causes']}")
        for cause in res.get("potentialCauses", []):
            with st.expander(f"{cause['name']} ({cause['likelihood']}%)"):
                st.markdown(f"**Opis:** {cause['description']}")
                st.markdown(f"**🔧 Rozwiązanie:** {cause['solution']}")
                col_c1, col_c2 = st.columns(2)
                col_c1.metric("Koszt", cause.get('estimatedCost', 'N/A'))
                col_c2.metric("Trudność", cause.get('difficulty', 'N/A'))
        
        st.success(f"💡 **{t['result_tip']}:** {res.get('maintenanceTip')}")

    # Wyniki Tuningu
    elif mode == "Tuning":
        st.subheader(f"⚡ {res.get('summary')}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric(t["tune_power"], res.get("expectedPowerIncrease"))
        c2.metric(t["tune_cost"], res.get("estimatedTotalCost"))
        c3.metric(t["tune_rel"], res.get("reliabilityImpact"))
        
        st.markdown(f"🏎️ **Wrażenia:** *{res.get('drivingCharacteristics')}*")
        
        st.markdown(f"#### {t['tune_parts']}")
        for part in res.get("partsRecommendation", []):
            with st.container(border=True):
                st.markdown(f"**{part['name']}** ({part['type']})")
                st.markdown(f"_{part['description']}_")
                sc1, sc2 = st.columns(2)
                sc1.markdown(f"💰 {part['estimatedPrice']}")
                sc2.markdown(f"📈 {part['powerGain']}")
        
        col_p, col_c = st.columns(2)
        with col_p:
            st.markdown(f"**👍 {t['tune_pros']}**")
            for p in res.get("pros", []):
                st.markdown(f"- {p}")
        with col_c:
            st.markdown(f"**👎 {t['tune_cons']}**")
            for c in res.get("cons", []):
                st.markdown(f"- {c}")

    # Sekcja Doprecyzowania (Refinement)
    st.divider()
    with st.form("refine_form"):
        st.markdown(f"### {t['refine_label']}")
        refine_text = st.text_input("Szczegóły", placeholder="Np. zapomniałem dodać, że silnik gaśnie na zimno...")
        if st.form_submit_button(t["refine_btn"]):
            with st.spinner(t["analyzing"]):
                # Aktualizacja historii kontekstu
                new_history = f"{st.session_state.history}\nUser update: {refine_text}"
                st.session_state.history = new_history
                
                # Ponowna analiza z kontekstem
                response = analyze_request(mode, vehicle_type, engine_type, refine_text, lang_code, image_data, context_history=new_history)
                st.session_state.result = response
                st.rerun()

# Footer
st.markdown("---")
st.markdown("© 2024 AutoWise. Powered by Google Gemini AI.", unsafe_allow_html=True)
