import pandas as pd
import os
import json 
import requests as rq
import streamlit as st
import pydeck as pdk
import time
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import datetime, timedelta

@st.cache(ttl = 3600, max_entries = 20)
def load_data():
    data = pd.read_csv("https://raw.githubusercontent.com/microsoft/Bing-COVID-19-Data/master/data/Bing-COVID19-Data.csv")
    data.rename(columns = {'Country_Region': 'Country','AdminRegion1': 'State', 'AdminRegion2':'City'}, inplace = True)
    return (data)
 

@st.cache(ttl = 3600, max_entries = 20)
def country_data(entire_data, country):
    country_data = entire_data[entire_data['Country'] == country]
    return country_data

@st.cache(ttl = 3600, max_entries = 20)
def country_data_date(entire_data, country, din):
    country_data = entire_data.loc[(entire_data['Country'] == country) & (entire_data['Updated'] == din)]
    return country_data

def show_map_worldwide(entire_data, din = None):
    if din == None:
        din = entire_data['Updated'].max()
        wd = entire_data[entire_data['Updated'] == din]
    else:
        wd = entire_data[entire_data['Updated'] == din]
    
    px.set_mapbox_access_token('pk.eyJ1IjoicnVjaGl0LXQiLCJhIjoiY2tkNmJ0bHR0MXFycjJ1bnR1YmI5ZDdiYSJ9.8oVDNbDpVDz2P8ZCdHnvlg')
    fig = px.scatter_mapbox(wd, lat="Latitude", lon="Longitude", size="Confirmed", hover_name = np.where(wd["City"].isnull(),wd["Country"] + "- Unknown State",wd["City"]), hover_data =['Deaths', 'Recovered','Confirmed']
                   ,color_discrete_sequence=["Red"], size_max=50, zoom=1)
    fig.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
      ])
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.write(fig)


@st.cache(ttl = 60*5, max_entries = 20)
def live_india_states():
    iapi = pd.read_csv("https://api.covid19india.org/csv/latest/states.csv")
    return iapi

@st.cache(ttl = 60*5, max_entries = 20)
def live_india_disticts():
    iapi = pd.read_csv("https://api.covid19india.org/csv/latest/districts.csv")
    return iapi

def plot_bargraph(data):
    fig = px.bar(data.transpose(), x = 'Cases', y = data.transpose().index , color = 'Cases',
    orientation= 'h', hover_data= ['Cases'], title= 'Total Covid-19 Cases')
    st.write(fig)

def plot_multiple_scatter(data1, data2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x= data1.columns, y= data1.loc['Cases'], name = 'Overall Stats',
                         line=dict(color='royalblue', width=4)))
    fig.add_trace(go.Scatter(x= data2.columns, y= data2.loc['Cases'], name = 'Daily Stats',
                         line=dict(color='indianred', width=4)))
    fig.update_layout(title='Covid-19 Cases',
                   xaxis_title='Status',
                   yaxis_title='Cases')
    
    st.write(fig)

def stack_bar(data1, data2):
    fig = go.Figure()
    fig.add_trace(go.Bar(
    x=data1.columns,
    y=data1.loc['Cases'],
    name='Overall Status',
    marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
    x=data2.columns,
    y=data2.loc['Cases'],
    name='Daily Status',
    marker_color='lightsalmon'
    ))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    st.write(fig)





entire_data = load_data()

st.markdown("<style>description {color: Green;}</style>",unsafe_allow_html = True)
st.title("Covid-19 🌎 Tracker With Visual Analysis!")
st.markdown("### *After the outbreak in late December 2019, Covid-19 also known as SARS-CoVid-19 or simply Corona Virus"
+ " has affected the world in the most unimaginable way. The objective of this website is to provide and analyze the data with visual representation."
+ " Worlwide Data gets updated everyday at 11 AM IST.*", unsafe_allow_html = True)
st.markdown("<b>Note</b>: Data is collected from multiple sources that update at different times and may not always align. Some regions may not provide complete breakdown of COVID-19 related stats.", unsafe_allow_html = True)
st.markdown("For better experience on mobile, please use desktop site.",unsafe_allow_html = True)

st.markdown("---")

st.sidebar.title("Tune the following parameters to analyze the Covid-19 situation!")

live_data_chxbox = st.sidebar.checkbox("Show Live Data", True, key = 1)

st.sidebar.markdown("This option is currently available for only few countries")

if live_data_chxbox is True:
    live_country = st.sidebar.selectbox("Select a Country: ", ['Worldwide', 'India', 'United States of America'])
    if live_country == 'India':
        india_states = live_india_states()  
        nation_wise = st.sidebar.checkbox("Show Nation wide Analysis", True)
        st.sidebar.markdown("Set the states & other parameters below to get customized results")
        if nation_wise is True:
            st.markdown("## **Nation Wise Analysis**")
            st.markdown("### Overall Live Cases in India yet")
            st.markdown("The tables give you the break up of all cases in India yet including Total Recovered, Deaths, Confirmed & Tested")
            total_result = (india_states[['Confirmed', 'Recovered', 'Deceased']].loc[(india_states['Date'] == india_states['Date'].max()) & (india_states['State'] == 'India') ])
            total_result.columns.name = 'Status'
            as_list = total_result.index.to_list()
            as_list[0] = 'Cases'
            total_result.index = as_list
            st.write(total_result)
            # total_graph = st.checkbox("Show Graph", False)
            # if total_graph is True:
                # plot_multiple_scatter(total_result)

            # st.sidebar.markdown("---")

            st.markdown("### Today's Live Confirmed, Recovered & Deceased Cases in India")
            st.markdown("The tables give you the break up of all cases Today in India including Total Recovered, Deaths, Confirmed & Tested")
            yest = pd.to_datetime(india_states['Date'].max())
            t =datetime.strftime(yest - timedelta(1), '%Y-%m-%d')
            yesterday_data = (india_states[['Confirmed', 'Recovered', 'Deceased']].loc[(india_states['Date'] == t) & (india_states['State'] == 'India') ])
            today_stats = total_result - yesterday_data.values
            today_stats.columns.name = 'Status'
            as_list = today_stats.index.to_list()
            as_list[0] = 'Cases'
            today_stats.index = as_list
            st.write(today_stats)
            daily_graph = st.checkbox("Show Graph", False, key = 4)
            if daily_graph is True:
                # plot_bargraph(today_stats)
                overall_viz = st.selectbox("Choose a type of visualization: ", ['Bar Chart', 'Line Chart'])
                if overall_viz == 'Bar Chart':
                    stack_bar(total_result, today_stats)
                else:
                    plot_multiple_scatter(total_result, today_stats)

            # st.sidebar.markdown("---")

            st.markdown("### Covid 19 Live State wise breakup")
            st.markdown("The following table gives you a real-time analysis of the confirmed, recovered and deceased cases of each Indian state")
            india_state_data = india_states.loc[(india_states['Date'] == india_states['Date'].max())]
            BlankIndex = ['']*len(india_state_data)
            india_state_data.index = BlankIndex
            st.write(india_state_data[['State','Confirmed','Recovered','Deceased','Tested']])
            st.markdown("---")
            st.sidebar.markdown("---")

        statewise = st.sidebar.checkbox("Show State Wise Analysis", False)
        if statewise is True:
            state = st.sidebar.selectbox("Select a State or Union Teritory:", india_states.State.unique()[india_states.State.unique() != 'India'])
            st.markdown("## **State Wise Analysis**")
            st.markdown("### Overall Confirmed, Recovered and Deceased Live Cases in "+state+" yet")
            st.markdown("This table gives the total Confirmed, Deceased & Recovered cases in "+state+". Please hit on the below checkbox to see the graphical representation of the same.")
            state_total = india_states[['Confirmed', 'Recovered', 'Deceased']].loc[(india_states.State == state) & (india_states.Date == india_states.Date.max())]
            state_total.columns.name = 'Status'
            as_list = state_total.index.to_list()
            as_list[0] = 'Cases'
            state_total.index = as_list
            st.write(state_total)
            total_graph = st.checkbox("Show Graph", False)
            if total_graph is True:
                plot_bargraph(state_total)



        # st.sidebar.markdown("---")

else:
    choice_country = st.sidebar.checkbox("Show Country Wise Ananlysis", True)

    st.sidebar.markdown("Set the state, city & other parameters to get the desired analysis.")

    if (choice_country is True):
        country = st.sidebar.selectbox("Select a Country:", entire_data.Country.unique()[1:])
        covid_country_data = country_data(entire_data, country)
        st.markdown("# **National Level Analysis**")
        st.markdown("## Overall Confirmed, Active, Recovered and Deceased cases in "+ country +" yet")
        st.markdown("### *This table gives you the data break-up of all confirmed, recovered, active and deceased cases that has been reported in "+ country+ " till now. The graphical representation of this tabular data insight is given right below, don’t forget to check it out.*")
        t = covid_country_data[['Confirmed', 'Deaths', 'Recovered']].loc[(covid_country_data['Updated'] == covid_country_data['Updated'].max()) & (covid_country_data['State'].isnull()) & (covid_country_data['City'].isnull())]
        st.write(t)
    # , t.rename(index = {t.index: 'Cases'})

# elif (choice_result == 'Worldwide'):
#     # covid_world_data = country_data(entire_data, 'Worldwide')
#     show_map_worldwide(entire_data)
#     overall = st.sidebar.checkbox("Show Overall Analysis", True, key = 1)
#     if overall is True:



    


    
    














































