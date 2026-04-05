def build_google_fonts_url(dark_mode: bool) -> str:
    if dark_mode:
        return (
            "https://fonts.googleapis.com/css2?"
            "family=Space+Grotesk:wght@300;400;500;600;700&"
            "family=Inter:wght@300;400;500&display=swap"
        )
    return (
        "https://fonts.googleapis.com/css2?"
        "family=Noto+Serif:wght@400;600;700&"
        "family=Newsreader:wght@400;500&"
        "family=Work+Sans:wght@300;400;500;600&display=swap"
    )


def build_css(t: dict, dark_mode: bool) -> str:

    cta_gradient = f"linear-gradient(135deg, {t['primary']}, {t['primary_container']})"
    ghost_border = f"1px solid {t['outline_variant']}29"

    return f"""
    <style>
    @import url('{build_google_fonts_url(dark_mode)}');

    :root {{
        --surface: {t['surface']};
        --surface-low: {t['surface_container_low']};
        --surface-mid: {t['surface_container']};
        --surface-high: {t['surface_container_high']};
        --surface-highest: {t['surface_container_highest']};

        --primary: {t['primary']};
        --primary-container: {t['primary_container']};

        --secondary: {t['secondary']};
        --secondary-container: {t['secondary_container']};

        --on-surface: {t['on_surface']};
        --on-surface-variant: {t['on_surface_variant']};
        --on-primary: {t['on_primary']};

        --outline-variant: {t['outline_variant']};

        --font-body: {t['font_body']};
        --font-label: {t['font_label']};

        --radius-card: {t['border_radius_card']};

        --cta-gradient: {cta_gradient};
        --ghost-border: {ghost_border};
        --shadow-float: {t['shadow_float']};
    }}

    /* ───────── BASE ───────── */
    html, body, .stApp {{
        background-color: var(--surface) !important;
        color: var(--on-surface) !important;
        font-family: var(--font-body);
    }}

    #MainMenu, footer, header {{
        visibility: hidden;
    }}

    /* ───────── SIDEBAR ───────── */
    [data-testid="stSidebar"] {{
        background-color: var(--surface-low) !important;
    }}

    [data-testid="stSidebar"] button {{
        background-color: var(--surface-mid) !important;
        color: var(--on-surface) !important;
        border: var(--ghost-border) !important;
        border-radius: var(--radius-card) !important;
        font-family: var(--font-label) !important;
        text-transform: uppercase;
    }}

    [data-testid="stSidebar"] button:hover {{
        background-color: var(--surface-high) !important;
        color: var(--primary) !important;
    }}

    /* ───────── CHAT INPUT ───────── */

    div[data-testid="stChatInput"] {{
        background-color: var(--surface-mid) !important;
        border: 2px solid var(--outline-variant) !important;
        border-radius: var(--radius-card) !important;
    }}

    div[data-testid="stChatInput"] div,
    div[data-baseweb="textarea"],
    div[data-baseweb="base-input"] {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    div[data-testid="stChatInput"] textarea {{
        background-color: transparent !important;
        color: var(--on-surface) !important;
        border: none !important;
        outline: none !important;
    }}

    div[data-testid="stChatInput"] button {{
        background: var(--cta-gradient) !important;
        color: var(--on-primary) !important;
        border: none !important;
    }}

    /* ───────── CLEAN BACKGROUND ───────── */

    .stApp,
    .main,
    .block-container {{
        background-color: var(--surface) !important;
    }}

    section[data-testid="stMain"] > div {{
        background-color: var(--surface) !important;
    }}

    div[data-testid="stVerticalBlock"],
    div[data-testid="stVerticalBlock"] > div {{
        background-color: transparent !important;
    }}

    /* ───────── CHATGPT STYLE CHAT UI ───────── */

    .chat-wrapper {{
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
        max-width: 900px;
        margin: 2rem auto;
        padding-bottom: 120px;
    }}

    .bubble-row {{
        display: flex;
        align-items: flex-end;
        gap: 0.6rem;
    }}

    .bubble-row.user {{
        justify-content: flex-end;
    }}

    .bubble-row.bot {{
        justify-content: flex-start;
    }}

    .avatar {{
        width: 34px;
        height: 34px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
    }}

    .user-av {{
        background: var(--primary);
        color: var(--on-primary);
    }}

    .bot-av {{
        background: var(--surface-high);
        color: var(--on-surface);
    }}

    .bubble {{
        max-width: 70%;
        padding: 0.75rem 1rem;
        border-radius: 16px;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: var(--shadow-float);
    }}

    .user-bubble {{
        background: var(--primary);
        color: var(--on-primary);
        border-bottom-right-radius: 4px;
    }}

    .bot-bubble {{
        background: var(--surface-high);
        color: var(--on-surface);
        border-bottom-left-radius: 4px;
    }}

    .bubble-meta {{
        font-size: 0.65rem;
        opacity: 0.6;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* ───────── FIX STREAMLIT COMPONENT COLORS ───────── */

    [data-testid="stFileUploaderDropzone"] {{
        background-color: var(--surface-mid) !important;
        border: 1px solid var(--outline-variant) !important;
    }}

    [data-testid="stFileUploaderDropzone"] * {{
        background-color: transparent !important;
    }}

    [data-testid="stFileUploader"] button {{
        background: var(--cta-gradient) !important;
        color: var(--on-primary) !important;
        border: none !important;
    }}

    div[data-testid="stBottomBlockContainer"],
    div[data-testid="stBottomBlockContainer"] > div,
    div[data-testid="stBottomBlockContainer"] div {{
        background-color: var(--surface) !important;
    }}

    div[data-testid="stChatInput"] {{
        background-color: var(--surface-mid) !important;
        border: 2px solid var(--outline-variant) !important;
    }}

    div[data-testid="stChatInput"] * {{
        background-color: transparent !important;
    }}

    textarea[data-testid="stChatInputTextArea"] {{
        color: var(--on-surface) !important;
    }}

    button[data-testid="stChatInputSubmitButton"] {{
        background: var(--cta-gradient) !important;
        color: var(--on-primary) !important;
    }}

    </style>
    """