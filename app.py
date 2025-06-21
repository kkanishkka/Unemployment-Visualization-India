import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
import datetime as dt
import plotly.express as px
from streamlit_option_menu import option_menu

# Set up page configuration
st.set_page_config(page_title="Time-wise Unemployment Analysis", page_icon="📊", layout="wide")

# Load external CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")

# Add the header
st.markdown('<div class="header-title">🔍 Time-wise Unemployment Analysis in India 📊</div>', unsafe_allow_html=True)
st.markdown('<p class="subheader">*Collaboratively made with 💡 by Kanishka, Kashish*</p>', unsafe_allow_html=True)

# Load data
df = pd.read_csv('data.csv')

# Data cleaning and transformation
df.columns = ['States', 'Date', 'Frequency', 'Estimated Unemployment Rate', 
              'Estimated Employed', 'Estimated Labour Participation Rate', 
              'Region', 'longitude', 'latitude']
df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
df['Frequency'] = df['Frequency'].astype('category')
df['Month'] = df['Date'].dt.month
df['MonthNumber'] = df['Month'].apply(lambda x: int(x))
df['MonthName'] = df['MonthNumber'].apply(lambda x: calendar.month_abbr[x])
df['Region'] = df['Region'].astype('category')
df.drop(columns='Month', inplace=True)

# Navigation menu
selected = option_menu(
    menu_title=None,
    options=["Overview", "EDA", "Lockdown Impact"],
    icons=["house", "bar-chart", "alert-circle"],
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#F8F9F9"},
        "icon": {"color": "#2874A6", "font-size": "18px"},
        "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px", "--hover-color": "#EAECEE"},
        "nav-link-selected": {"background-color": "#2874A6", "color": "white"},
    },
)

# Display based on selection
if selected == "Overview":
    st.subheader("📊 Overview: Key Statistics")
    st.write(df.describe())
    region_stats = df.groupby(['Region'])[['Estimated Unemployment Rate', 
                                           'Estimated Employed', 
                                           'Estimated Labour Participation Rate']].mean().reset_index()
    st.write(region_stats)

    #heatmap
    df47 = df[(df['MonthNumber'] >= 4) & (df['MonthNumber'] <= 7)]
    df14 = df[(df['MonthNumber'] >= 1) & (df['MonthNumber'] <= 4)]
    df47g = df47.groupby('States')['Estimated Unemployment Rate'].mean().reset_index()
    df14g = df14.groupby('States')['Estimated Unemployment Rate'].mean().reset_index()
    

    heatMap = df[['Estimated Unemployment Rate', 'Estimated Employed', 'Estimated Labour Participation Rate', 'longitude', 'latitude', 'MonthNumber']].corr()

    plt.figure(figsize=(12,6))
    sns.heatmap(heatMap, annot=True, cmap='coolwarm', fmt='.2f', linewidths=1)
    plt.title('🔗 Correlation Heatmap')
    st.subheader("Correlation Heatmap")
    st.pyplot(plt)


elif selected == "EDA":
    st.subheader("🔍 Exploratory Data Analysis")
    # Box plot
    fig = px.box(df, x='States', y='Estimated Unemployment Rate', color='States', title='State-wise Unemployment Rate')
    st.plotly_chart(fig)

    # Scatter matrix
    fig = px.scatter_matrix(df, dimensions=['Estimated Unemployment Rate', 'Estimated Employed', 
                                             'Estimated Labour Participation Rate'], color='Region')
    st.plotly_chart(fig)

    

elif selected == "Lockdown Impact":
    st.subheader("🚨 Impact of Lockdown on Employment")
    

        # Geospatial map
    fig = px.scatter_geo(df, 'longitude', 'latitude', color="Region", hover_name="States", size="Estimated Unemployment Rate", animation_frame="MonthName", scope='asia', title='Lockdown Impact Across India', template='plotly_dark')
    st.subheader("🌍 Geospatial Plot: Lockdown Impact in India")
    st.plotly_chart(fig)

    # Ensure the dataframe `df47g` has all required columns
    df47 = df[(df['MonthNumber'] >= 4) & (df['MonthNumber'] <= 7)]
    df14 = df[(df['MonthNumber'] >= 1) & (df['MonthNumber'] <= 4)]

    df47g = df47.copy()  # Ensure a clean copy of the data

    # Pre-lockdown and post-lockdown mean unemployment rates by state
    df47g = df47.groupby('States')['Estimated Unemployment Rate'].mean().reset_index()
    df14g = df14.groupby('States')['Estimated Unemployment Rate'].mean().reset_index()

    # Ensure column alignment
    df47g.rename(columns={'Estimated Unemployment Rate': 'Unemployment Rate After Lockdown'}, inplace=True)
    df14g.rename(columns={'Estimated Unemployment Rate': 'Unemployment Rate Before Lockdown'}, inplace=True)

    # Merge pre-lockdown and post-lockdown data
    df47g = pd.merge(df47g, df14g, on='States', how='left')

    # Calculate % Change in Unemployment
    df47g['% Change in Unemployment'] = round(
        (df47g['Unemployment Rate After Lockdown'] - df47g['Unemployment Rate Before Lockdown'])
        / df47g['Unemployment Rate Before Lockdown'] * 100, 2
    )

    # Sort by % Change in Unemployment
    df47g = df47g.sort_values('% Change in Unemployment')

    # Add Impact Status column with sorting logic
    def sort_impact(x):
        if x <= 10:
            return '🥲'
        elif x <= 20:
            return '🥲😥'
        elif x <= 30:
            return '🥲😥😖'
        elif x <= 40:
            return '🥲😥😖🤯'
        return '🚨 Severe Impact'

    df47g['Impact Status'] = df47g['% Change in Unemployment'].apply(sort_impact)

    # Display dataframe in Streamlit
    st.subheader("📊 Data Before & After Lockdown")
    st.write(df47g.head())

    # Bar graph classifying lockdown impact
    fig = px.bar(df47g, y='States', x='% Change in Unemployment', color='Impact Status',
                title='State-wise Impact of Lockdown on Employment', template='plotly_dark')
    st.subheader("📊 Bar Graph: Classifying Lockdown Impact by State")
    st.plotly_chart(fig)



