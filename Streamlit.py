import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import urllib
import unidecode
import matplotlib.image as mpimg
import streamlit as st

# Load your datasets
customers_df = pd.read_csv("f:/SELF LEARNING/Python/customers_dataset.csv")
orders_df = pd.read_csv("f:/SELF LEARNING/Python/orders_dataset.csv")
products_df = pd.read_csv("f:/SELF LEARNING/Python/products_dataset.csv")
sellers_df = pd.read_csv("f:/SELF LEARNING/Python/sellers_dataset.csv")
items_df = pd.read_csv("f:/SELF LEARNING/Python/order_items_dataset.csv")
reviews_df = pd.read_csv("f:/SELF LEARNING/Python/order_reviews_dataset.csv")
payments_df = pd.read_csv("f:/SELF LEARNING/Python/order_payments_dataset.csv")
category_df = pd.read_csv("f:/SELF LEARNING/Python/product_category_name_translation.csv")
geolocation_df = pd.read_csv("f:/SELF LEARNING/Python/geolocation_dataset.csv")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import urllib
import unidecode
import matplotlib.image as mpimg
import streamlit as st

# Load your datasets
customers_df = pd.read_csv("f:/SELF LEARNING/Python/customers_dataset.csv")
orders_df = pd.read_csv("f:/SELF LEARNING/Python/orders_dataset.csv")
products_df = pd.read_csv("f:/SELF LEARNING/Python/products_dataset.csv")
sellers_df = pd.read_csv("f:/SELF LEARNING/Python/sellers_dataset.csv")
items_df = pd.read_csv("f:/SELF LEARNING/Python/order_items_dataset.csv")
reviews_df = pd.read_csv("f:/SELF LEARNING/Python/order_reviews_dataset.csv")
payments_df = pd.read_csv("f:/SELF LEARNING/Python/order_payments_dataset.csv")
category_df = pd.read_csv("f:/SELF LEARNING/Python/product_category_name_translation.csv")
geolocation_df = pd.read_csv("f:/SELF LEARNING/Python/geolocation_dataset.csv")

# Convert columns to datetime
datetime_1 = ["order_purchase_timestamp","order_approved_at","order_delivered_carrier_date","order_delivered_customer_date","order_estimated_delivery_date"]
for column in datetime_1:
    orders_df[column] = pd.to_datetime(orders_df[column])

datetime_2 = ["shipping_limit_date"]
for column in datetime_2:
    items_df[column] = pd.to_datetime(items_df[column])

datetime_3 = ["review_creation_date","review_answer_timestamp"]
for column in datetime_3:
    reviews_df[column] = pd.to_datetime(reviews_df[column])

reviews_df.fillna(value="There is no comments", inplace=True)

# Calculate delivery time
delivery_time = orders_df["order_delivered_customer_date"] - orders_df["order_delivered_carrier_date"]
delivery_time = delivery_time.apply(lambda x: x.total_seconds())
orders_df["delivery_time"] = round(delivery_time / 86400)

# Merge data
orders_cust_df = pd.merge(customers_df, orders_df, how="left", left_on="customer_id", right_on="customer_id")
payrev_df = pd.merge(payments_df, reviews_df, how="left", left_on="order_id", right_on="order_id")
customers_df = pd.merge(orders_cust_df, payrev_df, how="left", left_on="order_id", right_on="order_id")
item_seller_df = pd.merge(items_df, sellers_df, how="left", left_on="seller_id", right_on="seller_id")
prod_cat_df = pd.merge(products_df, category_df, how="left", left_on="product_category_name", right_on="product_category_name")
selprod_df = pd.merge(prod_cat_df, item_seller_df, how="left", left_on="product_id", right_on="product_id")
all_data = pd.merge(customers_df, selprod_df, how="left", left_on="order_id", right_on="order_id")

# Function to make the column names more readable
def pretty_string(column):
    column_space = ' '.join(column.split())
    return unidecode.unidecode(column_space.lower())

# Calculate product counts by category
sum_order_items_df = all_data.groupby("product_category_name_english")["product_id"].count().reset_index()
sum_order_items_df = sum_order_items_df.rename(columns={"product_id": "products"})
sum_order_items_df = sum_order_items_df.sort_values(by="products", ascending=False)
sum_order_items_df = sum_order_items_df.head(10)

# Plot bar charts for most and least sold products
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
colors_highest = ["#034202", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
colors_lowest = ["#AB0404", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Most sold products
sns.barplot(x="product_category_name_english", y="products", data=sum_order_items_df.head(5), palette=colors_highest, ax=ax[0])
ax[0].set_xlabel(None)
ax[0].set_ylabel(None)
ax[0].set_title("Most Sold Products", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelrotation=45, labelsize=12)

# Least sold products
sns.barplot(x="product_category_name_english", y="products", data=sum_order_items_df.sort_values(by="products", ascending=True).head(5), palette=colors_lowest, ax=ax[1])
ax[1].set_xlabel(None)
ax[1].set_ylabel(None)
ax[1].set_title("Least Sold Products", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelrotation=45, labelsize=12)

plt.suptitle("Most and Least Sold Products", fontsize=20)
st.pyplot(fig)

# Time series of orders in 2017
all_data['order_approved_at'] = pd.to_datetime(all_data['order_approved_at'])
data_2017 = all_data[all_data['order_approved_at'].dt.year == 2017]

monthly_df = data_2017.resample(rule='M', on='order_approved_at').agg({"order_id": "nunique"})
monthly_df.index = monthly_df.index.strftime('%B')
monthly_df = monthly_df.reset_index()
monthly_df.rename(columns={"order_id": "order_count", "order_approved_at": "month"}, inplace=True)

month_mapping = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}
monthly_df["month_numeric"] = monthly_df["month"].map(month_mapping)
monthly_df = monthly_df.sort_values("month_numeric")
monthly_df = monthly_df.drop("month_numeric", axis=1)

# Plot Number of Orders per Month (2017)
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(monthly_df["month"], monthly_df["order_count"], marker='o', linewidth=2, color="#068DA9")
ax.set_title("Number of Orders per Month (2017)", loc="center", fontsize=20)
ax.tick_params(axis='x', labelrotation=25, labelsize=10)
ax.tick_params(axis='y', labelsize=10)
st.pyplot(fig)


monthly_df = all_data.resample(rule='M', on='order_approved_at').agg({
    "order_id": "nunique",
})
monthly_df.index = monthly_df.index.strftime('%B')  # Change format of order_approved_at to month name
monthly_df = monthly_df.reset_index()
monthly_df.rename(columns={"order_id": "order_count"}, inplace=True)

# Sort values by order count
monthly_df = monthly_df.sort_values('order_count').drop_duplicates('order_approved_at', keep='last')

# Map months to numerical values
month_mapping = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

# Add numeric month values for sorting
monthly_df["month_numeric"] = monthly_df["order_approved_at"].map(month_mapping)
monthly_df = monthly_df.sort_values("month_numeric")

# Drop numeric month column
monthly_df = monthly_df.drop("month_numeric", axis=1)

# Plot Number of Orders per Month (2018)
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    monthly_df["order_approved_at"],
    monthly_df["order_count"],
    marker='o',
    linewidth=2,
    color="#068DA9"
)
ax.set_title("Number of Orders per Month (2018)", loc="center", fontsize=20)
ax.tick_params(axis='x', labelrotation=25, labelsize=10)
ax.tick_params(axis='y', labelsize=10)

# Display plot with Streamlit
st.pyplot(fig)






# Rating distribution
review_scores = all_data['review_score'].value_counts().sort_values(ascending=False)
most_common_score = review_scores.idxmax()

sns.set(style="darkgrid")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=review_scores.index, y=review_scores.values, order=review_scores.index,
            palette=["#034202" if score == most_common_score else "#D3D3D3" for score in review_scores.index], ax=ax)
ax.set_title("Customer Ratings", fontsize=15)
ax.set_xlabel("Rating")
ax.set_ylabel("Count")
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)



other_state_geolocation = geolocation_df.groupby(['geolocation_zip_code_prefix'])['geolocation_state'].nunique().reset_index(name='count')
other_state_geolocation_filtered = other_state_geolocation[other_state_geolocation['count'] >= 2]

max_state = geolocation_df.groupby(['geolocation_zip_code_prefix', 'geolocation_state']).size().reset_index(name='count').drop_duplicates(subset='geolocation_zip_code_prefix').drop('count', axis=1)

geolocation_silver = geolocation_df.groupby(['geolocation_zip_code_prefix', 'geolocation_city', 'geolocation_state'])[['geolocation_lat', 'geolocation_lng']].median().reset_index()
geolocation_silver = geolocation_silver.merge(max_state, on=['geolocation_zip_code_prefix', 'geolocation_state'], how='inner')

customers_silver = customers_df.merge(geolocation_silver, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='inner')

# Geolocation plot of customers
def plot_brazil_map(data):
    # Load the Brazil map image
    brazil_url = 'https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'
    brazil_img = mpimg.imread(urllib.request.urlopen(brazil_url), 'jpg')

    # Create the scatter plot
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(data['geolocation_lng'], data['geolocation_lat'], alpha=0.3, s=0.3, c='#034202')
    ax.set_axis_off()
    ax.imshow(brazil_img, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
    
    # Display the plot in Streamlit
    st.pyplot(fig)

# Display map using Streamlit
plot_brazil_map(customers_silver.drop_duplicates(subset='customer_unique_id'))
