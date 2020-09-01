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

@st.cache(ttl = 60*1380)
def load_data():
    data = pd.read_csv("https://raw.githubusercontent.com/microsoft/Bing-COVID-19-Data/master/data/Bing-COVID19-Data.csv")
    data.rename(columns = {'Updated':'Date', 'ConfirmedChange':'New Confirmed','Deaths':'Deceased','DeathsChange':'New Deceased','RecoveredChange':'New Recovered','Country_Region':'Country','AdminRegion1':'State','AdminRegion2':'District'}, inplace = True)
    return (data)
 
@st.cache(ttl = 3600, max_entries = 100,allow_output_mutation=True)
def worldwide_live_data():
     w_d = rq.get("https://api.covid19api.com/summary").json()
     data = pd.DataFrame(w_d['Global'], index = [0])
     data.rename(columns={'NewConfirmed':'New Confirmed','TotalConfirmed':'Confirmed','NewDeaths':'New Deceased','TotalDeaths':'Deceased','NewRecovered':'New Recovered','TotalRecovered':'Recovered'},inplace=True)
     return data

@st.cache(ttl = 3600, max_entries = 100)
def countries_live_data():
     w_d = rq.get("https://api.covid19api.com/summary").json()
     data = pd.DataFrame(w_d['Countries'])
     data.rename(columns={'NewConfirmed':'New Confirmed','TotalConfirmed':'Confirmed','NewDeaths':'New Deceased','TotalDeaths':'Deceased','NewRecovered':'New Recovered','TotalRecovered':'Recovered'},inplace=True)
     return data

@st.cache(ttl = 3600, max_entries = 100)
def country_data(entire_data, country):
    country_data = entire_data[entire_data['Country'] == country]
    return country_data

@st.cache(ttl = 3600, max_entries = 100)
def country_data_date(entire_data, country, din):
    country_data = entire_data.loc[(entire_data['Country'] == country) & (entire_data['Updated'] == din)]
    return country_data

# @st.cache(suppress_st_warning=True)
def show_map_worldwide(data, maxday,mapstyle):
    mstyle = "white-b"
    wd = data[data['Date'] == maxday]
    px.set_mapbox_access_token('pk.eyJ1IjoicnVjaGl0LXQiLCJhIjoiY2tkNmJ0bHR0MXFycjJ1bnR1YmI5ZDdiYSJ9.8oVDNbDpVDz2P8ZCdHnvlg')
    fig = px.scatter_mapbox(wd, lat="Latitude", lon="Longitude", size="Confirmed", hover_name = np.where(wd["District"].isnull(),wd["Country"] + "- Unknown State",wd["District"]), hover_data =['Deceased', 'Recovered','Confirmed']
                   ,color_discrete_sequence=["Red"], size_max=50, zoom=1)
    if mstyle == "white-bg":
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
    else:
        fig.update_layout(
            mapbox = {
        'style': mapstyle, 'zoom': 0.7},
        showlegend = True)
    fig.update_layout( title = "Covid-19 Worldwide Effect")
    # fig.update_layout(margin={"r":1.0,"t":0.0,"l":1.0,"b":0.0})
    fig.update_layout(margin=dict(autoexpand = True))
    st.write(fig)
    # fig.show()


@st.cache(ttl = 60*30, max_entries = 100)
def live_india_states():
    iapi = pd.read_csv("https://api.covid19india.org/csv/latest/states.csv")
    return iapi

@st.cache(ttl = 60*30, max_entries = 100)
def live_india_disticts():
    iapi = pd.read_csv("https://api.covid19india.org/csv/latest/districts.csv")
    return iapi
    
@st.cache(ttl = 60*30, max_entries = 100)
def state_timeline_data():
    iapi = pd.read_csv("https://api.covid19india.org/csv/latest/state_wise_daily.csv")
    return iapi

@st.cache(ttl = 60*30, max_entries = 100)
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


def cal_total_daily_data(data):
    data['Active'] = data['Confirmed'] - data['Recovered'] - data['Deceased'] - data['Other']
    data.columns.name = 'Status'
    as_list = data.index.to_list()
    as_list[0] = 'Cases'
    data.index = as_list
    return data

def district_timeline(data, var1 = None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = data[data.columns[0]], y = data[data.columns[1]], mode = 'markers', text = "Confirmed Cases", name = 'Confirmed Cases'))
    fig.add_trace(go.Scatter(x = data[data.columns[0]], y = data[data.columns[2]], mode = 'markers', text = "Recovered Cases", name = 'Recovered Cases'))
    fig.add_trace(go.Scatter(x = data[data.columns[0]], y = data[data.columns[3]], mode = 'markers', text = "Deceased Cases", name = 'Confirmed Cases'))
    fig.update_layout(title_text="District wise Covid-19 Cases in "+var1, xaxis_title = 'Districts', yaxis_title = 'Cases', xaxis = dict(showgrid =  False), yaxis = dict(showgrid = False))
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
    'Dadra and Nagar Haveli and Daman and Diu':'DN',
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

entire_data = load_data()
t2 = pd.to_datetime(entire_data.Date.loc[entire_data['Country'] =='India'].max())
maxday = datetime.strftime(t2-timedelta(1), '%m/%d/%Y')

countries_data  = countries_live_data()

st.markdown("<style>description {color: Green;}</style>",unsafe_allow_html = True)
st.title("Covid-19 🌎 Tracker With Visual Analysis!")
st.markdown("### *After the outbreak in late December 2019, Covid-19 also known as SARS-CoVid-19 or simply Corona Virus"
+ " has affected the world in the most unimaginable way. The objective of this website is to provide and analyze the data with visual representation."
+ " Worlwide Data gets updated everyday at 11 AM IST.*", unsafe_allow_html = True)
st.markdown("<b>Note</b>: Data is collected from multiple sources that update at different times and may not always align. Some regions may not provide complete breakdown of COVID-19 related stats.", unsafe_allow_html = True)
st.markdown("For better experience on mobile, please use desktop site.",unsafe_allow_html = True)

st.markdown("---")

st.sidebar.title("Tune the following parameters to analyze the Covid-19 situation!")
# st.sidebar.markdown("---")
st.sidebar.markdown("<b>Note</b>: Live stats are currently available for India only (Refreshes in every 1 hour).", unsafe_allow_html = True)
st.sidebar.markdown("Click on <b>Worldwide</b> to see stats for all the countries, provinces & cities. (Refreshes at IST 11 AM everyday)", unsafe_allow_html=True)
st.sidebar.markdown("---")
live_data_chxbox = st.sidebar.checkbox("Show Covid-19 Data", True, key = 1)

if live_data_chxbox is True:
    live_country = st.sidebar.selectbox("Select a Country: ", ['Worldwide', 'India (Live Data)', 'Other Countries'])
    if live_country == 'India (Live Data)':
        india_states = live_india_states()  
        nation_wise = st.sidebar.checkbox("Show Nation wide Analysis", True)
        st.sidebar.markdown("Set the states & other parameters below to get customized results")
        if nation_wise is True:
            st.markdown("## **Nation Wise Analysis**")
            st.markdown("### Overall Live Cases in India yet")
            st.markdown("The tables give you the break up of all cases in India yet including Total Recovered, Deaths, Confirmed & Tested")
            total_result = (india_states.loc[(india_states['Date'] == india_states['Date'].max()) & (india_states['State'] == 'India') ])

            total_modified_result = cal_total_daily_data(total_result)
            st.write(total_modified_result[['Confirmed', 'Recovered', 'Deceased','Tested','Active']])
            st.markdown("### Today's Live Confirmed, Recovered & Deceased Cases in India")
            st.markdown("The tables give you the break up of all cases Today in India including Total Recovered, Deaths, Confirmed & Tested")
            yest = pd.to_datetime(india_states['Date'].max())
            t =datetime.strftime(yest - timedelta(1), '%Y-%m-%d')
            yesterday_data = (india_states.loc[(india_states['Date'] == t) & (india_states['State'] == 'India') ])
            yesterday_modified_data = cal_total_daily_data(yesterday_data)
            # yesterday_data['Active'] = yesterday_data['Confirmed'] - yesterday_data['Recovered'] - yesterday_data['Deceased'] - yesterday_data['Other']
            today_stats = total_modified_result[['Confirmed', 'Recovered', 'Deceased','Tested','Active']] - yesterday_modified_data[['Confirmed', 'Recovered', 'Deceased','Tested', 'Active']].values
            st.write(today_stats[['Confirmed', 'Recovered', 'Deceased','Active']])
            daily_graph = st.checkbox("Show Graph", False, key = 4)
            if daily_graph is True:
                overall_viz = st.selectbox("Choose a type of visualization: ", ['Bar Chart', 'Line Chart'])
                if overall_viz == 'Bar Chart':
                    stack_bar(total_result[['Confirmed', 'Recovered', 'Deceased']], today_stats[['Confirmed', 'Recovered', 'Deceased']])
                else:
                    plot_multiple_scatter(total_result[['Confirmed', 'Recovered', 'Deceased']], today_stats[['Confirmed', 'Recovered', 'Deceased']])
            

            st.markdown("### Covid 19 Live State wise breakup")
            st.markdown("The following table gives you a real-time analysis of the confirmed, recovered and deceased cases of each Indian state")
            india_state_data = india_states.loc[(india_states['Date'] == india_states['Date'].max())]
            BlankIndex = ['']*len(india_state_data)
            india_state_data.index = BlankIndex
            st.write(india_state_data[['State','Confirmed','Recovered','Deceased','Tested']])

            st.markdown("### Mortality Rate, Recovery Rate & Active Cases Rate in India")
            st.markdown("Below Pie Chart gives the comprehensive illustration of India's recovery, active and mortality percentage rate.")
            pie(total_modified_result[['Confirmed', 'Recovered', 'Deceased','Active']])

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
        
        # st.sidebar.markdown("---")
        st.sidebar.markdown("## **State Level Analysis**")
        statewise = st.sidebar.checkbox("Show State Wise Analysis", False)
        if statewise is True:
            state = st.sidebar.selectbox("Select a State or Union Teritory:", india_states.State.unique()[india_states.State.unique() != 'India'])
            st.markdown("## **State Wise Analysis**")
            st.markdown("### Overall Confirmed, Recovered and Deceased Live Cases in "+state+" yet")
            st.markdown("This table gives the total Confirmed, Deceased & Recovered cases in "+state+". Please hit on the below checkbox to see the graphical representation of the same.")
            state_total = india_states.loc[(india_states.State == state) & (india_states.Date == india_states.Date.max())]
            state_modified_total = cal_total_daily_data(state_total)
            st.write(state_modified_total[['Confirmed', 'Recovered', 'Deceased','Tested','Active']])
            yest = pd.to_datetime(india_states['Date'].max())
            t =datetime.strftime(yest - timedelta(1), '%Y-%m-%d')
            state_yesterday_data = (india_states.loc[(india_states['Date'] == t) & (india_states['State'] == state) ])
            state_yesterday_modified_data = cal_total_daily_data(state_yesterday_data)
            # state_yesterday_data['Active'] = state_yesterday_data['Confirmed'] - state_yesterday_data['Recovered'] - state_yesterday_data['Deceased'] - state_yesterday_data['Other']
            today_state_stats = state_modified_total[['Confirmed', 'Recovered', 'Deceased','Tested','Active']] - state_yesterday_modified_data[['Confirmed', 'Recovered', 'Deceased','Tested','Active']].values

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
            pie(state_modified_total[['Confirmed', 'Recovered', 'Deceased','Active']])
            district_data =  live_india_disticts()
            st.markdown("### Covid-19 cases district wise breakup in "+state)
            st.markdown("The following table gives you a real-time analysis of the confirmed, recovered and deceased cases of "+state)
            district_wise_breakup = district_data.loc[(district_data['Date'] == district_data['Date'].max()) & (district_data['State'] == state)]
            BlankIndex = ['']*len(district_wise_breakup)
            district_wise_breakup.index = BlankIndex
            st.write(district_wise_breakup[['District','Confirmed','Recovered','Deceased','Tested']].fillna("Unknwon"))
            district_timeline(district_wise_breakup[['District','Confirmed','Recovered','Deceased']],state)


            st.sidebar.markdown("---")
            st.markdown("---")
            st.sidebar.markdown("## **District Level Analysis**")
            districtwise = st.sidebar.checkbox("Show District wise analysis", True)
            if districtwise is True:
                district = st.sidebar.selectbox("Select a district of above selected state", district_data.District.loc[district_data['State'] == state].unique(),key = 10)
                st.markdown("## **District Wise Analysis**")
                st.markdown("### Overall Confirmed, Recovered and Deceased Live Cases in "+district+" yet")
                st.markdown("This table gives the total Confirmed, Deceased & Recovered cases in "+district+". Table also gives the active cases and total tested indivisiual count in the district.")
                district_total = district_data.loc[(district_data.District == district) & (district_data.Date == district_data.Date.max())]
                district_modified_total = cal_total_daily_data(district_total)
                st.write(district_modified_total[['Confirmed', 'Recovered', 'Deceased','Tested','Active']].fillna("Unknown"))
                district_yesterday_data = (district_data.loc[(district_data['Date'] == t) & (district_data['District'] == district) ])
                district_yesterday_modified_data = cal_total_daily_data(district_yesterday_data)
                today_district_stats = district_modified_total[['Confirmed', 'Recovered', 'Deceased','Tested','Active']] - district_yesterday_modified_data[['Confirmed', 'Recovered', 'Deceased','Tested','Active']].values
                st.markdown("### Today's Live Confirmed, Recovered & Deceased Cases in "+district)
                st.markdown("The tables give you the break up of all cases Today in "+district+" including Total Recovered, Deaths, Confirmed & Tested. Don't forget to click on the checkbox to see the graphical representation of total and daily case breakup in "+district+".")
                st.write(today_district_stats[['Confirmed', 'Recovered', 'Deceased']])
                total_district_graph = st.checkbox("Show Graph")
                if total_district_graph is True:
                    district_viz_selection = st.selectbox("Choose a type of visualization: ", ['Bar Chart', 'Line Chart'], key = 11)
                    if district_viz_selection == 'Bar Chart':
                        stack_bar(district_modified_total[['Confirmed', 'Recovered', 'Deceased']], today_district_stats[['Confirmed', 'Recovered', 'Deceased']])
                    else:
                        plot_multiple_scatter(district_modified_total[['Confirmed', 'Recovered', 'Deceased']], today_district_stats[['Confirmed', 'Recovered', 'Deceased']])

                st.markdown("### Overall Timeline of Covid Cases in "+district+" till date")
                st.markdown("This visual representation gives you an understanding about the data analysis of the confirmed, recovered and deceased cases of Covid-19 in "+district+" over time.")
                district_timeline_chxbox = st.checkbox("Show Timeline Graph for: ", True, key = 12)
                if district_timeline_chxbox is True:
                    timeline_state_chart(district_data[['Date','Confirmed', 'Recovered', 'Deceased']].loc[(district_data['District'] == district)])   

                st.markdown("### Mortality Rate, Recovery Rate & Active Cases Rate in "+district+".")
                st.markdown("Below Pie Chart gives the comprehensive illustration of "+district+"'s recovery, active and mortality percentage rate.")
                pie(district_modified_total[['Confirmed', 'Recovered', 'Deceased','Active']])

    elif live_country == 'Worldwide':
        st.markdown("## **Worldwide Analysis**")
        st.markdown("### Overall Covid-19 cases around the globe yet.")
        st.markdown("The below table gives the break down of total confirmed, deceased & recovered Covid-19 cases around the globe.")
        world_data = worldwide_live_data()
        # world_data.index.name = 'Cases'
        world_data.columns.name = 'Status'
        as_list = world_data.index.to_list()
        as_list[0] = 'Cases'
        world_data.index = as_list
        st.write(world_data[['Confirmed','Recovered','Deceased']])
        st.markdown("### Today's Covid-19 cases around the globe.")
        st.markdown("The tables give you the break up of all cases Today including Total Recovered, Deaths & Confirmed. Don't forget to click on the checkbox to see the graphical representation of total and daily case breakup.")
        st.write(world_data[['New Confirmed','New Recovered','New Deceased']])
        daily_copy = world_data[['New Confirmed','New Recovered','New Deceased']].copy()
        daily_copy.rename(columns= {'New Confirmed':'Confirmed','New Recovered':'Recovered','New Deceased':'Deceased'},inplace=True)
        # daily_copy.index.name = 'Cases'
        daily_graph = st.checkbox("Show Graph", False, key = 4)
        if daily_graph is True:
            overall_viz = st.selectbox("Choose a type of visualization: ", ['Bar Chart', 'Scatter Chart'])
            if overall_viz == 'Bar Chart':
                stack_bar(world_data[['Confirmed', 'Recovered', 'Deceased']], daily_copy[['Confirmed', 'Recovered', 'Deceased']])
            else:
                plot_multiple_scatter(world_data[['Confirmed', 'Recovered', 'Deceased']], daily_copy[['Confirmed', 'Recovered','Deceased']])


        st.markdown("### Map representation of Covid-19 cases around the globe.")
        st.markdown("Below map gives the overall insight of covid cases in the world. Hover over the cities and provinces to see confirmed, recovered and deceased cases in the particular area. Select a theme from list of options in the sidebar to see the data in your desired way!")
        mapstyle = st.sidebar.radio("Select a theme of map: ",['Outdoors','Dark','Satellite-Streets'])
        show_map_worldwide(entire_data, maxday,mapstyle.lower())
        st.markdown("### Worldwide Fatality Rate, Recovery Rate & Active Cases Percentage.")
        st.markdown("Below Pie Chart gives the comprehensive illustration of World's recovery, active and mortality percentage rate. Click on the right top side to expand the pie chart.")
        world_data['Active'] = world_data['Confirmed'] - world_data['Deceased'] - world_data['Recovered']
        pie(world_data[['Confirmed','Recovered','Deceased','Active']])

        st.write("### Timeline of Covid-19.")
        st.write("This visual representation gives you an understanding about the data analysis of the confirmed, recovered and deceased cases of Covid-19 in across the globe over time. Toggle between daily and overall analysis to see the desired graphical representation.")
        world_timeline_data = entire_data.loc[(entire_data['Country'] == "Worldwide")&(entire_data['State'].isnull())&(entire_data['District'].isnull())&(entire_data['New Recovered']>=0.0)].copy()
        world_timeline_data['Dates'] = pd.to_datetime(world_timeline_data['Date'])
        world_timeline_data['Dates'] = world_timeline_data['Dates'].apply(lambda x:x.strftime("%d-%b-%Y"))
        timeline_selectbox = st.selectbox("Show Timeline Graph for: ", ['Overall Cases', 'Daily Cases'],key =14)
        if timeline_selectbox == "Overall Cases":
            # st.write(timeline_state_chart(entire_data[['Date','Confirmed','Recovered','Deceased']].loc[(entire_data['Country'] == "Worldwide")&(entire_data['State'].isnull())&(entire_data['District'].isnull())]))
            st.write(timeline_state_chart((world_timeline_data[['Dates','Confirmed','Recovered','Deceased']])))
        else:
            # st.write(timeline_state_chart(entire_data[['Date','New Confirmed','New Recovered','New Deceased']].loc[(entire_data['Country'] == "Worldwide")&(entire_data['State'].isnull())&(entire_data['District'].isnull())&(entire_data['New Recovered']>=0.0)]))
            st.write(timeline_state_chart((world_timeline_data[['Dates','New Confirmed','New Recovered','New Deceased']])))


        st.write("### Top 5 Countries with highest number of Covid-19 confirmed cases")
        st.write("The following table represents the top 5 countries with highest number confirmed Covid-19 cases along with recovered and deceased cases.")
        top5 = countries_data.nlargest(5,'Confirmed')
        top5Index = np.arange(1,6)
        top5.index = top5Index
        st.write(top5[['Country','Confirmed','Recovered','Deceased','New Confirmed','New Recovered','New Deceased']])















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



    


    
    














































