import pandas as pd
import warnings
import streamlit as st
import plotly.express as px


pd.set_option("display.max.columns", 500)
warnings.filterwarnings("ignore")
st.set_page_config(page_title="Retail Sales Dashboard",
                   page_icon=":bar_chart:",
                   layout="wide")


@st.cache_data
def get_data():
    data = pd.read_csv("sales.csv")

    data["Order Date"] = pd.to_datetime(data["Order Date"], format="%d/%m/%Y", errors="coerce")
    data["Ship Date"] = pd.to_datetime(data["Ship Date"], format="%d/%m/%Y", errors="coerce")

    data["Month"] = data["Order Date"].dt.strftime("%b")
    data["Year"] = data["Order Date"].dt.year

    column_selection = ['Customer ID', "Order Date", "Ship Date", "Ship Mode", "Segment", "State",
                        "Category", "Sub-Category", "Month", "Year", "Sales"]

    return data[column_selection]


df = get_data()

# print(df.info())
# print(df.head())
# st.dataframe(df)

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
year = st.sidebar.multiselect(
    "Select the Year:",
    options=df["Year"].sort_values().unique(),
    # default=df["Year"].unique()
)
state = st.sidebar.multiselect(
    "Select the State:",
    options=df["State"].sort_values().unique(),
    # default=df["State"].unique()
)
# month = st.sidebar.multiselect(
#     "Select the Month:",
#     options=df["Month"].sort_values().unique(),
#     # default=df["Month"].unique()
# )

df_selection = df.query(
    "State == @state & Year == @year"
)

# st.dataframe(df_selection)


# ---- MainPage ----
st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

# ---- TOP KPI's ----

total_sales = int(df_selection["Sales"].sum())
average_sales = round(df_selection["Sales"].mean(), 2)
number_of_transactions = df_selection["Sales"].count()

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales")
    st.subheader(f"US $ {total_sales:,}")
with middle_column:
    st.subheader("Average Sales")
    st.subheader(f"US $ {average_sales:,}")
with right_column:
    st.subheader("Number of Transactions")
    st.subheader(f"{number_of_transactions:}")


st.markdown("---")
month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
monthly_sales = df_selection.groupby("Month")["Sales"].sum().reindex(month_order).reset_index()
fig1 = px.line(monthly_sales, x="Month", y="Sales", title="Monthly Sales ")

fig1.update_layout(xaxis_title=None)
st.plotly_chart(fig1, use_container_width=True)
st.markdown("---")
# SALES BY SUB CATEGORY (BAR CHART)

sales_by_sub_category = df_selection.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=True)

fig_product_sales = px.bar(
    sales_by_sub_category,
    x="Sales",
    y=sales_by_sub_category.index,
    orientation="h",
    title="<b>Sales by Sub Category</b>",
    color_discrete_sequence=["#0083BB"] * len(sales_by_sub_category),
    template="plotly_white"
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)


# Segment contribution
segment_contribution = df_selection.groupby('Segment')['Sales'].sum() / df['Sales'].sum() * 100

fig_segment_distribution = px.pie(
    segment_contribution,
    names=segment_contribution.index,
    values="Sales",
    hole=0.5,
    title="Segment Contribution to Overall Sales"

)

# Customize the layout for a better appearance
fig_segment_distribution.update_layout(
    annotations=[dict(text=f"Sales\n${total_sales}", x=0.5, y=0.5, font_size=20, showarrow=False)]
)


left_col, right_col = st.columns(2)
left_col.plotly_chart(fig_product_sales, use_container_width=True)
right_col.plotly_chart(fig_segment_distribution, use_container_width=True)

# HIDE STREAMLIT STYLE
hide_st_style = """
<style>
#ManiMenu {visibility: hidden;}
footer{visibility: hidden;}
header{visibility:hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)


fig = px.histogram(df_selection, x="Ship Mode", color='Category',
                   labels={'ship_mode': 'Ship Mode', 'category': 'Category'},
                   color_discrete_map={'Office Supplies': '#7FD4C1', 'Technology': '#30BFDD', 'Furniture': '#8690FF'},
                   title='Category Distribution for Ship Mode')

# Customize the layout
fig.update_xaxes(categoryorder="total descending")
fig.update_layout(xaxis_title=None, yaxis_title='Count', xaxis=(dict(showgrid=False)), yaxis=(dict(showgrid=False)))
st.plotly_chart(fig, use_container_width=True)
