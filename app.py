import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Flipkart Product Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("flipkart_com-ecommerce_sample.csv")
    df = df.dropna(subset=["retail_price", "discounted_price", "product_category_tree", "brand"])
    df["Main_Category"] = df["product_category_tree"].str.extract(r'\["([^>]+)')
    df["Discount"] = df["retail_price"] - df["discounted_price"]
    df["crawl_timestamp"] = pd.to_datetime(df["crawl_timestamp"], errors='coerce')
    df["product_rating"] = df["product_rating"].replace("No rating available", pd.NA)
    return df

df = load_data()

st.title("🛍️ Flipkart E-Commerce Product Dashboard")

# ───────────── Sidebar Filters ─────────────
st.sidebar.header("🔍 Filter Products")

# Brand dropdown
brand_options = ["All Brands"] + sorted(df["brand"].dropna().unique())
selected_brand = st.sidebar.selectbox("Select Brand", brand_options)

# Filter data based on brand
if selected_brand != "All Brands":
    brand_filtered_df = df[df["brand"] == selected_brand]
else:
    brand_filtered_df = df.copy()

# Category dropdown based on selected brand
category_options = sorted(brand_filtered_df["Main_Category"].dropna().unique())
selected_categories = st.sidebar.multiselect("Select Categories", category_options, default=category_options)

# Filtered data based on categories
filtered_df = brand_filtered_df[brand_filtered_df["Main_Category"].isin(selected_categories)]

# ───────────── Search by Product Name ─────────────
search_term = st.text_input("🔎 Search Product Name")
if search_term:
    filtered_df = filtered_df[filtered_df["product_name"].str.contains(search_term, case=False, na=False)]

# ───────────── KPIs ─────────────
avg_price = filtered_df["retail_price"].mean()
avg_discount = filtered_df["Discount"].mean()
total_products = filtered_df.shape[0]

st.metric("📦 Total Products", f"{total_products}")
st.metric("💲Average Retail Price", f"₹{avg_price:.2f}")
st.metric("🧾 Average Discount", f"₹{avg_discount:.2f}")

# ───────────── Timeline Chart ─────────────
st.subheader("🕒 Product Crawl Timeline")
timeline_df = filtered_df.groupby(filtered_df["crawl_timestamp"].dt.date).size()
st.line_chart(timeline_df)

# ───────────── Rating Distribution ─────────────
st.subheader("⭐ Product Rating Distribution")
rating_df = filtered_df["product_rating"].dropna()
if not rating_df.empty:
    fig3, ax3 = plt.subplots()
    sns.countplot(x=rating_df, order=rating_df.value_counts().index, ax=ax3)
    ax3.set_xlabel("Product Rating")
    ax3.set_ylabel("Count")
    st.pyplot(fig3)
else:
    st.info("No valid product ratings available.")

# ───────────── Discount by Category ─────────────
st.subheader("📉 Average Discount by Category")
fig1, ax1 = plt.subplots()
sns.barplot(data=filtered_df, x="Main_Category", y="Discount", estimator='mean', ci=None, ax=ax1)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha="right")
st.pyplot(fig1)

# ───────────── Price vs Discount ─────────────
st.subheader("📌 Price vs Discount Scatter Plot")
fig4, ax4 = plt.subplots()
sns.scatterplot(data=filtered_df, x="retail_price", y="Discount", hue="Main_Category", alpha=0.6, ax=ax4)
ax4.set_xlim(0, filtered_df["retail_price"].quantile(0.95))  # remove extreme outliers
ax4.set_ylim(0, filtered_df["Discount"].quantile(0.95))
st.pyplot(fig4)

# ───────────── Top Brands ─────────────
st.subheader("🏷️ Top 10 Brands by Product Count")
top_brands = filtered_df["brand"].value_counts().nlargest(10)
st.bar_chart(top_brands)

# ───────────── Top Discounts Table ─────────────
st.subheader("🔥 Top 10 Highest Discount Products")
top_discounts = filtered_df.sort_values(by="Discount", ascending=False)[["product_name", "brand", "retail_price", "discounted_price", "Discount"]].head(10)
st.dataframe(top_discounts)
