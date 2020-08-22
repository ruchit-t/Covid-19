@st.cache(ttl = 60*5)
def country_data():
    live_data = rq.get("https://api.covid19api.com/summary").json()
    entire_data = pd.DataFrame(live_data['Countries'], columns = ['Country','TotalConfirmed','TotalDeaths','TotalRecovered','Date'] )
    entire_data['Date'] = pd.to_datetime(entire_data['Date'])
    return entire_data

@st.cache(ttl = 60*5)
def global_data():
    live_data = rq.get("https://api.covid19api.com/summary").json()
    global_data = pd.DataFrame(live_data['Global'], columns = ["NewConfirmed","TotalConfirmed","NewDeaths","TotalDeaths","NewRecovered","TotalRecovered"])
    return global_data




                # st.bar_chart(total_result[['Confirmed', 'Recovered', 'Deceased']].transpose())
                # fig = px.bar(total_result.transpose(), x = 'Cases', y = total_result.transpose().index , color = 'Cases',
                # orientation= 'h', hover_data= ['Cases'], title= 'Total Covid-19 Cases')
                # st.write(fig)

''' Code for represting map'''
# map_data = pd.DataFrame(
# np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
# columns=['lat', 'lon'])
# st.map(map_data)

# st.pydeck_chart(pdk.Deck(
#      map_style='mapbox://styles/mapbox/light-v9',
#      initial_view_state=pdk.ViewState(
#          latitude=37.76,
#          longitude=-122.4,
#          zoom=11,
#          pitch=50,
#      ),
#      layers=[
#          pdk.Layer(
#             'HexagonLayer',
#             data=dfmap,
#             get_position='[lon, lat]',
#             radius=200,
#             elevation_scale=4,
#             elevation_range=[0, 1000],
#             pickable=True,
#             extruded=True,
#          ),
#          pdk.Layer(
#              'ScatterplotLayer',
#              data=dfmap,
#              get_position='[lon, lat]',
#              get_color='[200, 30, 0, 160]',
#              get_radius=200,
#          ),
#      ],
#  ))

# st.text("Data Loaded Successfully")




#code for progress bar and animations


# progress_bar = st.progress(0)
# status_text = st.empty()
# chart = st.line_chart(np.random.randn(10, 2))

# for i in range(100):
#     # Update progress bar.
#     progress_bar.progress(i + 1)

#     new_rows = np.random.randn(10, 2)

#     # Update status text.
#     status_text.text(
#         'The latest random number is: %s' % new_rows[-1, 1])

#     # Append data to the chart.
#     chart.add_rows(new_rows)

#     # Pretend we're doing some computation that takes time.
#     time.sleep(0.1)

# status_text.text('Done!')
# st.balloons()

# st.markdown("<style>global {color: Black;}</style>",unsafe_allow_html = True)
# st.markdown("<global><b>Global Covid-19 Data as on</b> </global>" + covid_country_data.Date[0].strftime('%d-%m-%Y'), unsafe_allow_html = True)



#     st.deck_gl_chart(
#             viewport={
#                 'latitude': midpoint[0],
#                 'longitude':  midpoint[1],
#                 'zoom': 4
#             },
#             layers=[{
#                 'type': 'ScatterplotLayer',
#                 'data': covid_country_data[covid_country_data['Country_Region'] == 'India'],
#                 'radiusScale': 250,
#    'radiusMinPixels': 5,
#                 'getFillColor': [248, 24, 148],
#             }]
#         )