"""
SkyCity Auckland Restaurants & Bars — Order Channel Performance Dashboard
Run locally with:  streamlit run app.py
Place SkyCity_Auckland_Restaurants___Bars.csv in the same folder as this file.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="SkyCity Channel Analytics", layout="wide")

# ----------------------------
# Load & prepare data
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("SkyCity_Auckland_Restaurants___Bars.csv")

    # Recalculate TRUE channel shares from raw order counts
    # (the dataset's own share columns don't sum to 100% — validated separately)
    df["TrueInStoreShare"] = df["InStoreOrders"] / df["MonthlyOrders"]
    df["TrueUEShare"] = df["UberEatsOrders"] / df["MonthlyOrders"]
    df["TrueDDShare"] = df["DoorDashOrders"] / df["MonthlyOrders"]
    df["TrueSDShare"] = df["SelfDeliveryOrders"] / df["MonthlyOrders"]

    # KPI 2: Aggregator Dependence Index
    df["AggregatorDependence"] = df["TrueUEShare"] + df["TrueDDShare"]

    # KPI 4: Channel Diversification Score (1 - sum of squared shares)
    df["DiversificationScore"] = 1 - (
        df["TrueInStoreShare"] ** 2
        + df["TrueUEShare"] ** 2
        + df["TrueDDShare"] ** 2
        + df["TrueSDShare"] ** 2
    )

    # Risk flag: 70%+ reliance on a single aggregator
    df["RiskFlag"] = df.apply(
        lambda r: "HIGH RISK" if (r["TrueUEShare"] > 0.7 or r["TrueDDShare"] > 0.7) else "OK",
        axis=1,
    )
    return df


df = load_data()

# ----------------------------
# Sidebar — User Capabilities (filters)
# ----------------------------
st.sidebar.header("Filters")

subregion_filter = st.sidebar.multiselect(
    "Subregion", sorted(df["Subregion"].unique()), default=sorted(df["Subregion"].unique())
)
cuisine_filter = st.sidebar.multiselect(
    "Cuisine Type", sorted(df["CuisineType"].unique()), default=sorted(df["CuisineType"].unique())
)
segment_filter = st.sidebar.multiselect(
    "Segment", sorted(df["Segment"].unique()), default=sorted(df["Segment"].unique())
)
channel_toggle = st.sidebar.radio("Channel View", ["All Channels", "In-Store vs Delivery"])

filtered = df[
    df["Subregion"].isin(subregion_filter)
    & df["CuisineType"].isin(cuisine_filter)
    & df["Segment"].isin(segment_filter)
]

# ----------------------------
# Header
# ----------------------------
st.title("Order Channel Performance & Market Share — SkyCity Auckland")
st.caption("Restaurants & Bars | Channel Mix, Dependency Risk, and Regional Preference Analytics")

# Guard: stop cleanly if the current filter combination matches no restaurants,
# instead of letting every chart below error out on an empty dataframe.
if filtered.empty:
    st.warning(
        "No restaurants match this combination of Subregion / Cuisine / Segment filters. "
        "Try selecting a broader set of options in the sidebar."
    )
    st.stop()

# Apply the Channel View toggle: restrict which channels feed every chart below.
if channel_toggle == "In-Store vs Delivery":
    # Collapse the 3 delivery channels into one "Delivery" bucket for a simpler 2-way view
    filtered = filtered.copy()
    filtered["DeliveryOrders"] = (
        filtered["UberEatsOrders"] + filtered["DoorDashOrders"] + filtered["SelfDeliveryOrders"]
    )
    CHANNELS = ["InStoreOrders", "DeliveryOrders"]
    CHANNEL_LABELS = {"InStoreOrders": "In-Store", "DeliveryOrders": "Delivery (All Aggregators)"}
else:
    CHANNELS = ["InStoreOrders", "UberEatsOrders", "DoorDashOrders", "SelfDeliveryOrders"]
    CHANNEL_LABELS = {
        "InStoreOrders": "In-Store",
        "UberEatsOrders": "Uber Eats",
        "DoorDashOrders": "DoorDash",
        "SelfDeliveryOrders": "Self-Delivery",
    }

# ----------------------------
# KPI row
# ----------------------------
total_orders = filtered[CHANNELS].sum().sum()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Orders", f"{total_orders:,.0f}")
k2.metric("Avg. In-Store Reliance", f"{filtered['TrueInStoreShare'].mean()*100:.1f}%")
k3.metric("Avg. Aggregator Dependence", f"{filtered['AggregatorDependence'].mean()*100:.1f}%")
k4.metric("Restaurants at High Risk (70%+ single channel)", int((filtered["RiskFlag"] == "HIGH RISK").sum()))

st.divider()

# ----------------------------
# Module 1: Channel Mix Overview
# ----------------------------
st.subheader("Channel Mix Overview")

channel_totals = filtered[CHANNELS].sum().rename(index=CHANNEL_LABELS).reset_index()
channel_totals.columns = ["Channel", "Orders"]

col1, col2 = st.columns([1, 1])
with col1:
    fig_pie = px.pie(channel_totals, names="Channel", values="Orders", title="Overall Channel Share")
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    fig_bar = px.bar(channel_totals, x="Channel", y="Orders", title="Total Orders by Channel", text_auto=True)
    st.plotly_chart(fig_bar, use_container_width=True)

# ----------------------------
# Module 2: Subregion-wise Channel Heatmap
# ----------------------------
st.subheader("Subregion Channel Heatmap")

subregion_pivot = filtered.groupby("Subregion")[CHANNELS].sum().rename(columns=CHANNEL_LABELS)
subregion_share = subregion_pivot.div(subregion_pivot.sum(axis=1), axis=0)

fig_heat = px.imshow(
    subregion_share,
    text_auto=".1%",
    aspect="auto",
    color_continuous_scale="Blues",
    title="Channel Share (%) by Subregion",
)
st.plotly_chart(fig_heat, use_container_width=True)

# ----------------------------
# Module 3: Cuisine vs Channel Distribution
# ----------------------------
st.subheader("Cuisine vs Channel Distribution")

cuisine_pivot = filtered.groupby("CuisineType")[CHANNELS].sum().rename(columns=CHANNEL_LABELS)
cuisine_share = cuisine_pivot.div(cuisine_pivot.sum(axis=1), axis=0).reset_index()
cuisine_long = cuisine_share.melt(id_vars="CuisineType", var_name="Channel", value_name="Share")

fig_cuisine = px.bar(
    cuisine_long,
    x="CuisineType",
    y="Share",
    color="Channel",
    title="Channel Share by Cuisine Type",
    barmode="stack",
)
fig_cuisine.update_yaxes(tickformat=".0%")
st.plotly_chart(fig_cuisine, use_container_width=True)

# ----------------------------
# Module 4: Dependency Risk Panel
# ----------------------------
st.subheader("Channel Dependency Risk Panel")

risk_col1, risk_col2 = st.columns([1, 2])
with risk_col1:
    risk_counts = filtered["RiskFlag"].value_counts().reset_index()
    risk_counts.columns = ["Risk Status", "Count"]
    fig_risk = px.bar(risk_counts, x="Risk Status", y="Count", color="Risk Status", title="Restaurants by Risk Status")
    st.plotly_chart(fig_risk, use_container_width=True)

with risk_col2:
    st.markdown("**Restaurants with negative Uber Eats or DoorDash profitability**")
    unprofitable = filtered[(filtered["UberEatsNetProfit"] < 0) | (filtered["DoorDashNetProfit"] < 0)]
    st.dataframe(
        unprofitable[
            ["RestaurantName", "CuisineType", "Segment", "Subregion", "UberEatsNetProfit", "DoorDashNetProfit"]
        ].sort_values("UberEatsNetProfit"),
        use_container_width=True,
        height=300,
    )

# ----------------------------
# Module 5: Diversification Score Distribution
# ----------------------------
st.subheader("Channel Diversification Score Distribution")
fig_div = px.histogram(filtered, x="DiversificationScore", nbins=40, title="Distribution of Diversification Scores")
st.plotly_chart(fig_div, use_container_width=True)

st.caption(
    "Note: The dataset's provided share columns (InStoreShare, UE_share, DD_share, SD_share) do not sum to 100% "
    "and are excluded from this analysis. All shares here are recalculated directly from raw order counts."
)
