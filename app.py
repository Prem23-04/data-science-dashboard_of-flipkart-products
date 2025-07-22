import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="🛍️ Product Insights Dashboard", layout="wide")
st.title("🛍️ Product Insights from Uploaded Dataset")

# ───────────── File Upload ─────────────
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV File", type=["csv"])

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df = df.dropna(subset=["retail_price", "discounted_price", "brand"])
    df["Discount"] = df["retail_price"] - df["discounted_price"]
    return df

if uploaded_file:
    df = load_data(uploaded_file)

    st.subheader("📋 Preview of Dataset")
    st.dataframe(df.head())

    # ───────────── Search and Filter ─────────────
    st.sidebar.header("🔍 Filter Products")

    # Filter by brand
    brand_options = ["All Brands"] + sorted(df["brand"].dropna().unique())
    selected_brand = st.sidebar.selectbox("Select Brand", brand_options)
    if selected_brand != "All Brands":
        df = df[df["brand"] == selected_brand]

    # Search by product name
    search_term = st.text_input("🔎 Search Product Name")
    if search_term:
        df = df[df["product_name"].str.contains(search_term, case=False, na=False)]

    # ───────────── KPIs ─────────────
    st.subheader("📈 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Products", f"{df.shape[0]}")
    col2.metric("💲Average Retail Price", f"₹{df['retail_price'].mean():.2f}")
    col3.metric("🧾 Average Discount", f"₹{df['Discount'].mean():.2f}")

    # ───────────── Top Brands ─────────────
    st.subheader("🏷️ Top 10 Brands by Product Count")
    top_brands = df["brand"].value_counts().nlargest(10)
    st.bar_chart(top_brands)

    # ───────────── Discount Distribution ─────────────
    st.subheader("📉 Discount Distribution")
    fig1, ax1 = plt.subplots()
    sns.histplot(df["Discount"], bins=20, kde=True, ax=ax1)
    ax1.set_xlabel("Discount Amount")
    ax1.set_ylabel("Number of Products")
    st.pyplot(fig1)

    # ───────────── Price vs Discount ─────────────
    st.subheader("📌 Price vs Discount")
    fig2, ax2 = plt.subplots()
    sns.scatterplot(data=df, x="retail_price", y="Discount", hue="brand", alpha=0.6, ax=ax2)
    ax2.set_xlim(0, df["retail_price"].quantile(0.95))
    ax2.set_ylim(0, df["Discount"].quantile(0.95))
    st.pyplot(fig2)

    # ───────────── Top Discounts Table ─────────────
    st.subheader("🔥 Top 10 Highest Discounted Products")
    top_discounts = df.sort_values(by="Discount", ascending=False)[
        ["product_name", "brand", "retail_price", "discounted_price", "Discount"]
    ].head(10)
    st.dataframe(top_discounts)

else:
    st.info("Please upload a CSV file containing the following columns: `uniq_id`, `product_name`, `product_url`, `pid`, `retail_price`, `discounted_price`, and `brand`.")
