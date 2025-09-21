# app.py
import os
import streamlit as st

# Try to import the Google Generative AI SDK; if it's not available we'll still allow mock mode
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False

st.set_page_config(page_title="AI Misinformation Toolkit", layout="centered")

st.title("🛡️ AI Misinformation Toolkit (Prototype)")
st.caption("Paste text (news, social post, forward). Prototype: Red flags, factual summary, and educational insights.")

# --- API key handling ---
# 1. Preferred (local Streamlit): st.secrets["GEMINI_API_KEY"]
# 2. Fallback to environment variable: os.environ.get("GEMINI_API_KEY")
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.environ.get("GEMINI_API_KEY")

USE_MOCK = False
if not api_key or not GENAI_AVAILABLE:
    USE_MOCK = True
else:
    # configure the SDK
    genai.configure(api_key=api_key)

# --- UI: input area ---
input_text = st.text_area("Paste suspicious text here:", height=220, placeholder="Paste an article, tweet thread, WhatsApp forward, etc.")
col1, col2 = st.columns([1, 1])
with col1:
    analyze_btn = st.button("🔍 Analyze")
with col2:
    clear_btn = st.button("Clear")

if clear_btn:
    st.experimental_rerun()

def call_gemini(prompt: str, max_tokens: int = 300) -> str:
    """
    Calls Gemini model via google.generativeai if configured,
    otherwise returns a helpful mock response.
    """
    if USE_MOCK:
        # Simple mock that echoes part of prompt and shows placeholder output
        return ("[MOCK RESPONSE — no API key detected]\n\n"
                "This is a placeholder. Add your Gemini API key in .streamlit/secrets.toml or as env var GEMINI_API_KEY to get live results.")
    try:
        # This uses a typical genai call - adjust model name if needed
        resp = genai.generate_text(model="gemini-pro", prompt=prompt, max_output_tokens=max_tokens)
        # Many genai clients return a .text or .candidates[0].content - handle both cases
        if hasattr(resp, "text"):
            return resp.text
        if hasattr(resp, "candidates") and resp.candidates:
            return resp.candidates[0].content
        return str(resp)
    except Exception as e:
        return f"[ERROR calling Gemini API] {e}"

def generate_red_flags(text: str) -> str:
    prompt = (
        "You are an assistant that identifies indicators of misinformation in text. "
        "Given the following text, return a bulleted list of 'red flags'. For each flag include: "
        "1) Quote or short excerpt, 2) the type of problem (e.g., emotional appeal, no source, sensational claim, cherry-picking, misleading statistic, poor sourcing), "
        "3) a one-line explanation. Use short bullet points.\n\n"
        f"TEXT:\n'''{text}'''\n\n"
        "Format strictly as bullets."
    )
    return call_gemini(prompt, max_tokens=280)

def generate_summary(text: str) -> str:
    prompt = (
        "You are a neutral summarizer. Read the text and provide a concise, factual, neutral summary (2-4 sentences). "
        "Do not add opinions and avoid speculative language. If the input contains claims that are verifiable, indicate them as 'Claim: ...' and mark 'Verified/Unverified/Unknown' if possible.\n\n"
        f"TEXT:\n'''{text}'''"
    )
    return call_gemini(prompt, max_tokens=200)

def generate_insights(text: str) -> str:
    prompt = (
        "You are an educational assistant. For the provided text, list 2-4 misinformation tactics used (e.g., cherry-picking, appeal to emotion, false cause), "
        "and for each tactic give a two-sentence plain-language explanation and an example suggestion for how a user can check or verify such a tactic.\n\n"
        f"TEXT:\n'''{text}'''"
    )
    return call_gemini(prompt, max_tokens=300)

if analyze_btn:
    if not input_text.strip():
        st.warning("Please paste text to analyze.")
    else:
        with st.spinner("Analyzing..."):
            red_flags = generate_red_flags(input_text)
            summary = generate_summary(input_text)
            insights = generate_insights(input_text)

        st.subheader("🚩 Red Flag Analysis")
        # Display red flags as markdown
        st.markdown(red_flags.replace("\n", "\n\n"))

        st.subheader("📌 Factual Summary")
        st.write(summary)

        st.subheader("🎓 Educational Insights")
        st.write(insights)

        st.info("Tip: For production, wire model outputs to citation checks (news sources, fact-checkers) and show evidence links.")

# Footer / instructions
st.markdown("---")
st.markdown(
    "### How to enable Gemini (live mode)\n"
    "- Create a file at `.streamlit/secrets.toml` with:\n\n"
    "```toml\nGEMINI_API_KEY = \"your_actual_api_key_here\"\n```\n"
    "- Or set environment variable `GEMINI_API_KEY`.\n"
    "\nIf you enable the key, the app will call Gemini. Without it, the app runs in MOCK mode so you can test the UI."
)
