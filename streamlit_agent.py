import os
import random
import re
from datetime import datetime

from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Try to configure an LLM client if API key is present.
_llm_available = False
_llm = None

try:
    if OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
        from langchain_openai import ChatOpenAI
        # Create a LangChain ChatOpenAI client; it will read the OPENAI_API_KEY
        _llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.3)
        _llm_available = True
except Exception:
    _llm_available = False
    _llm = None


FAQ_RESPONSES = {
    "password": "To reset your password, go to the login page and click 'Forgot Password'. Follow the link sent to your email.",
    "install": "Download the installer from your dashboard, run it, and follow the prompts. Let me know if you hit an error message.",
    "billing": "Billing is managed under Account → Billing. You can view invoices, update payment details, and request refunds there.",
    "cancel": "To cancel your subscription, open Account → Subscription and choose 'Cancel Plan'. Your access remains until the end of the billing cycle.",
    "refund": "Refund requests are reviewed within 3–5 business days. Please provide your order details so we can help.",
    "feature": "Feature requests are welcome! Tell me what you'd like to see, and I’ll pass it to the product team.",
}

ESCALATION_KEYWORDS = [
    "angry",
    "frustrated",
    "furious",
    "lawsuit",
    "legal",
    "terrible",
    "hate",
    "worst",
    "broken",
    "issue",
    "problem",
]

FALLBACK_RESPONSES = [
    "Thanks for your question — could you share a few more details so I can help?",
    "I can help with account, billing, installation, and product questions. What would you like to know?",
    "I’m here to help. Please tell me more about the issue you are facing.",
]

GREETING_RESPONSES = [
    "Hello! How can I help you today?",
    "Hi there! What can I do for you?",
    "Hey! I’m here to help with your support question.",
]


def _call_openai(user_message: str) -> str | None:
    """Call OpenAI ChatCompletion if available; return None on failure."""
    if not _llm_available or _llm is None:
        return None
    try:
        # Use LangChain message wrapper for robust calls
        from langchain_core.messages import HumanMessage

        response = _llm.invoke([HumanMessage(content=user_message)])

        # Common response shapes: object with `content`, list-like, or dict
        if hasattr(response, "content"):
            return str(response.content).strip()
        if isinstance(response, (list, tuple)) and response:
            first = response[0]
            if hasattr(first, "content"):
                return str(first.content).strip()
            return str(first).strip()
        if isinstance(response, dict):
            # best-effort extraction
            for k in ("content", "text", "message"):
                if k in response:
                    return str(response[k]).strip()
            return None
        return str(response).strip()
    except Exception:
        return None


def generate_agent_response(user_message: str) -> dict:
    text = user_message.strip()
    if not text:
        return {"text": "Please type a message so I can assist you.", "escalated": False}

    lower_text = text.lower()

    if re.search(r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b", lower_text):
        return {"text": random.choice(GREETING_RESPONSES), "escalated": False}

    if any(keyword in lower_text for keyword in ESCALATION_KEYWORDS):
        return {
            "text": (
                "ESCALATE_TO_HUMAN We have flagged this conversation for human review because your message appears urgent. "
                "A support agent will follow up shortly."
            ),
            "escalated": True,
        }

    for keyword, answer in FAQ_RESPONSES.items():
        if keyword in lower_text:
            return {"text": answer, "escalated": False}

    # If local rules didn't match and an LLM is available, call it as a fallback.
    llm_reply = _call_openai(text)
    if llm_reply:
        return {"text": llm_reply, "escalated": False}

    if "thank" in lower_text or "thanks" in lower_text:
        return {"text": "You’re welcome! Let me know if there’s anything else I can do.", "escalated": False}

    return {"text": random.choice(FALLBACK_RESPONSES), "escalated": False}


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "escalated" not in st.session_state:
        st.session_state.escalated = False
    if "started_at" not in st.session_state:
        st.session_state.started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def render_chat_app() -> None:
    st.set_page_config(page_title="Chat Agent (env LLM toggle)", layout="centered")
    st.title("Chat Agent — Uses .env for API keys")
    st.write("The app uses local rules first. If `OPENAI_API_KEY` is set in `.env`, it will call OpenAI as a fallback.")

    with st.sidebar:
        st.header("Support settings")
        st.text_input("Your name", value="Customer", key="user_name")
        st.selectbox("Plan", ["Standard", "Pro", "Enterprise"], key="user_plan")
        st.markdown("---")
        st.write("LLM available: " + ("Yes" if _llm_available else "No"))
        if _llm_available:
            st.write(f"Using model: {OPENAI_MODEL}")

    init_state()

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message", key="chat_input")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        st.session_state.messages.append({
            "role": "user",
            "text": f"{st.session_state.user_name}: {user_input}",
            "time": datetime.now().strftime("%H:%M:%S"),
        })
        response = generate_agent_response(user_input)
        st.session_state.messages.append({
            "role": "assistant",
            "text": response["text"],
            "time": datetime.now().strftime("%H:%M:%S"),
        })
        st.session_state.escalated = response["escalated"]

    if st.session_state.messages:
        for item in st.session_state.messages:
            with st.chat_message(item["role"]):
                st.markdown(item["text"])

    if st.session_state.escalated:
        st.warning("This conversation has been flagged for human review.")

    if st.button("Reset conversation"):
        st.session_state.messages = []
        st.session_state.escalated = False
        st.experimental_rerun()


if __name__ == "__main__":
    render_chat_app()
