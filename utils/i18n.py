# utils/i18n.py
MESSAGES = {
    "en": { 
       "greeting": "Hello! I am AgroSense 🌾. How can I help you today?",
       "ask_soil_info": "Before I can suggest, please provide soil & season details.",
       "soil_type": "Soil type (e.g. Sandy, Loamy, Clay, Kandi, Floodplain, Forest):",
       "moisture": "Moisture level (Low / Medium / High):",
       "organic": "Organic matter (Poor / Average / Good):",
       "n_level": "Nitrogen (N) level (number or Low/Medium/High):",
       "p_level": "Phosphorus (P) level (number or Low/Medium/High):",
       "k_level": "Potassium (K) level (number or Low/Medium/High):",
       "season": "Season (Kharif / Rabi / Summer):",
       "error_invalid": "Invalid input — please re-enter.",
       "thanks": "Thanks! Preparing recommendation..."
    },
    "hi": {
       "greeting": "नमस्ते! मैं AgroSense 🌾 हूँ। आपकी कैसे मदद कर सकता हूँ?",
       "ask_soil_info": "कृपया अपनी मिट्टी और मौसम की जानकारी दीजिए:",
       "soil_type": "मिट्टी का प्रकार (जैसे: Sandy, Loamy, Clay, Kandi, Floodplain, Forest):",
       "moisture": "नमी स्तर (Low / Medium / High):",
       "organic": "जैविक पदार्थ (Poor / Average / Good):",
       "n_level": "नाइट्रोजन (N) स्तर (संख्या या Low/Medium/High):",
       "p_level": "फॉस्फोरस (P) स्तर (संख्या या Low/Medium/High):",
       "k_level": "पोटैशियम (K) स्तर (संख्या या Low/Medium/High):",
       "season": "सीजन (Kharif / Rabi / Summer):",
       "error_invalid": "गलत इनपुट — कृपया फिर से भरें।",
       "thanks": "धन्यवाद! सलाह तैयार की जा रही है..."
    }
}

SUPPORTED_LANG = ["en", "hi"]

def t(lang, key):
    return MESSAGES.get(lang, MESSAGES["en"]).get(key, key)
