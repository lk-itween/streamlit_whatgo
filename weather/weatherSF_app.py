import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from PIL import Image
from wordcloud import WordCloud,STOPWORDS
import os
print(os.getcwd())

#---------------------------------#
# Page layout
## Page expands to full width
st.set_page_config(layout="wide")
#---------------------------------#
# Title

img = Image.open('./weather/data/sf.jpg')

st.image(img, width=700)

st.title('San Francisco 15-Day Weather Forecast App')
st.markdown("""
Get 15-day wether forecast for **days & nigths** in San Francisco
""")
#---------------------------------#
# About
expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit,matplotlib, BeautifulSoup, requests, datetime
* **Data source:** [The Weather Channel](https://weather.com/en-IN/).
* **Credit:** Web scraper adapted from the article *[Scrapping Weather prediction Data using Python and BS4](https://www.geeksforgeeks.org/scrapping-weather-prediction-data-using-python-and-bs4/)*.
""")



col1 = st.sidebar

col2, col3 = st.columns((2,1))



# Web scraping 
@st.cache
def load_data():
    file = requests.get("https://weather.com/en-IN/weather/tenday/l/69bedc6a5b6e977993fb3e5344e3c06d8bc36a1fb6754c3ddfb5310a3c6d6c87")
    soup = BeautifulSoup(file.content, "html.parser")

    all_text = soup.find("section", {"class": "card Card--card--HiWPW DailyForecast--Card--1tOGm"})
    title = all_text.find('h1').text
   

    dayparts = all_text.find_all('div', {'class': 'DailyContent--DailyContent--KcPxD'})
    humiditysections = all_text.find_all('div', {'class': 'DetailsTable--field--3ZKJV'})
    humiditysections = [i for i in humiditysections if i.find('span', {'data-testid': 'HumidityTitle'})]
    select_all = zip(dayparts, humiditysections)

    columns=['date', 'day', 'time', 'weather', 'humidity', 'precip', 'temp', 'wind']
    data = pd.DataFrame(columns=columns)

    for num, (daypart, humiditysection) in enumerate(select_all):
        day, date, _, time = daypart.find('h3').text.split(' ')
        temp = daypart.find('span', {'data-testid': 'TemperatureValue'}).text
        weather = daypart.find('svg').find('title').text
        precip_find = daypart.find('span', {'data-testid': 'PercentageValue'})
        precip = precip_find.text if precip_find else '0%'
        wind = daypart.find('span', {'data-testid': 'Wind'}).text
        humidity = humiditysection.find('span', {'data-testid': 'PercentageValue'}).text
        data = data.append(pd.Series([date, day, time, weather, humidity, precip, temp, wind], name=num, index=columns))
        df= data  
    
    #data clean
    df['temp']= df['temp'].replace(r'[^0-9]','',regex= True).astype('int')
    df ['temp']= ((df['temp'] * 9/5) + 32).astype('int')

    today = datetime.today()
    date_value = pd.date_range(today, today + timedelta(days =14)).date
    date_dict ={f'{i.day:02}':i for i in date_value}
    df['date'] = df['date'].map(date_dict)
    
    return df

df = load_data()



#mutiple slected date
col2.subheader('Selected Date')
date_unique= df['date'].unique()
selected_date = col1.multiselect('Selected Date', date_unique, date_unique)

df_selected_date = df[ (df['date'].isin(selected_date)) ] 

col2.dataframe(df_selected_date)

#download data
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_date), unsafe_allow_html=True)



# Day and night Temperature line chart
col2.subheader('Day & Night Temperature')
df1 = df[['date','time','temp','humidity','precip']].copy()
df1[['humidity','precip']] = df1[['humidity','precip']].replace(r'[^0-9]','',regex=True).astype(int)


def day_night_line(data, date):
    df_selected_date2 = data[data['date'].isin(date)].copy()
    if df_selected_date2.empty:
        return plt.figure(figsize=(10,6))
    df_selected_date2 = df_selected_date2[:].set_index(['date', 'time']).unstack('time')['temp']
    plt.figure(figsize=(10,6))
    plt.subplots_adjust(top = 1, bottom = 0)
    df_selected_date2.plot(kind='line')
    xticks_ = df_selected_date2.index.astype(str)
    plt.xticks(xticks_, rotation=45, ha='right')
    plt.ylabel('Temp(°F)')
    plt.legend(loc='upper right')
    return plt

col2.pyplot(day_night_line(df1, selected_date))
col2.write('---')



#wordcloud for weather condition
col2.subheader('Word Cloud for Weather in 15days')
df4 =df.copy()
df4 = pd.DataFrame(df4['weather'].value_counts().reset_index() )
dict = {} 
for col in df4.values:
    dict[col[0]] = col[1]
wordcloud = WordCloud(background_color = 'White', width=1920,height=1080)
wordcloud.generate_from_frequencies(dict)
plt.figure(figsize=(5,8))
plt.imshow(wordcloud,interpolation='bilinear')
plt.axis('off')
col2.pyplot(plt)

col2.write('---')



#selected condition
col1.subheader('Get table by weather condition in 15days ') 
col2.subheader('Selected Weather Condition')

selected_condition = col1.selectbox('Selected weather condition table',['humidity>80%','Rain','DIF>15','Windy'])   
df_bool_serise = df1['time'] == 'Day'
df1.loc[df_bool_serise,'temp'] = df1.loc[df_bool_serise,'temp']*(-1)
df2 = abs(df1.groupby(['date'],sort=False)['temp'].sum()).reset_index(name = 'DIF')
sunny = df['weather'] == 'Sunny'
windy = df['weather'] == 'Wind'
rain = df['weather'] == 'Rain'


if 'DIF>15' in selected_condition: 
    df2_data = df2.loc[df2.query(selected_condition).index,'date']
    col2.write(df[df['date'].isin(df2_data)])
   
    #df_DIF= df[df['date'].isin(df2_data)

elif 'Sunny' in selected_condition:
    col2.write(df[sunny])
elif 'Windy' in selected_condition :
    col2.write(df[windy])
elif 'Rain' in selected_condition :
    col2.write(df[rain])
else:
    col2.write(df.loc[df1.query(selected_condition[:-1]).index, :])



# DIF visualiztion in col3
col3.subheader('Difference between day and night temperature in 15days')
col3.write('greater than 15°F show in green color')
df3 = df2[df2['date'].isin(df[df.duplicated(subset=['date'])]['date'])].set_index('date')
df3= df3.sort_values(by='DIF')
df3['DIF1'] = df3['DIF']>15

plt.figure(figsize=(4,17))
plt.subplots_adjust(top = 1, bottom = 0)
df3['DIF'].plot(kind='barh',color=df3.DIF1.map({True: 'g', False: 'r'}))
col3.pyplot(plt)
