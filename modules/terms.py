import streamlit as st


def terms_page():
    st.markdown("""
    <div style='max-width:860px;margin:0 auto;'>
    <div style='margin-bottom:2rem;'>
        <div style='font-size:.7rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;
                    color:#7C3AED;margin-bottom:.4rem;'>Legal</div>
        <h1 style='font-size:2rem;font-weight:800;color:#1C1917;margin:0 0 .4rem;'>Terms of Service</h1>
        <div style='width:44px;height:4px;background:linear-gradient(90deg,#7C3AED,#F43F5E);
                    border-radius:2px;margin-bottom:.8rem;'></div>
        <p style='color:#6B7280;font-size:.875rem;'>Last updated: January 2025</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

    sections = [
        ("1. Agreement to Terms", """
By accessing or using DataViz Pro, you agree to be bound by these Terms of Service and our
Privacy Policy. If you do not agree, please do not use the application.

These Terms apply to all visitors, users, and others who access or use DataViz Pro.
        """),
        ("2. Description of Service", """
DataViz Pro is a no-code data analytics and visualisation platform that allows users to:
- Upload datasets (CSV, Excel, JSON, Parquet)
- Perform data cleaning and exploration
- Build interactive charts and dashboards
- Run machine learning analyses
- Export data and reports

The service is provided "as is" and may change or be discontinued at any time.
        """),
        ("3. User Responsibilities", """
You agree to use DataViz Pro only for lawful purposes and in accordance with these Terms.

You agree **not** to:
- Upload data that violates any applicable law or regulation
- Upload data containing personal information of third parties without their consent
- Attempt to reverse engineer, hack, or disrupt the service
- Use the service to distribute malware or harmful content
- Violate any applicable local, national, or international law

You are solely responsible for the data you upload and any results derived from it.
        """),
        ("4. Data and Privacy", """
Your uploaded files are processed during your session only and are not stored permanently.
Please review our Privacy Policy for full details on how we handle your data.

By uploading data, you represent and warrant that:
- You own the data or have the legal right to use it
- The data does not violate any third-party rights
- The data does not contain unlawfully obtained personal information
        """),
        ("5. Intellectual Property", """
The DataViz Pro application, including its design, code, features, and branding, is owned
by us and is protected by intellectual property laws.

You retain full ownership of the data you upload. We claim no intellectual property rights
over your data or the analyses you generate.

You may not copy, modify, distribute, sell, or lease any part of the DataViz Pro application
without our express written permission.
        """),
        ("6. Third-Party Services and Advertisements", """
DataViz Pro may display advertisements provided by third-party advertising networks, including
Google AdSense. These advertisements are governed by the respective third parties' terms and
privacy policies.

We may include links to third-party websites or services. We are not responsible for the
content, accuracy, or practices of those third parties.
        """),
        ("7. Disclaimer of Warranties", """
DataViz Pro is provided on an "AS IS" and "AS AVAILABLE" basis without any warranties,
express or implied, including but not limited to:
- Warranties of merchantability or fitness for a particular purpose
- Warranties that the service will be error-free or uninterrupted
- Warranties regarding the accuracy or reliability of analysis results

You use the service at your own risk. We do not guarantee that any analysis, chart, or
insight produced by DataViz Pro is accurate or suitable for making business decisions.
        """),
        ("8. Limitation of Liability", """
To the maximum extent permitted by applicable law, DataViz Pro and its operators shall not
be liable for any indirect, incidental, special, consequential, or punitive damages, including:
- Loss of data or profits
- Business interruption
- Errors in analysis results
- Decisions made based on outputs from the service

Our total liability shall not exceed the amount you paid for the service (if any) in the
twelve months preceding the claim.
        """),
        ("9. Indemnification", """
You agree to indemnify and hold harmless DataViz Pro and its operators from any claims,
losses, liabilities, damages, costs, or expenses (including legal fees) arising from:
- Your use of the service
- Your uploaded data
- Your violation of these Terms
- Your violation of any third-party rights
        """),
        ("10. Termination", """
We reserve the right to terminate or suspend your access to DataViz Pro at any time,
without notice, for conduct that we believe violates these Terms or is harmful to other
users, us, or third parties, or for any other reason at our sole discretion.
        """),
        ("11. Governing Law", """
These Terms shall be governed by and construed in accordance with applicable laws.
Any disputes arising from these Terms or your use of the service shall be subject to
the exclusive jurisdiction of the competent courts in the relevant jurisdiction.
        """),
        ("12. Changes to Terms", """
We reserve the right to modify these Terms at any time. We will notify you of material
changes by updating the "Last updated" date. Your continued use of DataViz Pro after any
changes constitutes your acceptance of the updated Terms.

It is your responsibility to review these Terms periodically.
        """),
        ("13. Contact", """
If you have questions about these Terms of Service, please contact us:

**DataViz Pro**
Email: legal@datavizpro.app

We will respond to your inquiry within 30 days.
        """),
    ]

    for title, body in sections:
        with st.expander(title, expanded=(title == "1. Agreement to Terms")):
            st.markdown(body)

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center;color:#9CA3AF;font-size:.8rem;padding:1rem 0;'>
        See also:
        <a href='#' style='color:#7C3AED;text-decoration:none;margin:0 .5rem;'>Privacy Policy</a> ·
        <a href='#' style='color:#7C3AED;text-decoration:none;margin:0 .5rem;'>Cookie Policy</a>
    </div>
    """, unsafe_allow_html=True)
