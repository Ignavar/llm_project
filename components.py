# components.py
import html


def page_header() -> str:
    return """
    <div class="bank-header">
        <h1>NUST <span>Bank</span> Assistant</h1>
        <p>Reliable · Secure · 24/7 AI Banking Support</p>
    </div>
    <div class="themed-divider"></div>
    """


# ✅ USER MESSAGE (RIGHT SIDE)
def user_bubble(content: str) -> str:
    safe = html.escape(content)
    return f"""
    <div class="bubble-row user">
        <div class="bubble user-bubble">
            <div class="bubble-meta">You</div>
            {safe}
        </div>
        <div class="avatar user-av">U</div>
    </div>
    """


# ✅ BOT MESSAGE (LEFT SIDE)
def bot_bubble(content: str) -> str:
    return f"""
    <div class="bubble-row bot">
        <div class="avatar bot-av">AI</div>
        <div class="bubble bot-bubble">
            <div class="bubble-meta">Assistant</div>
            {content}
        </div>
    </div>
    """


def empty_state() -> str:
    suggestions = [
        "Check my balance",
        "Apply for a loan",
        "Transfer funds",
        "View transactions",
        "Account services",
    ]
    chips_html = "".join(f'<span class="chip">{s}</span>' for s in suggestions)
    return f"""
    <div class="empty-state">
        <div class="icon">🏦</div>
        <h3>How can I help you today?</h3>
        <p>Ask me anything about your accounts, loans, transfers, or banking services.</p>
        <div class="chip-row">{chips_html}</div>
    </div>
    """


def sidebar_section_label(text: str) -> str:
    return f'<p class="sidebar-section-label">{html.escape(text)}</p>'


def status_indicator(online: bool = True) -> str:
    label = "System Online" if online else "System Offline"
    return f"""
    <div style="margin-top: 0.75rem;">
        <span class="status-dot"></span>
        <span class="status-text">{label}</span>
    </div>
    """


def chat_wrapper_open() -> str:
    return '<div class="chat-wrapper">'


def chat_wrapper_close() -> str:
    return '</div>'