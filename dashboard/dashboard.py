# Import necessary libraries
import pandas as pd
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import seaborn as sns  
import streamlit as st

# Function to create additional dataframes
def get_user_summary(df):
    """Summarizes total casual and registered users."""
    return df[['casual', 'registered', 'cnt']].sum().to_frame().T

def get_users_by_year(df):
    """Groups users by year."""
    return df.groupby('yr')[['casual', 'registered']].sum().reset_index()

def get_yearly_trend(df):
    """Creates a monthly user trend dataset."""
    df['month_year'] = df['dteday'].dt.to_period('M').astype(str)
    return df.groupby('month_year')[['casual', 'registered', 'cnt']].sum().reset_index()

def get_users_by_season(df):
    """Groups users by season."""
    return df.groupby('season')[['cnt']].sum().reset_index()

def get_users_by_month(df):
    """Groups users by month."""
    return df.groupby('mnth')[['cnt']].sum().reset_index()

def get_users_by_hour(df):
    """Groups users by hour."""
    users_by_hour = df.groupby('hr')[['casual', 'registered', 'cnt']].mean().reset_index()
    users_by_hour['cnt'] = users_by_hour['casual'] + users_by_hour['registered']
    return users_by_hour

# Helper functions for number formatting
def format_number(value):
    """Formats numbers with thousands separator."""
    return f"{value:,.0f}".replace(",", ".")

def format_large_number(value, pos):
    """Formats large numbers in K, M, or B format."""
    if value >= 1e9:
        return f'{value * 1e-9:.1f} B'
    elif value >= 1e6:
        return f'{value * 1e-6:.1f} M'
    elif value >= 1e3:
        return f'{value * 1e-3:.1f} K'
    return str(value)

# Load cleaned dataset
df = pd.read_csv("dashboard/cleaned_main_data.csv")

# Convert date columns to datetime
df['dteday'] = pd.to_datetime(df['dteday'])

# Streamlit page configuration
st.set_page_config(page_title="Bike Sharing System Dashboard", layout="wide")

# Get date range for filtering
min_date = df['dteday'].min()
max_date = df['dteday'].max()

# Sidebar with date filter
with st.sidebar:
    st.header("Bike Share System \n 2011 - 2012 Performance Report")

    start_date, end_date = st.date_input(
        "Select Date Range", min_value=min_date, max_value=max_date, value=[min_date, max_date]
    )

# Filter dataset based on selected date range
filtered_df = df[(df['dteday'] >= pd.to_datetime(start_date)) & (df['dteday'] <= pd.to_datetime(end_date))]

# Generate required datasets
user_summary_df = get_user_summary(filtered_df)
users_by_year_df = get_users_by_year(filtered_df)
yearly_trend_df = get_yearly_trend(filtered_df)
users_by_season_df = get_users_by_season(filtered_df)
users_by_month_df = get_users_by_month(filtered_df)
users_by_hour_df = get_users_by_hour(filtered_df)

# Correct month order
month_order = ["January", "February", "March", "April", "May", "June", 
               "July", "August", "September", "October", "November", "December"]

users_by_month_df["mnth"] = pd.Categorical(users_by_month_df["mnth"], categories=month_order, ordered=True)
users_by_month_df = users_by_month_df.sort_values("mnth").reset_index(drop=True)

# Correct season order 
season_order = ['Winter', 'Spring', 'Summer', 'Fall']

users_by_season_df["season"] = pd.Categorical(users_by_season_df["season"], categories=season_order, ordered=True)
users_by_season_df = users_by_season_df.sort_values("season").reset_index(drop=True)

# Dashboard Title
st.header("Dicoding Project: Bike Sharing System")

st.subheader("Total User Rentals")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Casual Users", value=format_number(filtered_df.casual.sum()))
with col2:
    st.metric("Registered Users", value=format_number(filtered_df.registered.sum()))
with col3:
    st.metric("Total Users", value=format_number((filtered_df.casual + filtered_df.registered).sum()))

# Users Distribution Charts
st.subheader("Users Distribution Overview")

col1, col2 = st.columns(2)

# Pie Chart: Users by Type
with col1:
    st.subheader("Users by Type")
    total_casual = filtered_df['casual'].sum()
    total_registered = filtered_df['registered'].sum()

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie([total_casual, total_registered], labels=['Casual Users', 'Registered Users'], 
           autopct='%1.1f%%', colors=['#0D9488', '#FB923C'], startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

# Bar Chart: Users by Year
with col2:
    st.subheader("Users by Year")
    fig, ax = plt.subplots(figsize=(6, 6))
    users_by_year_df.set_index('yr').plot(kind='bar', ax=ax, color=['#0D9488', '#FB923C'])
    ax.set_xticklabels(['2011', '2012'], rotation=0)
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Users")
    ax.yaxis.set_major_formatter(FuncFormatter(format_large_number))
    ax.legend(["Casual Users", "Registered Users"])
    st.pyplot(fig)

# Additional User Count Charts
st.subheader("User Count Distribution")

# Row 1: Users by Season
st.subheader("Users by Season")
fig, ax = plt.subplots(figsize=(8, 5))
users_by_season_df.set_index('season').plot(kind='bar', ax=ax, color=['#0D9488'])
ax.set_xlabel("Season")
ax.set_xticklabels(users_by_season_df['season'], rotation=0, ha='center')
ax.set_ylabel("Total Users")
ax.yaxis.set_major_formatter(FuncFormatter(format_large_number))
st.pyplot(fig)

# Row 2: Users by Month
st.subheader("Users by Month")
fig, ax = plt.subplots(figsize=(10, 5))
users_by_month_df.set_index('mnth').plot(kind='bar', ax=ax, color=['#FB923C'])
ax.set_xlabel("Month")
ax.set_xticklabels(users_by_month_df['mnth'], rotation=45, ha='right')
ax.set_ylabel("Total Users")
ax.yaxis.set_major_formatter(FuncFormatter(format_large_number))
st.pyplot(fig)

# User Trends Over Time
st.subheader("User Growth Over Time")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(yearly_trend_df['month_year'], yearly_trend_df['casual'], label='Casual Users', color='#0D9488', marker='o')
ax.plot(yearly_trend_df['month_year'], yearly_trend_df['registered'], label='Registered Users', color='#FB923C', marker='o')
ax.set_xticks(range(len(yearly_trend_df['month_year'])))
ax.set_xticklabels(yearly_trend_df['month_year'], rotation=45, ha='right')
ax.yaxis.set_major_formatter(FuncFormatter(format_large_number))
ax.legend()
st.pyplot(fig)

# Peak Hours
st.subheader("Peak Hours for Bike Rentals")

hourly_users_above_q3 = users_by_hour_df.loc[users_by_hour_df['cnt'] > users_by_hour_df['cnt'].quantile(0.75), 'hr'].tolist()

fig, ax = plt.subplots(figsize=(16, 6))
sns.lineplot(x="hr", y="cnt", data=users_by_hour_df, marker='o', label='Total Rides', ax=ax)

# Add vertical lines and red dots
for i, x in enumerate(hourly_users_above_q3):
    cnt_x = users_by_hour_df.loc[users_by_hour_df["hr"] == x, "cnt"].values[0]
    ax.axvline(x, linestyle='--', color='gray', alpha=0.7)  
    ax.scatter(x, cnt_x, color='red', s=100, zorder=5, label='Peak Hour' if i == 0 else "")
    ax.fill_between([x - 1, x, x + 1], 
                    [users_by_hour_df.loc[users_by_hour_df["hr"] == x-1, "cnt"].values[0] if x-1 in users_by_hour_df["hr"].values else 0, 
                     cnt_x, 
                     users_by_hour_df.loc[users_by_hour_df["hr"] == x+1, "cnt"].values[0] if x+1 in users_by_hour_df["hr"].values else 0], 
                    alpha=0.2, color="red", label='Peak Hour Range' if i == 0 else "")

ax.set_xticks(range(24))
ax.set_xlabel("Hour of the Day")
ax.set_ylabel("Total Rides")
ax.set_title("Hourly Bike Share User Count by Hour")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
st.pyplot(fig)

# Footer
st.caption("Project created by: Destio Hardiansyah")