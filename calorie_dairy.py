import streamlit as st
import calorie_counter_with_classes as ccc
import functions
import os
from datetime import date
import pandas as pd

current_week = None

def create_week_file():
    week_no = st.session_state["week"]
    week_file = 'weekly_tracker' + os.sep + f'week{week_no}_tracker.txt'
    if not os.path.exists(week_file):
        with open(week_file, 'x') as f:
            pass
    
    day = functions.get_dayname()
    f = open(week_file)
    lines = f.readlines()
    for line in lines:
        if day in line:
            return
    line = day + ": \n"
    lines.append(line)
    print(lines)
    with open(week_file,'w+') as f:
        f.writelines(lines)

def add_item_to_dictionary(self,item):
        fname = 'calorie_dict.xlsx'
        df = pd.read_excel(fname,engine = 'openpyxl')  
        print("Completed")      
        st.write("For item"+item)
        st.text_input(label="Enter measure", key='measure')
        measure = st.session_state["measure"]
        if st.session_state['measure']:
            st.text_input(label="Enter calories", key='calories')
            calories = st.session_state["calories"]
        if st.session_state["calories"]:
            st.text_input(label="Enter protein", key='protein')
            protein = st.session_state["protein"]
        if st.session_state["protein"]:
            st.text_input(label="Enter fats", key='fats')
            fats = st.session_state["fats"]
        if st.session_state["fats"]:
            st.text_input(label="Enter carbs", key='carbs')
            carbs = st.session_state["carbs"]

        if item in df['food_item'].values:
            print(f"{item} exists, so updating")
            df = pd.read_excel(fname,engine = 'openpyxl')
            index = df.index[df['food_item']==item]
            df.iloc[index] = [item,measure,calories,protein,fats,carbs]
        else:
            df2 = {'food_item':item,'measure':measure,'calories':calories,"protein":protein,"fats":fats,"carbohydrates":carbs}
            df = pd.read_excel(fname,engine = 'openpyxl')
            df = df.append(df2, ignore_index = True)
        self.update_excel_file(df,fname)

st.title("Calorie Counter")
st.subheader("This is my calorie counter app")
st.write("This app is to help diet and exercise tracking.")

st.text_input(label="Add work week:", placeholder="Add work week no...", 
on_change=create_week_file, key='week')

st.text_input(label="Current weight:", placeholder="Current weight in kgs...", key='weight')

dct = ccc.DailyCalorieTracker(st.session_state['week'],date=date.today(),current_weight=st.session_state["weight"])
st.text_input(label="Enter item or meal:", placeholder="Enter item or meal...", key='snack')
