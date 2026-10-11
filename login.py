"""Streamlit login gate. Call before loading data or creating any dashboard UI."""
import streamlit as st
from access_control import LoginService, parse_settings, valid_session
from branding import brand

SESSION_KEY = "_review_access"


@st.cache_resource
def login_service():
    return LoginService()


def settings():
    # Deliberately not cached here. Cloud secret changes must be saved and the app rebooted.
    return parse_settings(st.secrets["review_access"])


def clear_session():
    for key in list(st.session_state):
        del st.session_state[key]


def require_login():
    try:
        config = settings()
    except (KeyError, ValueError, TypeError, AttributeError, FileNotFoundError):
        clear_session()
        brand()
        st.title("Review access")
        st.error("Access has not been configured. Please contact the dashboard owner.")
        st.stop()
    session = st.session_state.get(SESSION_KEY)
    if valid_session(session, config):
        return session["username"]
    if session:
        clear_session()
    st.markdown('<style>[data-testid="stSidebar"] {display:none;}</style>', unsafe_allow_html=True)
    _, column, _ = st.columns([1, 1.2, 1])
    with column:
        brand()
        st.title("Review access")
        st.write("Sign in to explore the PrismHaus dashboard.")
        if session:
            st.info("Your access has ended. Please sign in again or contact the dashboard owner.")
        with st.form("review_login", clear_on_submit=True):
            username = st.text_input("Username", max_chars=64)
            password = st.text_input("Password", type="password", max_chars=256)
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            authenticated, error = login_service().authenticate(username, password, config)
            if authenticated:
                st.session_state[SESSION_KEY] = authenticated
                st.rerun()
            st.error(error)
        st.caption("Access is provided by the dashboard owner. HoneyBook figures are illustrative.")
    st.stop()


@st.fragment(run_every="30s")
def session_controls():
    """Recheck active access every 30 seconds as well as on all full app runs."""
    try:
        allowed = valid_session(st.session_state.get(SESSION_KEY), settings())
    except (KeyError, ValueError, TypeError, AttributeError, FileNotFoundError):
        allowed = False
    if not allowed:
        clear_session()
        st.rerun()
    st.caption(f"Signed in as {st.session_state[SESSION_KEY]['username']}")
    if st.button("Log out", key="review_logout", use_container_width=True):
        clear_session()
        st.rerun()
