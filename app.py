
from security_analysis import analyze_email
import sqlite3
from datetime import datetime
from pathlib import Path    

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="PhishGuard | Email Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"
DB_PATH = BASE_DIR / "detection_history.db"

# Dataset figures from the validated cleaned dataset.
TOTAL_EMAILS = 17_520
SAFE_EMAILS = 10_977
PHISHING_EMAILS = 6_543
TRAINING_RECORDS = 14_016
TEST_RECORDS = 3_504

# Model evaluation results from the reported held-out test run.
MODEL_RESULTS = pd.DataFrame(
    [
        {
            "Model": "Logistic Regression",
            "Accuracy": 97.95,
            "Phishing Precision": 98.0,
            "Phishing Recall": 97.0,
            "Phishing F1": 97.24,
        },
        {
            "Model": "Naive Bayes",
            "Accuracy": 97.35,
            "Phishing Precision": 99.0,
            "Phishing Recall": 94.0,
            "Phishing F1": 96.36,
        },
        {
            "Model": "Linear SVM",
            "Accuracy": 98.80,
            "Phishing Precision": 98.0,
            "Phishing Recall": 99.0,
            "Phishing F1": 98.40,
        },
    ]
)

# Confusion matrix order: rows = actual [Safe, Phishing],
# columns = predicted [Safe, Phishing].
SVM_CONFUSION_MATRIX = [[2172, 23], [19, 1290]]


# =========================================================
# DATABASE
# =========================================================
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detected_at TEXT NOT NULL,
                prediction TEXT NOT NULL,
                email_preview TEXT NOT NULL
            )
            """
        )
        connection.commit()


def save_detection(prediction, email_text):
    preview = " ".join(email_text.split())[:300]
    detected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO detections (detected_at, prediction, email_preview)
            VALUES (?, ?, ?)
            """,
            (detected_at, prediction, preview),
        )
        connection.commit()


def load_detection_history():
    with get_connection() as connection:
        return pd.read_sql_query(
            """
            SELECT
                id AS "ID",
                detected_at AS "Time",
                prediction AS "Prediction",
                email_preview AS "Email Preview"
            FROM detections
            ORDER BY id DESC
            """,
            connection,
        )


def clear_detection_history():
    with get_connection() as connection:
        connection.execute("DELETE FROM detections")
        connection.commit()


initialize_database()


# =========================================================
# LOAD MODEL
# =========================================================
@st.cache_resource
def load_model(model_path):
    return joblib.load(model_path)


model = None
model_error = None

try:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}\n"
            "Check that models/best_model.pkl exists in your project."
        )
    model = load_model(str(MODEL_PATH))
except Exception as exc:
    model_error = str(exc)


# =========================================================
# CUSTOM DESIGN
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #101827;
        color: #E8EEF7;
        font-family: "Segoe UI", sans-serif;
    }

    .block-container {
        max-width: 1500px;
        padding: 2rem 2.5rem;
    }

    section[data-testid="stSidebar"] {
        background: #111C2E;
        border-right: 1px solid #2B3C54;
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 1.8rem 1rem;
    }

    section[data-testid="stSidebar"] h1 {
        font-size: 27px !important;
        font-weight: 750;
        color: #F8FAFC !important;
    }

    section[data-testid="stSidebar"] h3 {
        font-size: 15px !important;
        font-weight: 750;
        letter-spacing: 0.7px;
        color: #93C5FD !important;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    section[data-testid="stSidebar"] p {
        font-size: 13px !important;
        line-height: 1.7 !important;
        color: #B8C6D8;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 7px 9px;
        border-radius: 7px;
        margin-bottom: 5px;
        min-height: 35px;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 14px !important;
        font-weight: 550;
        color: #DCE6F2 !important;
    }

    section[data-testid="stSidebar"] hr,
    hr {
        border-color: #30435C;
        margin-top: 19px;
        margin-bottom: 19px;
    }

    .hero {
        background: linear-gradient(110deg, #17365D, #10504F);
        padding: 28px 30px;
        border: 1px solid #31566C;
        border-radius: 15px;
        margin-bottom: 28px;
    }

    .hero h1 {
        color: #FFFFFF !important;
        font-size: 34px !important;
        font-weight: 750 !important;
        margin: 0 0 8px 0;
    }

    .hero p {
        color: #D6E5F2;
        font-size: 15px;
        margin: 0;
    }

    .metric-card {
        background: #1B2A40;
        padding: 20px;
        border: 1px solid #30435C;
        border-radius: 13px;
        min-height: 112px;
    }

    .metric-label {
        color: #A9BCD2;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .metric-value {
        color: #FFFFFF;
        font-size: 29px;
        font-weight: 750;
        margin-top: 10px;
    }

    .stButton > button {
        min-height: 42px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 650;
    }

    .stButton > button[kind="primary"] {
        background: #2563EB !important;
        color: #FFFFFF !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 9px !important;
        font-size: 15px !important;
        font-weight: 650 !important;
        min-height: 45px;
    }

    .stButton > button[kind="primary"]:hover {
        background: #1D4ED8 !important;
    }

    textarea {
        background-color: #1B2A40 !important;
        color: #FFFFFF !important;
    }

    .small-note {
        color: #B8C6D8;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown("# 🛡️ PhishGuard")
    st.caption("EMAIL SECURITY PLATFORM")
    st.divider()

    st.markdown("### WORKSPACE")
    page = st.radio(
        "Navigation",
        [
            "Email Threat Analyzer",
            "Detection Analytics",
            "Detection History",
            "Model Evaluation",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("### DETECTION PIPELINE")

    st.markdown(
        """
        **01 · TF-IDF**

        <p style="color:#94A3B8;font-size:12px;margin-top:-8px;margin-bottom:14px;">
        Email text feature extraction
        </p>

        **02 · Linear SVM**

        <p style="color:#4ADE80;font-size:12px;margin-top:-8px;margin-bottom:14px;">
        Selected classification model
        </p>

        **03 · Binary Classification**

        <p style="color:#94A3B8;font-size:12px;margin-top:-8px;margin-bottom:5px;">
        Safe Email / Phishing Email
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown("### PROJECT STATUS")

    if model is not None:
        st.success("✓ Model Loaded Successfully")
    else:
        st.error("Model Loading Failed")

    st.caption("M.Tech Cybersecurity Project")
    st.caption("PhishGuard · Version 1.0")


# =========================================================
# MAIN HEADER
# =========================================================
st.markdown(
    """
    <div class="hero">
        <h1>🛡️ PhishGuard</h1>
        <p>Machine Learning-Based Phishing Email Detection System</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if model_error:
    st.error("The trained model could not be loaded.")
    st.code(model_error)
    st.info(
        "Verify that models/best_model.pkl exists and that the "
        "required Python packages are installed."
    )
    st.stop()


# =========================================================
# HELPER: KPI CARD
# =========================================================
def render_metric_card(column, label, value):
    with column:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# PAGE 1: EMAIL THREAT ANALYZER
# =========================================================
if page == "Email Threat Analyzer":
    st.subheader("Email Threat Analyzer")
    st.markdown(
        '<p class="small-note">Analyze email text using the trained '
        "TF-IDF and Linear SVM classification pipeline.</p>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("#### 📧 Email Content")

        email_text = st.text_area(
            "Paste email message",
            height=230,
            placeholder="Paste the email subject and body here...",
            label_visibility="collapsed",
            key="email_input",
        )

        analyze_clicked = st.button(
            "🔍 Analyze Email",
            type="primary",
            use_container_width=True,
        )

    if analyze_clicked:
        if not email_text.strip():
            st.warning("Please enter email content before analyzing.")
        else:
            try:
                # 1. Existing ML model prediction
                prediction = str(model.predict([email_text])[0])

                if prediction not in ("Safe Email", "Phishing Email"):
                    st.error(f"Unexpected model output: {prediction}")
                else:
                    # 2. New security analysis
                    security_report = analyze_email(email_text)

                    # 3. Save existing detection history
                    save_detection(prediction, email_text)

                    st.divider()
                    st.markdown("### Classification Result")

                    if prediction == "Phishing Email":
                        st.error("⚠️ Potential Phishing Email Detected")
                        st.write(
                            "The Linear SVM model classified this email "
                            "as phishing."
                        )
                    else:
                        st.success("✅ Classified as Safe Email")
                        st.write(
                            "The Linear SVM model classified this email "
                            "as safe. This does not guarantee that it is harmless."
                        )

                    # 4. Security indicators
                    st.markdown("### Security Indicator Analysis")

                    indicators = security_report["indicators"]
                    url_findings = security_report["url_findings"]

                    if indicators:
                        st.warning(
                            f"{len(indicators)} suspicious language "
                            "category/categories detected."
                        )

                        for item in indicators:
                            st.markdown(
                                f"**{item['indicator']}** — "
                                f"{item['description']}"
                            )
                    else:
                        st.success(
                            "No configured suspicious-language patterns "
                            "were detected."
                        )

                    # 5. URL analysis
                    st.markdown("### URL Analysis")

                    if security_report["urls"]:
                        for item in url_findings:
                            st.markdown(f"**URL:** `{item['url']}`")

                            if item["findings"]:
                                for finding in item["findings"]:
                                    st.write(f"- ⚠️ {finding}")
                            else:
                                st.write(
                                    "- No configured URL warning patterns found."
                                )
                    else:
                        st.info("No URLs detected in the submitted email.")

                    # 6. Recommended action
                    st.markdown("### Recommended Action")

                    if prediction == "Phishing Email" or indicators or any(
                        item["findings"] for item in url_findings
                    ):
                        st.warning(
                            "Treat this email cautiously. Do not click "
                            "links or share credentials. Verify the sender "
                            "through an independently known contact method."
                        )
                    else:
                        st.info(
                            "No configured warning indicators were found. "
                            "Still verify the sender and context before "
                            "trusting the email."
                        )

                    st.caption(
                        "ML classification and rule-based indicators are "
                        "separate checks. URL pattern analysis does not "
                        "verify website reputation or prove a URL is safe."
                    )

                    st.success("Detection record saved to Detection History.")

            except Exception as exc:
                st.error("Email analysis failed.")
                st.exception(exc)


            except Exception as exc:
                st.error("Email analysis failed.")
                st.exception(exc)

    st.caption(
        "Always verify suspicious senders, links, and attachments independently."
    )


# =========================================================
# PAGE 2: DETECTION ANALYTICS
# =========================================================
elif page == "Detection Analytics":
    st.subheader("Detection Analytics")
    st.caption(
        "Explore the validated dataset, compare trained models, "
        "and monitor emails analyzed by this application."
    )

    history_df = load_detection_history()
    total_analyzed = len(history_df)

    if total_analyzed:
        phishing_detected = int(
            (history_df["Prediction"] == "Phishing Email").sum()
        )
        safe_detected = int(
            (history_df["Prediction"] == "Safe Email").sum()
        )
    else:
        phishing_detected = 0
        safe_detected = 0

    st.markdown("### Live Detection Summary")
    live_cols = st.columns(3)
    render_metric_card(live_cols[0], "TOTAL ANALYZED", f"{total_analyzed:,}")
    render_metric_card(live_cols[1], "PHISHING DETECTED", f"{phishing_detected:,}")
    render_metric_card(live_cols[2], "SAFE CLASSIFIED", f"{safe_detected:,}")

    st.caption(
        "Live figures are based on records saved by this application. "
        "They are not counts of all emails received by an organization."
    )

    st.divider()
    st.markdown("### 1. Dataset Distribution")

    dataset = pd.DataFrame(
        {
            "Email Type": ["Safe Email", "Phishing Email"],
            "Records": [SAFE_EMAILS, PHISHING_EMAILS],
        }
    )

    dataset_col, dataset_note_col = st.columns([1.4, 1])

    with dataset_col:
        fig_dataset = px.pie(
            dataset,
            names="Email Type",
            values="Records",
            hole=0.58,
            color="Email Type",
            color_discrete_map={
                "Safe Email": "#22C55E",
                "Phishing Email": "#EF4444",
            },
        )
        fig_dataset.update_traces(
            textinfo="label+percent",
            textfont_size=13,
            hovertemplate=(
                "%{label}<br>Records: %{value:,}"
                "<br>Share: %{percent}<extra></extra>"
            ),
        )
        fig_dataset.update_layout(
            template="plotly_dark",
            paper_bgcolor="#101827",
            plot_bgcolor="#101827",
            font_color="#E8EEF7",
            height=360,
            margin=dict(t=25, b=25, l=20, r=20),
            legend_title_text="Email Class",
        )
        st.plotly_chart(fig_dataset, use_container_width=True)

    with dataset_note_col:
        st.markdown("#### Validated dataset")
        st.metric("Total cleaned emails", f"{TOTAL_EMAILS:,}")
        st.metric("Safe emails", f"{SAFE_EMAILS:,}", "62.65%")
        st.metric("Phishing emails", f"{PHISHING_EMAILS:,}", "37.35%")
        st.caption(
            "These figures come from the cleaned dataset used for model "
            "development. They do not change when new emails are tested."
        )

    st.divider()
    st.markdown("### 2. Machine Learning Model Comparison")

    fig_models = px.bar(
        MODEL_RESULTS,
        x="Accuracy",
        y="Model",
        orientation="h",
        text="Accuracy",
        color="Model",
        color_discrete_map={
            "Logistic Regression": "#64748B",
            "Naive Bayes": "#F59E0B",
            "Linear SVM": "#22C55E",
        },
    )
    fig_models.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        cliponaxis=False,
    )
    fig_models.update_layout(
        template="plotly_dark",
        paper_bgcolor="#101827",
        plot_bgcolor="#101827",
        font_color="#E8EEF7",
        height=330,
        xaxis=dict(title="Accuracy (%)", range=[0, 110]),
        yaxis_title="",
        showlegend=False,
        margin=dict(t=20, b=30, l=20, r=60),
    )
    st.plotly_chart(fig_models, use_container_width=True)

    st.caption(
        "Model comparison values are from the reported held-out test run. "
        "They remain fixed unless the models are retrained and the results updated."
    )

    st.divider()
    st.markdown("### 3. Linear SVM Confusion Matrix")

    fig_cm = go.Figure(
        data=go.Heatmap(
            z=SVM_CONFUSION_MATRIX,
            x=["Predicted Safe", "Predicted Phishing"],
            y=["Actual Safe", "Actual Phishing"],
            colorscale=[
                [0, "#17365D"],
                [0.5, "#176B91"],
                [1, "#22C55E"],
            ],
            text=SVM_CONFUSION_MATRIX,
            texttemplate="%{text}",
            textfont={"size": 20},
            hovertemplate="%{y}<br>%{x}<br>Count: %{z}<extra></extra>",
        )
    )
    fig_cm.update_layout(
        template="plotly_dark",
        paper_bgcolor="#101827",
        plot_bgcolor="#101827",
        font_color="#E8EEF7",
        height=350,
        margin=dict(t=25, b=40, l=40, r=20),
    )
    st.plotly_chart(fig_cm, use_container_width=True)
    st.caption(
        "Rows represent actual classes and columns represent predicted "
        "classes. Class order: Safe Email, then Phishing Email."
    )

    st.divider()
    st.markdown("### 4. Live Detection Activity")

    if total_analyzed > 0:
        live_distribution = pd.DataFrame(
            {
                "Result": ["Safe Email", "Phishing Email"],
                "Count": [safe_detected, phishing_detected],
            }
        )

        live_col, recent_col = st.columns([1, 1.3])

        with live_col:
            fig_live = px.pie(
                live_distribution,
                names="Result",
                values="Count",
                hole=0.60,
                color="Result",
                color_discrete_map={
                    "Safe Email": "#22C55E",
                    "Phishing Email": "#EF4444",
                },
            )
            fig_live.update_traces(
                textinfo="label+value+percent",
                hovertemplate="%{label}<br>Count: %{value}<extra></extra>",
            )
            fig_live.update_layout(
                template="plotly_dark",
                paper_bgcolor="#101827",
                plot_bgcolor="#101827",
                font_color="#E8EEF7",
                height=330,
                title="Saved Detection Distribution",
            )
            st.plotly_chart(fig_live, use_container_width=True)

        with recent_col:
            st.markdown("#### Recent analyzed emails")
            st.dataframe(
                history_df.head(8),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info(
            "No emails have been analyzed yet. Use Email Threat Analyzer "
            "to generate live detection statistics."
        )


# =========================================================
# PAGE 3: DETECTION HISTORY
# =========================================================
elif page == "Detection History":
    st.subheader("Detection History")
    st.caption(
        "Previously analyzed email previews and their model predictions."
    )

    history_df = load_detection_history()

    if not history_df.empty:
        total_records = len(history_df)
        phishing_records = int(
            (history_df["Prediction"] == "Phishing Email").sum()
        )
        safe_records = int(
            (history_df["Prediction"] == "Safe Email").sum()
        )

        cols = st.columns(3)
        render_metric_card(cols[0], "TOTAL RECORDS", f"{total_records:,}")
        render_metric_card(cols[1], "PHISHING", f"{phishing_records:,}")
        render_metric_card(cols[2], "SAFE", f"{safe_records:,}")

        st.write("")
        search_text = st.text_input(
            "Search email preview",
            placeholder="Enter a word or phrase to filter history...",
        )

        filtered_df = history_df.copy()
        if search_text.strip():
            filtered_df = filtered_df[
                filtered_df["Email Preview"].str.contains(
                    search_text, case=False, na=False
                )
            ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download history as CSV",
            data=csv_data,
            file_name="phishguard_detection_history.csv",
            mime="text/csv",
        )

        st.warning(
            "Clearing history permanently deletes the locally stored "
            "detection records in detection_history.db."
        )
        if st.button("Clear All Detection History", type="secondary"):
            clear_detection_history()
            st.success("Detection history cleared.")
            st.rerun()
    else:
        st.info(
            "No email analysis records yet. Start by analyzing an email."
        )


# =========================================================
# PAGE 4: MODEL EVALUATION
# =========================================================
elif page == "Model Evaluation":
    st.subheader("Model Evaluation")
    st.caption(
        "Performance comparison on the held-out test dataset."
    )

    eval_cols = st.columns(3)
    render_metric_card(eval_cols[0], "TRAINING RECORDS", f"{TRAINING_RECORDS:,}")
    render_metric_card(eval_cols[1], "TEST RECORDS", f"{TEST_RECORDS:,}")
    render_metric_card(eval_cols[2], "BEST TEST ACCURACY", "98.80%")

    st.write("")
    st.markdown("### Algorithm Performance Comparison")

    st.dataframe(
        MODEL_RESULTS.style.format(
            {
                "Accuracy": "{:.2f}%",
                "Phishing Precision": "{:.2f}%",
                "Phishing Recall": "{:.2f}%",
                "Phishing F1": "{:.2f}%",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.success(
        "Selected model: Linear SVM — highest reported accuracy "
        "and phishing F1-score among the three evaluated models."
    )

    st.markdown("### Linear SVM Confusion Matrix")

    matrix_df = pd.DataFrame(
        SVM_CONFUSION_MATRIX,
        index=["Actual Safe", "Actual Phishing"],
        columns=["Predicted Safe", "Predicted Phishing"],
    )
    st.dataframe(matrix_df, use_container_width=True)

    st.markdown("### Interpretation")
    st.write(
        "- True Safe: 2,172 safe emails correctly classified as safe.\n"
        "- False Phishing: 23 safe emails incorrectly classified as phishing.\n"
        "- False Safe: 19 phishing emails incorrectly classified as safe.\n"
        "- True Phishing: 1,290 phishing emails correctly classified as phishing."
    )

    st.warning(
        "These are results from the current held-out test split. "
        "They do not guarantee the same performance on unseen real-world emails."
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()
st.caption(
    "PhishGuard | Machine Learning-Based Phishing Email Detection System "
    "| Academic Project"
)
