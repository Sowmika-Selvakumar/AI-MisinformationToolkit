import streamlit as st
import google.generativeai as genai
import os

# ------------------------
# 🔑 API Key Configuration
# ------------------------
# Use Streamlit secrets if available, else fall back to environment variable
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    USE_MOCK = False
elif os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    USE_MOCK = False
else:
    USE_MOCK = True


# ------------------------
# 🔧 Helper Function
# ------------------------
def call_gemini(prompt: str, max_tokens: int = 300) -> str:
    """
    Calls Gemini model via google.generativeai if configured,
    otherwise returns a helpful mock response.
    """
    if USE_MOCK:
        return ("[MOCK RESPONSE — no API key detected]\n\n"
                "This is a placeholder. Add your Gemini API key in .streamlit/secrets.toml "
                "or as env var GEMINI_API_KEY to get live results.")
    try:
        # ✅ Correct Gemini usage
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(prompt)

        if hasattr(resp, "text"):
            return resp.text.strip()
        return str(resp)
    except Exception as e:
        return f"[ERROR calling Gemini API] {e}"


# ------------------------
# 🎨 Streamlit UI
# ------------------------
st.set_page_config(page_title="ContractAnalyzer - Misinformation Tool", layout="wide")
st.title("🛡️ AI-Powered Tool for Combating Misinformation")
st.write("Paste any suspicious text below to analyze for misinformation cues, get a factual summary, and learn educational insights.")

# Text input
user_input = st.text_area("Paste suspicious text here:", height=200)

if st.button("🔍 Analyze"):
    if not user_input.strip():
        st.warning("⚠️ Please enter some text to analyze.")
    else:
        with st.spinner("Analyzing with Gemini..."):
            # Generate outputs
            red_flags = call_gemini(
                f"Analyze the following text for misinformation cues (like emotional appeals, lack of sources, exaggeration, fallacies). "
                f"Highlight specific red flags:\n\n{user_input}"
            )

            factual_summary = call_gemini(
                f"Provide a concise, factual, and neutral summary of the topic discussed in this text:\n\n{user_input}"
            )

            educational_insights = call_gemini(
                f"Explain the misinformation techniques used in this text (e.g., cherry-picking, appeal to emotion, false authority). "
                f"Give short, clear explanations:\n\n{user_input}"
            )

        # Display results
        st.subheader("🚩 Red Flag Analysis")
        st.write(red_flags)

        st.subheader("📌 Factual Summary")
        st.write(factual_summary)

        st.subheader("🎓 Educational Insights")
        st.write(educational_insights)

        st.info("💡 Tip: For production, consider adding fact-checker APIs or citation checks to back up summaries with credible sources.")
