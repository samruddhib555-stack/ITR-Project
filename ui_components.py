import streamlit as st

def load_css(css_path):
    """Loads and injects custom CSS for dark premium theme."""
    try:
        with open(css_path, "r") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        # Fallback if CSS cannot be read
        st.warning(f"Unable to load custom styles: {e}")

def metric_card(label, value, subtext="", color="blue"):
    """
    Renders a custom glassmorphism metric card with a colored value.
    color can be 'blue', 'green', or 'orange'
    """
    val_class = "metric-value"
    if color == "orange":
        val_class = "metric-value-orange"
    elif color == "green":
        val_class = "metric-value-green"
        
    html = f"""
    <div class="premium-card">
        <div class="metric-label">{label}</div>
        <div class="{val_class}">{value}</div>
        <div class="metric-sub">{subtext}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def progress_bar(label, value, target, unit, color="blue"):
    """Renders a labeled progress bar with details and percentage calculation."""
    pct = min(100.0, (value / target * 100.0) if target > 0 else 0.0)
    
    fill_class = "progress-bar-fill"
    if color == "orange":
        fill_class = "progress-bar-fill-orange"
    elif color == "green":
        fill_class = "progress-bar-fill-green"
        
    html = f"""
    <div class="premium-card" style="padding: 16px 24px;">
        <div style="display: flex; justify-content: space-between; font-weight: 500; font-size: 0.95rem; margin-bottom: 5px;">
            <span>{label}</span>
            <span style="color: #8a8f9d;">{value} / {target} {unit} ({round(pct)}%)</span>
        </div>
        <div class="progress-container">
            <div class="{fill_class}" style="width: {pct}%;"></div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_recommendation(rec):
    """Renders a recommendation card with status indicators."""
    status = rec.get("status", "info")
    category = rec.get("category", "Advice")
    message = rec.get("message", "")
    
    status_class = ""
    icon = "💡"
    if status == "warning":
        status_class = "warning"
        icon = "⚠️"
    elif status == "success":
        status_class = "success"
        icon = "✅"
        
    html = f"""
    <div class="recommendation-item {status_class}">
        <div style="font-size: 1.25rem; margin-right: 4px;">{icon}</div>
        <div>
            <strong style="color: #ffffff; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.5px;">{category}</strong>
            <div style="font-size: 0.9rem; color: #d1d4db; margin-top: 2px;">{message}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_hero(title_line1, title_line2, description, button_key="hero_btn", button_text="START FITNESS JOURNEY"):
    """Renders a premium hero banner section on the landing page."""
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 10px 20px 10px;">
        <h1 class="hero-title">{title_line1}</h1>
        <h1 class="hero-subtitle">{title_line2}</h1>
        <p style="font-size: 1.15rem; color: #8a8f9d; max-width: 600px; margin: 0 auto 30px auto; line-height: 1.6;">
            {description}
        </p>
    </div>
    """, unsafe_allow_html=True)

def info_callout(message):
    """Renders a styled dark background callout box."""
    st.markdown(f"""
    <div class="info-alert">
        <strong>💡 Tip:</strong> {message}
    </div>
    """, unsafe_allow_html=True)
