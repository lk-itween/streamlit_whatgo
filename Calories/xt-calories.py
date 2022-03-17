import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import qrcode
import time
from PIL import Image
import numpy as np
from base64 import b64encode
from io import BytesIO
import requests
import cv2
from xt_calorisattached import * 
import json

st.set_page_config(layout="wide")
st.title('Calories Playground App')
st.markdown("""
This app shows the main food's caloris and you can create your own low-caloris recipe""")
#---------------------------------#

# web scrabing 
@st.cache
def load_data():
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
}

    url = 'https://us.myprotein.com/thezone/nutrition/food-calories-chart-whats-in-your-fruit-veg-meat-and-other-daily-produce/'
    resp = requests.get(url, headers=headers)
# get online dataframe and rename 

    data_list = map(lambda x: pd.DataFrame(x.values, columns=['Food Items', 'Kcal per 100g']), pd.read_html(resp.text, header=0))

    data = pd.concat(data_list,keys=['Fruits','Vegetables','Grains and Pulses','Meat','Fish','Dairy and Eggs','Carbohydrates','Cooking Oils','Soft Beverages','Alcoholic Beverages'])
    data = data.reset_index(level=[0,1]).drop('level_1',axis=1).rename(columns={'level_0':'Food Category'})
    data = data[['Food Items','Kcal per 100g','Food Category']]
    return data

df = load_data()

#layout
cc1,cc2 = st.columns((2,1))

#show Calories table, food items as index
with cc1:
    cc1.subheader('Calories Chart')
    df1=df.copy()
    food_category_uniqe = df1['Food Category'].unique()
    select_food = st.sidebar.multiselect('Select Food Category',food_category_uniqe,food_category_uniqe)
    df_selected_food= df1[(df1['Food Category'].isin(select_food))]
    df_selected_food1=df_selected_food.set_index('Food Items')
    st.dataframe(df_selected_food1,width=700,height=400)

#download table_csv
    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
        return href

    st.markdown(filedownload(df_selected_food), unsafe_allow_html=True)

#show the mean calories of selectedfood category
with cc2:
    if st.button('Show the mean calories of selected food category'): 
        plt.figure(figsize=(5,10))
        df_plt1= df_selected_food.copy().sort_values(by='Kcal per 100g')
        df_plt1['Kcal per 100g'] = df_plt1['Kcal per 100g'].astype(float)
        df_plt1= df_plt1.groupby('Food Category').mean().reset_index().sort_values(by='Kcal per 100g',ascending=False)
        plt.barh(df_plt1['Food Category'],df_plt1['Kcal per 100g'])
        plt.subplots_adjust(top = 1, bottom = 0)
        plt.xlabel('Food',fontsize=20)
        plt.ylabel('Caloris',labelpad= 30)
        plt.xticks(rotation=45,ha='right',fontsize=20)
        plt.yticks(fontsize=20)
        plt.legend(loc='upper right')
        st.set_option('deprecation.showPyplotGlobalUse', False)

    st.pyplot(plt)

st.write('---')



#sort calories by selected food category
st.subheader('Calories sorted by selected food category')
caloris_plt=['Fruits','Vegetables','Grains and Pulses','Meat','Fish','Dairy and Eggs','Carbohydrates','Cooking Oils','Soft Beverages','Alcoholic Beverages']
st.sidebar.subheader('Selected plot sorted calories by food category')
food_selected = st.sidebar.selectbox('Select Food Caterory',caloris_plt)
plt_data = df1.set_index('Food Category')


def pltdata_func(data,index):
    data = data.copy()
    data = data.loc[index,:].sort_values(by='Kcal per 100g')
    plt.figure(figsize=(10,5))
    plt.plot(data['Food Items'],data['Kcal per 100g'])
    plt.xlabel('Food Items',fontsize=20)
    plt.ylabel('Kcal per 100g',fontsize=20,labelpad= 30)
    plt.xticks(rotation=45,fontsize=16,ha='right')
    plt.yticks(fontsize=16)
    plt.legend(loc='upper right')
    return plt

st.pyplot(pltdata_func(plt_data,food_selected),width=700,height=300)



# QR CODE

qr = qrcode.QRCode(version=1,
                    error_correction = qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=6)


def main():
    st.sidebar.subheader('Create your recipt table and generate QRCode')
    menu= ['Create recipt table and Generate QR Code','DecodeQR']
    choice = st.sidebar.radio('Option',menu)
   

    
    # selected the ingredient from table and create low-calories recipe
    create_table()
    if choice == "Create recipt table and Generate QR Code":
        st.subheader("Add ingredients and crate your low-calories recipt")
        ingredient = st.selectbox('Selected Ingredient',df1['Food Items'].sort_values())
        amount = st.text_input('Amount of Ingredient')
        units = st.selectbox('Choose units',['tbsp','tsp','cup','lb','l','ml','pt','oz','piece'])
        note=st.text_area('Note')
        #add item in the table
        if st.button("Add Ingredient"):
            add_data(ingredient,amount,units,note)
            st.success("Added ::{} ::To List".format(ingredient))

        #view recipt table and delete/edit table
        with st.expander("View and Edit Recipe table"):
            st.subheader('view Recipe table')
            result = view_all_data()
            clean_df = pd.DataFrame(result,columns=['Ingredients',' Amount_of_Ingredients','Units','Note'])
            st.dataframe(clean_df)

            #delete and update recipt table
            st.subheader('Delete and Upadate ingrredient in table')
            ingredients_list =[i[0] for i in view_all_ingredients_data()]
            delete_ingredients=st.selectbox('Select ingredent to delete',ingredients_list)
            if st.button("Delete selected ingredient"):
                delete_data(delete_ingredients)
                st.warning("Deleted: '{}'".format(delete_ingredients))
            if st.button('Update Recipe table'):
                 result = view_all_data()


                        
        #gererate qr code for recipe
        submit_button = st.button('Generate recipe QR Code')    
        if submit_button:
            subc1,subc2= st.columns(2)
            with subc1:
                #add data
                qr.add_data(json.dumps(clean_df.to_dict(orient="records")))
                #FGenerate
                qr.make(fit=True)
                img1 = qr.make_image(fill_color = 'black',back_color='white')
                st.image(img1.get_image())   
            with subc2:
                st.info('Original Text')
                st.write(pd.DataFrame(clean_df))

            #Download QRcode
            def get_image_download_link(img):
                    buffered = BytesIO()
                    img.save(buffered, format="JPEG")
                    img_str = b64encode(buffered.getvalue()).decode()
                    href = f'<a href="data:image/jpeg;base64,{img_str}" download="qrcode_{int(time.time())}.jpeg">Download result</a>'
                    return href
                
            st.markdown(get_image_download_link(img1),unsafe_allow_html=True)

    
    #Decoding QRCode
    elif choice == 'DecodeQR':
        st.subheader('Decode QR')
        image_file =st.file_uploader('Upload QR Code',type=['jpg','png','jpeg'])
        
        if image_file is not None:
            file_bytes = np.asarray(bytearray(image_file.read()),dtype=np.uint8)
            opencv_image = cv2.imdecode(file_bytes,1)
            cl1,cl2=st.columns(2)
            with cl1:
                st.image(image_file)

            with cl2:
                st.info('Decoded QR Code')
                det = cv2.wechat_qrcode_WeChatQRCode()
                retval= det.detectAndDecode(opencv_image)[0][0]
                st.dataframe(pd.DataFrame(json.loads(retval)))
               
               

    else:
        st.subheader('About')

if __name__ == "__main__":
    main()
