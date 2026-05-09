import streamlit as st


def privacy_page():
    st.markdown("""
    <div style='max-width:860px;margin:0 auto;'>
    <div style='margin-bottom:2rem;'>
        <div style='font-size:.7rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;
                    color:#7C3AED;margin-bottom:.4rem;'>Legal</div>
        <h1 style='font-size:2rem;font-weight:800;color:#1C1917;margin:0 0 .4rem;'>Privacy Policy</h1>
        <div style='width:44px;height:4px;background:linear-gradient(90deg,#7C3AED,#F43F5E);
                    border-radius:2px;margin-bottom:.8rem;'></div>
        <p style='color:#6B7280;font-size:.875rem;'>Last updated: January 2025</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

    sections = [
        ("1. Introduction", """
DataViz Pro ("we", "our", or "us") is committed to protecting your privacy.
This Privacy Policy explains how we collect, use, disclose, and safeguard your information
when you use our data analytics platform.

Please read this policy carefully. If you disagree with its terms, please stop using the application.
        """),
        ("2. Information We Collect", """
**a) Data You Upload**

DataViz Pro is a client-side data analysis tool. Files you upload (CSV, Excel, JSON, Parquet)
are processed **entirely in your browser session** and on the server for the duration of your
session only. We do **not** permanently store, share, or sell your uploaded data.

**b) Usage Data (Analytics)**

We may collect anonymous, aggregated usage data such as:
- Pages visited within the application
- Features used (e.g., which chart types are selected)
- Browser type, operating system, and screen resolution
- Approximate geographic location (country level)
- Session duration and frequency of visits

This data does not identify you personally and is used solely to improve the application.

**c) Cookies and Similar Technologies**

We use cookies and similar tracking technologies to:
- Keep your session active while you use the app
- Remember your preferences
- Collect anonymous analytics data (via Google Analytics, if enabled)

You can control cookies through your browser settings. Disabling cookies may affect functionality.
        """),
        ("3. Google AdSense and Advertising", """
DataViz Pro may display advertisements served by Google AdSense or other advertising networks.
These third-party ad servers use cookies to serve ads based on your prior visits to this and
other websites.

Google's use of advertising cookies enables it and its partners to serve ads based on your
visit to our site and/or other sites on the Internet. You may opt out of personalized
advertising by visiting [Google Ads Settings](https://www.google.com/settings/ads).

We do not have access to or control over the cookies used by third-party ad networks.
You can find more information about Google's practices at:
https://policies.google.com/technologies/ads
        """),
        ("4. How We Use Your Information", """
We use the information we collect to:
- Provide, operate, and maintain DataViz Pro
- Improve, personalise, and expand our services
- Understand and analyse how you use the application
- Develop new features and functionality
- Display relevant advertisements (if applicable)
- Comply with legal obligations
        """),
        ("5. Data Sharing and Disclosure", """
We do **not** sell, trade, or rent your personal information to third parties.

We may share information with:
- **Service providers**: Third-party vendors who help us operate the platform
  (e.g., hosting, analytics)
- **Advertising partners**: Anonymous, aggregated data only — never your uploaded files
- **Legal requirements**: When required by law or to protect our rights

Your uploaded dataset files are **never** shared with third parties.
        """),
        ("6. Data Retention", """
- **Uploaded files**: Deleted at the end of your browser session. We do not retain them.
- **Usage analytics**: Retained in aggregated, anonymised form for up to 24 months.
- **Cookies**: Expire as described in our Cookie Policy (see the Cookies page).
        """),
        ("7. Your Rights", """
Depending on your location, you may have the following rights:
- **Access**: Request a copy of the personal data we hold about you
- **Correction**: Request correction of inaccurate data
- **Deletion**: Request deletion of your data
- **Opt-out of advertising**: Use Google's opt-out tools linked above
- **Cookie control**: Manage cookies through your browser settings

To exercise these rights, contact us at the address below.
        """),
        ("8. Children's Privacy", """
DataViz Pro is not directed to children under the age of 13. We do not knowingly collect
personal information from children under 13. If you believe a child has provided us with
personal information, please contact us and we will delete it promptly.
        """),
        ("9. Third-Party Links", """
Our application may contain links to third-party websites. We are not responsible for the
privacy practices or content of those sites. We encourage you to review the privacy policies
of any third-party sites you visit.
        """),
        ("10. Security", """
We implement industry-standard security measures to protect your information. However, no
method of transmission over the internet or electronic storage is 100% secure.
We cannot guarantee absolute security.
        """),
        ("11. Changes to This Policy", """
We may update this Privacy Policy from time to time. We will notify you of changes by
updating the "Last updated" date at the top of this page. Your continued use of DataViz Pro
after any changes constitutes your acceptance of the new policy.
        """),
        ("12. Contact Us", """
If you have questions about this Privacy Policy, please contact us at:

**DataViz Pro**
Email: privacy@datavizpro.app

We will respond to your inquiry within 30 days.
        """),
    ]

    for title, body in sections:
        with st.expander(title, expanded=(title == "1. Introduction")):
            st.markdown(body)

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center;color:#9CA3AF;font-size:.8rem;padding:1rem 0;'>
        See also:
        <a href='#' style='color:#7C3AED;text-decoration:none;margin:0 .5rem;'>Terms of Service</a> ·
        <a href='#' style='color:#7C3AED;text-decoration:none;margin:0 .5rem;'>Cookie Policy</a>
    </div>
    """, unsafe_allow_html=True)
