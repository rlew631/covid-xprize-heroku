import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import datetime

from PIL import Image
import pickle


#intro
# st.sidebar.write("This is an application for predicting COVID cases around the country!")
# st.sidebar.button("Predict")

from HTML_snippets import Title_html
st.markdown(Title_html, unsafe_allow_html=True) #Title rendering

st.markdown("The dashboard will visualize the Covid-19 cases worldwide")
st.markdown("Coronavirus disease (COVID-19) is an infectious disease caused by a newly discovered coronavirus. Most people infected with the COVID-19 virus will experience mild to moderate respiratory illness and recover without requiring special treatment. This app gives you the real-time predicted daily new cases of COVID-19")
st.sidebar.title("Visualization Selector")
st.sidebar.markdown("Select the Charts/Plots accordingly:")

# DATA_URL=('E:\Data science Projects\NIELIT project\covid_19_world.csv')
# For different use case where the data does not change often
# @st.cache(persist=True)


def load_data():
    # data=pd.read_csv("./../2020-08-01_2020-08-04_predictions_example.csv")
    data = pd.read_csv("https://github.com/rlew631/covid-xprize-heroku/raw/main/2020-08-01_2020-08-04_predictions_example.csv")
    # data = pd.read_csv("https://github.com/OxCGRT/covid-policy-tracker/blob/master/data/OxCGRT_latest.csv")
    return data

df=load_data()
if st.checkbox('Show dataframe'):
    st.write(df)

# st.sidebar.checkbox("Show Analysis by Country", True, key=1)
select = st.sidebar.selectbox('Select a Country',df['CountryName'].unique())

#get the country selected in the selectbox
country_data = df[df['CountryName'] == select]

if st.sidebar.checkbox("Show Analysis by Country", True, key=2):
    st.markdown("## **Country level analysis**")
    if not st.checkbox('Hide Graph', False, key=1):
        country_total_graph = px.line(
            country_data,
            x='Date',
            y='PredictedDailyNewCases',
            labels={
                'PredictedDailyNewCases':'<b>Number of Cases (per 100k?)</b>',
                'Date':'<b>Date</b>'
            },
            title=f'<b>Overall Predicted Daily New Cases in {select}</b>')
            #color='Date')
        country_total_graph.update_layout(
            xaxis_tickformat="%b %d %Y",
            xaxis_nticks=len(list(country_data['Date'])),
            yaxis_range = [0,max(list(country_data['PredictedDailyNewCases']))]
        )
        country_total_graph.update_yaxes(tick0 = 0)
        st.plotly_chart(country_total_graph)
        #st.write(country_data)

        stringency = st.slider('Select the level of stringency for NPIs', 0, 9)
        # prescribe_df = pd.read_csv('all_2021q1_test_task.csv')
        prescribe_df = pd.read_csv('https://github.com/rlew631/covid-xprize-heroku/raw/main/all_2021q1_test_task.csv')
        prescribe_df = prescribe_df[prescribe_df['CountryName'] == select] #select the country
        prescribe_df = prescribe_df[pd.to_datetime(prescribe_df['Date']) >= datetime.datetime.today()] #select today and future dates
        prescribe_df = prescribe_df[prescribe_df['PrescriptionIndex'] == stringency] #select the relevant prescription index
        st.write(prescribe_df)

        # all_npis = ['C1_School closing', 'C2_Workplace closing', 'C3_Cancel public events', 'C4_Restrictions on gatherings',
        # 'C5_Close public transport', 'C6_Stay at home requirements', 'C7_Restrictions on internal movement',
        # 'C8_International travel controls', 'H1_Public information campaigns', 'H2_Testing policy',
        # 'H3_Contact tracing', 'H6_Facial Coverings', 'Date', 'CountryName', 'RegionName', 'PrescriptionIndex']

        # `npis` is in reverse order of `all_npis` because of the way the matrix ends up when it's transposed

        # npis = ['H6_Facial Coverings', 'H3_Contact tracing', 'H2_Testing policy',
        # 'H1_Public information campaigns', 'C8_International travel controls',
        # 'C7_Restrictions on internal movement', 'C6_Stay at home requirements',
        # 'C5_Close public transport', 'C4_Restrictions on gatherings', 'C3_Cancel public events',
        # 'C2_Workplace closing', 'C1_School closing']

        first_date = datetime.datetime.today() - datetime.timedelta(days=1)
        last_date = pd.to_datetime(prescribe_df['Date'].values[-1])
        dates = [first_date + datetime.timedelta(days=x) for x in range((last_date-first_date).days + 2)] #adding the extra day for setting the color scale to 0-4

        prescribe_df = np.transpose(np.array(prescribe_df.drop(axis=1, columns=['Date', 'CountryName', 'RegionName', 'PrescriptionIndex'])))
        prescribe_df = np.concatenate(
            (np.transpose(np.array([[0,1,2,3,4,4,4,4,4,4,4,4]])), # this is here to make sure that the color scale actually goes from 0 to 4
            prescribe_df), axis=1)

        fig2 = go.Figure(data=go.Heatmap(
                z=prescribe_df,
                x=dates,
                ygap=10,
                colorscale=[#this isn't working properly and scales continuously if not all npi values are present (i.e. 4 is missing)
                        [0,"white"],
                        [0.2,"white"],
                        [0.2,"blue"],
                        [0.4,"blue"],
                        [0.4,'green'],#can also use rgba()
                        [0.6,'green'],
                        [0.6,"yellow"],
                        [0.8,"yellow"],
                        [0.8,"red"],
                        [1,"red"]
                ],
                y=[
                'Mask Mandate',
                'Contact Tracing',
                'Testing Policy',
                'Public Information Campaign',
                'International Travel Restrictions',
                'Local Travel Restrictions',
                'Stay at Home Order',
                'Suspend Public Transportation',
                'Restrict Social Gatherings',
                'Cancel Public Events',
                'Close Workplaces',
                'Close Schools'],
                hovertemplate='%{x}<br>' + '%{y}<br>' + 'Restriction Level: %{z}'#see https://plotly.com/python/hover-text-and-formatting/
        ))
        fig2.update_layout(
            title='Recommended Intervention Plan',
            xaxis_nticks=len(dates)//4, # make it more frequent without flipping it 90 degrees
            xaxis_tickformat='%d \n %B', # For more time formatting types, see: https://github.com/d3/d3-time-format/blob/master/README.md
            # ^^ from https://plotly.com/javascript/tick-formatting/
            hovermode="y",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            width=775,
            xaxis_range = [datetime.datetime.today(),last_date])
        fig2.update_traces(
            showscale=False
        )
        st.plotly_chart(fig2)


# put in a legend with the actual colors somehow. Maybe an SVG?
# make the hover text more useful if possible. get rid of "trace 0"!!!!!
# put in plain english explanations of what the NPIs actually mean and a link to the official explanations.


