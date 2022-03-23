import hashlib
import pandas as pd
import smtplib as s
# Data Viz Pkgs
import plotly.express as px
import streamlit as st
from xt_employee_db import *


def make_hashed(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


st.title('Employee table App')
st.markdown("""
You can create and edit your employee table, and **send email** to employee in this app!""")


@st.cache
def user_table_init():
    create_user_table()


user_table_init()
username = st.sidebar.text_input("User Name")
password = st.sidebar.text_input("Password", type='password')
# login_key = st.button("Login/Signup")

if all([password, username]):
    hashed_pwd = make_hashed(password)
    result = verify_pwd(username, hashed_pwd)
    if result:
        login_successfully = True
        employee_table_name = f'employee_table_{username}'
        st.sidebar.success(f"Logged in as {username}.")
    elif result is None:
        employee_table_name = add_userdata(username, hashed_pwd)
        login_successfully = True
        st.sidebar.success(f'Successfully registered {username}!')
    else:
        login_successfully = False
        st.sidebar.warning("Incorrect Username/Password !")
else:
    login_successfully = False
    st.sidebar.warning("The user name/password is empty. Please enter the password!")


def view_all_employee(table_name):
    data = view_all_data(table_name)
    data = pd.DataFrame(data, columns=['Employee_Name', 'Position', 'Email_Address', 'Entry_date'])
    st.dataframe(data)
    return data


if login_successfully and employee_table_name.startswith('employee_table'):
    menu = ["Add Employee Info", "Update Info", "Delete Info", "Send Email"]
    choice = st.sidebar.selectbox("Selected Activity", menu)
    position_level = ["Senior", "Middle", "Junior"]

    if choice == "Add Employee Info":
        st.subheader("Add Employee Info")
        col1, col2 = st.columns(2)

        with col1:
            Name = st.text_input("Name")
            Email = st.text_input('Email Address')

        with col2:
            Position = st.selectbox("Position Level", position_level)
            Entry_date = st.date_input("Date of Entry")

        if st.button("Add Employee"):
            add_employee(employee_table_name, Name, Position, Email, Entry_date)
            st.success("Added ::{} ::To List".format(Name))

        with st.expander("View Employee Table"):
            result = view_all_employee(employee_table_name)

        with st.expander("Position Chart"):
            position_df = result['Position'].value_counts()  # .to_frame()
            #                 st.dataframe(position_df)

            p1 = px.pie(position_df)  # , names='index',values='Position')
            st.plotly_chart(p1, use_container_width=True)

    if choice == "Update Info":
        st.subheader("Edit Info")

        with st.expander("Current Data"):
            result = view_all_employee(employee_table_name)

        list_of_employee = result['Employee_Name'].unique().tolist()
        selected_name = st.selectbox("Select Employee", list_of_employee)
        position = result.loc[result['Employee_Name'] == selected_name, 'Position'].tolist()
        entry_date = result.loc[result['Employee_Name'] == selected_name, 'Entry_date'].values[0]

        col1, col2 = st.columns(2)

        with col1:
            new_name = st.text_input("Edit Name")
            new_email = st.text_input('Edit Email')

        with col2:
            reset_position_level = position + [i for i in position_level if i not in position]
            new_position_status = st.selectbox("Position Level", reset_position_level)
            new_entry_date = st.date_input(entry_date)

        if st.button("Update Employee Info"):
            edit_info_data(employee_table_name, selected_name, new_name, new_position_status, new_email, new_entry_date)
            st.success("Updated ::{}'s info".format(Name))

        with st.expander("View Updated Data"):
            result = view_all_employee(employee_table_name)

    if choice == "Delete Info":
        st.subheader("Delete")
        with st.expander("View Data"):
            result = view_all_employee(employee_table_name)

        list_of_employee = result['Employee_Name'].unique().tolist()
        delete_employee_name = st.selectbox("Select Employee", list_of_employee, key="<uniquevalueofsomesort>")

        if st.button("Delete"):
            delete_data(employee_table_name, delete_employee_name)
            st.warning("Deleted: '{}'".format(delete_employee_name))

        with st.expander("Updated Data"):
            result = view_all_employee(employee_table_name)

    if choice == "Send Email":
        st.subheader('Send eamil to selected employee')
        email_sender = st.text_input(
            'Enter User Gmail: (Please turn on the less secure app access in your google account setting)')
        password = st.text_input('Enter User Password : ', type='password')
        group = ['Send to Employee', 'Send by Job Title']
        group_reviever = st.selectbox('Where to send :', group)

        if group_reviever == 'Send to Employee':
            list_of_employee = [i[0] for i in view_all_employee_info(employee_table_name)]
            selected_name = st.selectbox("Select Employee", list_of_employee, key="<uniquevalueofsomesort>")
            email_result = get_email(employee_table_name, selected_name)

            if email_result:
                st.write(selected_name, email_result[0][0])

        elif group_reviever == 'Send by Job Title':
            title_send = st.selectbox("Selected Job Title", position_level)
            email_reciever_list = [i[0] for i in view_position(employee_table_name, title_send)]
            st.write(email_reciever_list)

            subject = st.text_input('Your Email Subject :')
            body = st.text_area('Your Email')

        if st.button('Send Email'):
            if not email_sender:
                st.error('Please Fill User Email Field')

            if not password:
                st.error('Please Fill User Password Filed')

            if not email_reciever_list:
                st.error('Please Fill Reciecer Email Filed')

            try:
                connection = s.SMTP('smtp.gmail.com', 587)
                connection.starttls()
                connection.login(email_sender, password)
                message = 'Subject:{}\n\n{}'.format(subject, body)
                connection.sendmail(email_sender, email_reciever_list, message)
                st.success('Email Send Successfully.')

            except Exception as e:
                st.error(
                    'Please check your email and password, or turn on the less secure app access in your google account setting')

            finally:
                connection.quit()
