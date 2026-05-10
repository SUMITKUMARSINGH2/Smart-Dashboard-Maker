import streamlit as st


def cookies_page():
    st.markdown("""
    <div style='max-width:860px;margin:0 auto;'>
    <div style='margin-bottom:2rem;'>
        <div style='font-size:.7rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;
                    color:#7C3AED;margin-bottom:.4rem;'>Legal</div>
        <h1 style='font-size:2rem;font-weight:800;color:#1C1917;margin:0 0 .4rem;'>Cookie Policy</h1>
        <div style='width:44px;height:4px;background:linear-gradient(90deg,#7C3AED,#F43F5E);
                    border-radius:2px;margin-bottom:.8rem;'></div>
        <p style='color:#6B7280;font-size:.875rem;'>Last updated: January 2025</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    This Cookie Policy explains how DataViz Pro uses cookies and similar tracking technologies
    when you visit our application. It explains what these technologies are and why we use them,
    as well as your rights to control our use of them.
    """)

    st.markdown("### What Are Cookies?")
    st.markdown("""
    Cookies are small data files placed on your computer or mobile device when you visit a website.
    They are widely used to make websites work, or work more efficiently, as well as to provide
    reporting information to site owners. Cookies set by the website owner are called "first-party
    cookies". Cookies set by parties other than the website owner are called "third-party cookies".
    """)

    st.markdown("### Types of Cookies We Use")

    cookie_types = [
        {
            "name": "Strictly Necessary Cookies",
            "color": "#059669",
            "bg": "#ECFDF5",
            "desc": "These cookies are required for the application to function and cannot be switched off. They are usually set in response to actions you take such as setting your preferences, keeping your session active, or filling in forms.",
            "examples": [
                ("Session cookie", "Keeps you logged in during your visit", "Session end"),
                ("CSRF token", "Prevents cross-site request forgery attacks", "Session end"),
            ]
        },
        {
            "name": "Analytics Cookies",
            "color": "#0EA5E9",
            "bg": "#F0F9FF",
            "desc": "These cookies allow us to count visits and traffic sources so we can measure and improve the performance of the application. All information these cookies collect is aggregated and therefore anonymous.",
            "examples": [
                ("_ga (Google Analytics)", "Distinguishes unique users", "2 years"),
                ("_gid (Google Analytics)", "Distinguishes unique users", "24 hours"),
                ("_gat (Google Analytics)", "Throttles request rate", "1 minute"),
            ]
        },
        {
            "name": "Advertising Cookies (Google AdSense)",
            "color": "#F59E0B",
            "bg": "#FFFBEB",
            "desc": "These cookies are set by our advertising partner Google AdSense. They may be used to build a profile of your interests and show you relevant adverts on other sites. They do not store directly personal information.",
            "examples": [
                ("IDE", "Used for targeted advertising by Google", "1 year"),
                ("test_cookie", "Checks if your browser supports cookies", "15 minutes"),
                ("ANID", "Used to target advertising based on previous visits", "13 months"),
                ("NID", "Stores preferences and other information for Google ads", "6 months"),
            ]
        },
        {
            "name": "Preference Cookies",
            "color": "#8B5CF6",
            "bg": "#F5F3FF",
            "desc": "These cookies enable the application to remember choices you make (such as your preferred theme or chart settings) and provide enhanced, more personalised features.",
            "examples": [
                ("app_theme", "Remembers your display preferences", "30 days"),
            ]
        },
    ]

    for ct in cookie_types:
        st.markdown(f"""
        <div style='background:{ct["bg"]};border-radius:12px;padding:1.2rem 1.4rem;
                    margin-bottom:1.2rem;border-left:4px solid {ct["color"]};'>
            <div style='font-weight:800;color:{ct["color"]};font-size:.95rem;
                        margin-bottom:.5rem;'>{ct["name"]}</div>
            <p style='color:#374151;font-size:.85rem;margin:0 0 .8rem;line-height:1.6;'>{ct["desc"]}</p>
        </div>
        """, unsafe_allow_html=True)

        import pandas as pd
        rows = [(e[0], e[1], e[2]) for e in ct["examples"]]
        df = pd.DataFrame(rows, columns=["Cookie Name", "Purpose", "Expiry"])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### How to Control Cookies")
    st.markdown("""
    You have the right to decide whether to accept or reject cookies (except strictly necessary ones).

    **Browser Settings**
    Most web browsers allow you to control cookies through their settings preferences. You can:
    - View what cookies have been set
    - Allow, block, or delete cookies
    - Set preferences for specific websites

    Here are links to cookie management instructions for popular browsers:
    - [Google Chrome](https://support.google.com/chrome/answer/95647)
    - [Mozilla Firefox](https://support.mozilla.org/en-US/kb/enable-and-disable-cookies-website-preferences)
    - [Apple Safari](https://support.apple.com/guide/safari/manage-cookies-sfri11471/mac)
    - [Microsoft Edge](https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge)

    **Google Analytics Opt-Out**
    Install the [Google Analytics Opt-out Browser Add-on](https://tools.google.com/dlpage/gaoptout)
    to prevent Google Analytics from collecting your data.

    **Google AdSense Opt-Out**
    Visit [Google Ads Settings](https://www.google.com/settings/ads) to opt out of
    personalised advertising.

    Note: Disabling certain cookies may affect the functionality of DataViz Pro.
    """)

    st.markdown("### Updates to This Policy")
    st.markdown("""
    We may update this Cookie Policy from time to time to reflect changes in technology,
    legislation, or our data practices. Any changes will become effective when we post the
    updated policy with a new "Last updated" date.

    **Contact Us**
    If you have questions about our use of cookies, contact us at: cookies@datavizpro.app
    """)

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center;color:#9CA3AF;font-size:.8rem;padding:1rem 0;'>
        See also:
        <a href='#' style='color:#7C3AED;text-decoration:none;margin:0 .5rem;'>Privacy Policy</a> ·
        <a href='#' style='color:#7C3AED;text-decoration:none;margin:0 .5rem;'>Terms of Service</a>
    </div>
    """, unsafe_allow_html=True)
