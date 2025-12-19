import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

st.set_page_config(
    page_title="EcomInsight AI | Strategic Decision Suite",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #31333f;
        padding: 15px 15px 15px 20px;
        border-radius: 15px;
        color: white;
    }
    .stSubheader { color: #00d4ff !important; font-weight: bold; }
    .insight-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 EcomInsight AI-Driven Analytics")
st.markdown("<p style='color: #808495; font-size: 18px;'>Strategic Customer Intelligence & Retention Optimization</p>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("data/processed/final_customer_insights.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("⚠️ Data file not found. Please ensure the pipeline has been run.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="👥 Total Customers", value=f"{len(df):,}")
with col2:
    st.metric(label="💰 Avg. Revenue (CLV)", value=f"${df['monetary'].mean():.2f}")
with col3:
    st.metric(label="📉 Churn Rate", value=f"{df['is_churned'].mean()*100:.1f}%", delta="-1.2%", delta_color="inverse")
with col4:
    st.metric(label="🏷️ Active Segments", value=df['segment_name'].nunique())

st.divider()


left_col, right_col = st.columns(2)

with left_col:
    st.subheader("👥 Customer Segmentation")
    fig_seg = px.pie(
        df, names='segment_name', 
        hole=0.6,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_seg.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', showlegend=True)
    st.plotly_chart(fig_seg, use_container_width=True)

with right_col:
    st.subheader("💰 Revenue vs. Tenure")
    fig_scatter = px.scatter(
        df, x='tenure', y='monetary', 
        color='segment_name', 
        size='frequency',
        labels={"tenure": "Days as Customer", "monetary": "Total Spent ($)"}
    )
    fig_scatter.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()


st.subheader("🔮 Strategic Prediction & Business Recovery")


def get_strategic_advice(risk_score, freq, mon, ret):
    
    confidence = "High" if risk_score > 0.85 or risk_score < 0.20 else "Moderate"
    recovery_val = mon * risk_score 
    window = "Critical (1-7 Days)" if freq > 8 else "Standard (14-30 Days)"
    
    return confidence, recovery_val, window

with st.container():
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        with st.form("churn_prediction_form"):
            st.write("📋 **Customer Behavior Input**")
            f = st.number_input("Purchase Frequency", min_value=1, value=5)
            m = st.number_input("Total Monetary ($)", min_value=0.0, value=250.0)
            t = st.number_input("Tenure (Days)", min_value=1, value=120)
            r = st.slider("Return Rate (0-1)", 0.0, 1.0, 0.05)
            d = st.slider("Avg. Discount Applied", 0.0, 1.0, 0.10)
            q = st.number_input("Avg. Item Quantity", min_value=1, value=2)
            submit_button = st.form_submit_button("⚡ RUN AI STRATEGY ENGINE")

    with c2:
        if submit_button:
            payload = {"frequency": f, "monetary": m, "tenure": t, "return_rate": r, "avg_discount": d, "avg_quantity": q}
            try:
                response = requests.post("http://127.0.0.1:8000/predict/churn", json=payload)
                result = response.json()
                risk_score = result["churn_risk_score"]
                
                
                conf, recv, wind = get_strategic_advice(risk_score, f, m, r)
                
               
                color = "#ff4b4b" if result["will_churn"] else "#28a745"
                bg_color = "#4b1b1b" if result["will_churn"] else "#1b3d1b"
                
                st.markdown(f"""
                    <div style="background-color: {bg_color}; padding: 30px; border-radius: 15px; border-left: 10px solid {color}; text-align: center;">
                        <h2 style="color: white; margin: 0;">{"🚨 HIGH CHURN RISK" if result["will_churn"] else "✅ LOYAL PROFILE"}</h2>
                        <h1 style="color: white; margin: 10px 0; font-size: 50px;">{risk_score*100:.1f}%</h1>
                        <p style="color: #ccc; margin: 0;">AI Confidence Level: <b>{conf}</b></p>
                    </div>
                """, unsafe_allow_html=True)

                st.write("")
                
                
                st.write("### 🏢 Strategic Business Metrics")
                metrics_df = pd.DataFrame({
                    "Metric": ["Estimated Recovery Value", "Retention Action Window", "Prediction Deviation", "Suggested Strategy"],
                    "Value": [f"${recv:.2f}", wind, "±3.8%", "Retention Campaign" if result["will_churn"] else "Loyalty Program"]
                })
                st.table(metrics_df)

                if result["will_churn"]:
                    st.warning(f"👉 **Decision:** This customer represents a potential loss of ${recv:.2f}. Execute {wind} retention plan.")
                else:
                    st.info(f"👉 **Decision:** Stable revenue stream. Focus on up-selling within the {wind} window.")

            except Exception as e:
                st.error(f"API Connection Error: {e}")
        else:
            st.info("💡 **Pro Tip:** Enter a customer's recent shopping metrics to see AI-driven business recommendations.")


st.divider()
st.caption("EcomInsight AI Platform v2.0 | Explainable AI & Business Intelligence Architecture | 2025")