import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------- PAGE CONFIGURATION --------------------
st.set_page_config(
    page_title="JNTUA CEA Placement Analysis",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- CUSTOM STYLING --------------------
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #f5f5f5;
        }
        h1 {
            text-align: center;
            color: #00e676;
            font-family: 'Trebuchet MS', sans-serif;
            font-weight: 900;
            text-shadow: 1px 1px 3px #000;
        }
        h2, h3 {
            color: #80deea;
            font-family: 'Trebuchet MS', sans-serif;
            font-weight: 700;
        }
        .metric-box {
            background-color: #263238;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            color: #00e676;
            box-shadow: 0px 0px 10px rgba(0, 230, 118, 0.5);
        }
        .company-box {
            background-color: #004d40;
            color: #ffffff;
            padding: 10px;
            border-radius: 8px;
            margin: 5px;
            text-align: center;
            font-weight: 600;
            display: inline-block;
            box-shadow: 0px 0px 8px rgba(255, 255, 255, 0.2);
        }
        [data-testid="stSidebar"] {
            background-color: #263238;
            color: #ffffff;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------- PAGE TITLE --------------------
st.title("🎓 JNTUA CEA Placement Analysis")

# -------------------- LOAD DATA --------------------
data_23 = pd.read_excel("22-23_batches.xlsx")
data_24 = pd.read_excel("23-24_batches.xlsx")
data_25 = pd.read_csv("24-25_batches.csv")
data_24.to_csv("output_file.csv", index=False)
data_23.to_csv("output_file.csv", index=False)

# Add year column
data_23["Year"] = 2023
data_24["Year"] = 2024
data_25["Year"] = 2025

# Combine all data
combined_data = pd.concat([data_23, data_24, data_25], ignore_index=True)

# Convert salary to LPA (assuming salary is in rupees)
combined_data["salary"] = pd.to_numeric(combined_data["salary"], errors="coerce").fillna(0)
combined_data["salary"] = (combined_data["salary"] / 100000).astype(int)

# -------------------- SIDEBAR --------------------
st.sidebar.title("📊 Dashboard Controls")
selected_year = st.sidebar.selectbox("Select Year:", [2023, 2024, 2025])

filtered_data = combined_data[combined_data["Year"] == selected_year]

# -------------------- TOP SUMMARY BOXES --------------------
st.header(f"📋 Placement Summary for {selected_year}")

# ✅ FIXED: Correct total count (no artificial reduction)
total_selected = filtered_data.shape[0]
avg_lpa = round(filtered_data["salary"].mean(), 2)

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='metric-box'>Students Got Selected in {selected_year}<br><h2>{total_selected}</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-box'>Average Package<br><h2>{avg_lpa} LPA</h2></div>", unsafe_allow_html=True)

# -------------------- BRANCH-WISE ANALYSIS --------------------
st.header(f"🏫 Branch-wise Placement Analysis ({selected_year})")

branch_salary = filtered_data.groupby("branch")["salary"].mean().reset_index()
fig_salary = px.bar(
    branch_salary,
    x="branch",
    y="salary",
    color="branch",
    text_auto=True,
    title=f"Average Salary by Branch ({selected_year})",
    color_discrete_sequence=px.colors.sequential.Tealgrn
)
fig_salary.update_layout(
    plot_bgcolor="#102027",
    paper_bgcolor="#102027",
    font=dict(color="#ffffff", size=14),
    yaxis_title="Average Package (LPA)"
)
st.plotly_chart(fig_salary, use_container_width=True)

# -------------------- TOTAL SELECTIONS BY BRANCH (ALL YEARS) --------------------
st.subheader("📈 Total Students Got Selected by Branch (2023–2025)")
placement_count = combined_data.groupby(["Year", "branch"]).size().reset_index(name="count")
fig_count = px.bar(
    placement_count,
    x="Year",
    y="count",
    color="branch",
    barmode="group",
    title="Total Students Got Selected by Branch Over the Years",
    color_discrete_sequence=px.colors.qualitative.Safe
)
fig_count.update_layout(
    plot_bgcolor="#102027",
    paper_bgcolor="#102027",
    font=dict(color="#ffffff", size=13),
    yaxis_title="Number of Students Selected"
)
st.plotly_chart(fig_count, use_container_width=True)

# -------------------- BRANCH-WISE DETAILED ANALYSIS --------------------
st.header(f"🏢 Company-wise Analysis ({selected_year})")

for branch in filtered_data["branch"].unique():
    with st.expander(f"{branch} Branch Analysis ({selected_year})"):
        branch_data = filtered_data[filtered_data["branch"] == branch]

        # ✅ FIXED: Use actual count, not reduced by 30%
        selected_students = branch_data.shape[0]
        avg_package = round(branch_data["salary"].mean(), 2)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='metric-box'>Students Got Selected in {selected_year}<br><h3>{selected_students}</h3></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-box'>Average Package<br><h3>{avg_package} LPA</h3></div>", unsafe_allow_html=True)

        # Company representation (bar chart)
        st.markdown(f"### 🏢 {branch} - Companies Visited in {selected_year}")
        company_count = branch_data["company"].value_counts().reset_index()
        company_count.columns = ["Company", "Count"]
        fig_company = px.bar(
            company_count,
            x="Company",
            y="Count",
            color="Company",
            title=f"{branch} - Company-wise Selection Count ({selected_year})",
            color_discrete_sequence=px.colors.qualitative.Dark2
        )
        fig_company.update_layout(
            plot_bgcolor="#102027",
            paper_bgcolor="#102027",
            font=dict(color="#ffffff", size=13),
            yaxis_title="Number of Students Selected"
        )
        st.plotly_chart(fig_company, use_container_width=True)

        # Company names in boxes
        st.markdown(f"### 🏢 Companies that selected students from {branch} in {selected_year}:")
        company_names = branch_data["company"].unique()
        company_html = "".join([f"<div class='company-box'>{name}</div>" for name in company_names])
        st.markdown(company_html, unsafe_allow_html=True)