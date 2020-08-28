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
from plotly.subplots import make_subplots

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
    
@st.cache(ttl = 60*5, max_entries = 20)
def state_timeline_data():
    iapi = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise_daily.csv")
    return iapi

@st.cache(ttl = 60*5, max_entries = 20)
def india_timeline_data():
    iapi = pd.read_csv("https://api.covid19india.org/csv/latest/case_time_series.csv")
    return iapi

def plot_bargraph(data):
    fig = px.bar(data.transpose(), x = 'Cases', y = data.transpose().index , color = 'Cases',
    orientation= 'h', hover_data= ['Cases'], title= 'Total Covid-19 Cases')
    st.write(fig)

def plot_multiple_scatter(data1, data2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x= data1.columns, y= data1.loc['Cases'], name = 'Overall Stats',
                        marker=dict(color="crimson", size=25),
                        mode="markers"))
    fig.add_trace(go.Scatter(x= data2.columns, y= data2.loc['Cases'], name = 'Daily Stats',
                        marker=dict(color="royalblue", size=15),
                        mode="markers"))
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


def timeline_state_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data[data.columns[0]], y=data[data.columns[1]], name = 'Confirmed Cases',line=dict(color='royalblue', width=4)))
    fig.add_trace(go.Scatter(x=data[data.columns[0]], y=data[data.columns[2]], name = 'Recovered Cases', line=dict(color='red', width=4)))
    fig.add_trace(go.Scatter(x=data[data.columns[0]], y=data[data.columns[3]], name = 'Deceased Cases',line=dict(color='yellow', width=4)))
    fig.update_layout(title_text="TimeLine of Covid-19 Cases", xaxis_title = 'Date', yaxis_title = 'Cases',autosize=True,
    margin=dict(
        autoexpand=True,
        l=0,
        r=0,
        t=90,
    ), xaxis = dict(showgrid =  False), yaxis = dict(showgrid = False))
    st.write(fig)

def state_daily_timeline(data):
    fig = px.line(data, x = 'Date', y=data[data.columns[2]], color = 'Status', line_group= 'Status', labels={ data.columns[2] : 'Number of Cases'})
    fig.update_layout(title_text="TimeLine of Covid-19 Cases", xaxis_title = 'Date', yaxis_title = 'Cases', xaxis = dict(showgrid =  False), yaxis = dict(showgrid = False))
    st.write(fig)

 
def pie(data):
    fig = px.pie(data[['Recovered','Deceased','Active']], names = data.loc[data.index.max()].index[1:], values=data[['Recovered','Deceased', 'Active']].loc[data.index.max()].values, title= "Pie Chart Break Up of Recovered, Active and Deceased Covid Cases",labels={'label':'Case Status','value':'Number of Cases'})
    fig.update_traces(textinfo='percent+label')
    st.write(fig)
# entire_data = load_data()

state_codes = {
    'Andaman and Nicobar Islands':'AN',
    'Andhra Pradesh	': 'AP',
    'Arunachal Pradesh': 'AR',
    'Assam':'AS',
    'Bihar':'BR',
    'Chandigarh':'CH',
    'Chhattisgarh':'CT',
    'Dadra and Nagar Haveli':'DN',
    'Daman and Diu':'DD',
    'Delhi':'DL',
    'Goa':'GA',
    'Gujarat':'GJ',
    'Haryana':'HR',
    'Himachal Pradesh': 'HP',
    'Jammu and Kashmir':'JK',
    'Jharkhand':'JH',
    'Karnataka':'KA',
    'Kerala': 'KL',
    'Lakshadweep':'LD',
    'Madhya Pradesh':'MP',
    'Maharashtra':'MH',
    'Manipur':'MN',
    'Meghalaya':'ML',
    'Mizoram':'MZ',
    'Nagaland':'NL',
    'Odisha':'OR',
    'Puducherry':'PY',
    'Punjab':'PB',
    'Rajasthan':'RJ',
    'Sikkim':'SK',
    'Tamil Nadu':'TN',
    'Telangana':'TG',
    'Tripura':'TR',
    'Uttar Pradesh':'UP',
    'Uttarakhand': 'UT',
    'West Bengal':'WB'
}

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
            total_result = (india_states.loc[(india_states['Date'] == india_states['Date'].max()) & (india_states['State'] == 'India') ])
            total_result['Active'] = total_result['Confirmed'] - total_result['Recovered'] - total_result['Deceased'] - total_result['Other']
            total_result.columns.name = 'Status'
            as_list = total_result.index.to_list()
            as_list[0] = 'Cases'
            total_result.index = as_list
            st.write(total_result[['Confirmed', 'Recovered', 'Deceased','Tested','Active']])
            st.markdown("### Today's Live Confirmed, Recovered & Deceased Cases in India")
            st.markdown("The tables give you the break up of all cases Today in India including Total Recovered, Deaths, Confirmed & Tested")
            yest = pd.to_datetime(india_states['Date'].max())
            t =datetime.strftime(yest - timedelta(1), '%Y-%m-%d')
            yesterday_data = (india_states.loc[(india_states['Date'] == t) & (india_states['State'] == 'India') ])
            yesterday_data['Active'] = yesterday_data['Confirmed'] - yesterday_data['Recovered'] - yesterday_data['Deceased'] - yesterday_data['Other']
            today_stats = total_result[['Confirmed', 'Recovered', 'Deceased','Tested','Active']] - yesterday_data[['Confirmed', 'Recovered', 'Deceased','Tested', 'Active']].values
            today_stats.columns.name = 'Status'
            as_list = today_stats.index.to_list()
            as_list[0] = 'Cases'
            today_stats.index = as_list
            st.write(today_stats[['Confirmed', 'Recovered', 'Deceased']])
            daily_graph = st.checkbox("Show Graph", False, key = 4)
            if daily_graph is True:
                overall_viz = st.selectbox("Choose a type of visualization: ", ['Bar Chart', 'Line Chart'])
                if overall_viz == 'Bar Chart':
                    stack_bar(total_result[['Confirmed', 'Recovered', 'Deceased']], today_stats[['Confirmed', 'Recovered', 'Deceased']])
                else:
                    plot_multiple_scatter(total_result[['Confirmed', 'Recovered', 'Deceased']], today_stats[['Confirmed', 'Recovered', 'Deceased']])
            # pie(total_result)

            st.markdown("### Covid 19 Live State wise breakup")
            st.markdown("The following table gives you a real-time analysis of the confirmed, recovered and deceased cases of each Indian state")
            india_state_data = india_states.loc[(india_states['Date'] == india_states['Date'].max())]
            BlankIndex = ['']*len(india_state_data)
            india_state_data.index = BlankIndex
            st.write(india_state_data[['State','Confirmed','Recovered','Deceased','Tested']])

            st.markdown("### Mortality Rate, Recovery Rate & Active Cases Rate in India")
            st.markdown("Below Pie Chart gives the comprehensive illustration of India's recovery, active and mortality percentage rate.")
            pie(total_result[['Confirmed', 'Recovered', 'Deceased','Active']])

            st.sidebar.markdown("---")

            st.markdown("### Timeline of Covid-19 in India")
            st.markdown("Below is the time line of overall and daily cases of covid in india since the first case that occurred in Januray. Toggle between Daily and overall timeline to get the graphical representation of the virus spread!")
            timeline_selectbox = st.selectbox("Show Timeline Graph for: ", ['Overall Cases', 'Daily Cases'])
            india_timeline = india_timeline_data()
            if timeline_selectbox is 'Overall Cases':
                timeline_state_chart(india_timeline[['Date','Total Confirmed', 'Total Recovered', 'Total Deceased']])
            else:
                timeline_state_chart(india_timeline[['Date','Daily Confirmed', 'Daily Recovered', 'Daily Deceased']])
            st.markdown("---")
        
        statewise = st.sidebar.checkbox("Show State Wise Analysis", False)
        if statewise is True:
            state = st.sidebar.selectbox("Select a State or Union Teritory:", india_states.State.unique()[india_states.State.unique() != 'India'])
            st.markdown("## **State Wise Analysis**")
            st.markdown("### Overall Confirmed, Recovered and Deceased Live Cases in "+state+" yet")
            st.markdown("This table gives the total Confirmed, Deceased & Recovered cases in "+state+". Please hit on the below checkbox to see the graphical representation of the same.")
            state_total = india_states.loc[(india_states.State == state) & (india_states.Date == india_states.Date.max())]
            # [['Confirmed', 'Recovered', 'Deceased']]
            state_total['Active'] = state_total['Confirmed'] - state_total['Recovered'] - state_total['Deceased'] - state_total['Other']
            state_total.columns.name = 'Status'
            as_list = state_total.index.to_list()
            as_list[0] = 'Cases'
            state_total.index = as_list
            st.write(state_total[['Confirmed', 'Recovered', 'Deceased','Tested','Active']])
            yest = pd.to_datetime(india_states['Date'].max())
            t =datetime.strftime(yest - timedelta(1), '%Y-%m-%d')
            state_yesterday_data = (india_states.loc[(india_states['Date'] == t) & (india_states['State'] == state) ])
            state_yesterday_data['Active'] = state_yesterday_data['Confirmed'] - state_yesterday_data['Recovered'] - state_yesterday_data['Deceased'] - state_yesterday_data['Other']
            today_state_stats = state_total[['Confirmed', 'Recovered', 'Deceased','Tested','Active']] - state_yesterday_data[['Confirmed', 'Recovered', 'Deceased','Tested','Active']].values
            today_state_stats.columns.name = 'Status'
            as_list = today_state_stats.index.to_list()
            as_list[0] = 'Cases'
            today_state_stats.index = as_list
            st.markdown("### Today's Live Confirmed, Recovered & Deceased Cases in "+state)
            st.markdown("The tables give you the break up of all cases Today in "+state+" including Total Recovered, Deaths, Confirmed & Tested. Please click on the checkbox to see the graphical representation of total and daily case breakup in "+state+".")
            st.write(today_state_stats[['Confirmed', 'Recovered', 'Deceased']])
            total_graph = st.checkbox("Show Graph", False, key = 5)
            if total_graph is True:
                state_viz_selection = st.selectbox("Choose a type of visualization: ", ['Bar Chart', 'Line Chart'], key = 6)
                if state_viz_selection == 'Bar Chart':
                   stack_bar(state_total[['Confirmed', 'Recovered', 'Deceased']], today_state_stats[['Confirmed', 'Recovered', 'Deceased']])
                else:
                    plot_multiple_scatter(state_total[['Confirmed', 'Recovered', 'Deceased']], today_state_stats[['Confirmed', 'Recovered', 'Deceased']])

            st.markdown("### Overall Timeline of Covid Cases in "+state+" till date")
            st.markdown("This table gives you an understanding about the data analysis pertaining to the confirmed, recovered and deceased cases of Covid-19 in "+state+" over time.")
            state_timeline = state_timeline_data()
            state_timeline_chxbox = st.selectbox("Show Timeline Graph for: ", ['Overall Cases', 'Daily Cases'], key = 7)
            if state_timeline_chxbox is "Overall Cases":
                timeline_state_chart(india_states[['Date','Confirmed', 'Recovered', 'Deceased']].loc[(india_states['State'] == state)])   
            else:
                state_daily_timeline(state_timeline[['Date','Status',state_codes[state]]])
            
            st.markdown("### Mortality Rate, Recovery Rate & Active Cases Rate in "+state+".")
            st.markdown("Below Pie Chart gives the comprehensive illustration of "+state+"'s recovery, active and mortality percentage rate.")
            pie(state_total[['Confirmed', 'Recovered', 'Deceased','Active']])
        # st.sidebar.markdown("---")


# else:
#     choice_country = st.sidebar.checkbox("Show Country Wise Ananlysis", True)

#     st.sidebar.markdown("Set the state, city & other parameters to get the desired analysis.")

#     if (choice_country is True):
#         country = st.sidebar.selectbox("Select a Country:", entire_data.Country.unique()[1:])
#         covid_country_data = country_data(entire_data, country)
#         st.markdown("# **National Level Analysis**")
#         st.markdown("## Overall Confirmed, Active, Recovered and Deceased cases in "+ country +" yet")
#         st.markdown("### *This table gives you the data break-up of all confirmed, recovered, active and deceased cases that has been reported in "+ country+ " till now. The graphical representation of this tabular data insight is given right below, don’t forget to check it out.*")
#         t = covid_country_data[['Confirmed', 'Deaths', 'Recovered']].loc[(covid_country_data['Updated'] == covid_country_data['Updated'].max()) & (covid_country_data['State'].isnull()) & (covid_country_data['City'].isnull())]
#         st.write(t)
#     # , t.rename(index = {t.index: 'Cases'})

# elif (choice_result == 'Worldwide'):
#     # covid_world_data = country_data(entire_data, 'Worldwide')
#     show_map_worldwide(entire_data)
#     overall = st.sidebar.checkbox("Show Overall Analysis", True, key = 1)
#     if overall is True:



    


    
    














































