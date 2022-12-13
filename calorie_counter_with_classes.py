from calendar import week
import pandas as pd
from openpyxl import load_workbook
import json
import os
import streamlit as st

class DailyCalorieTracker():
    def __init__(self,week_no,date,current_weight):
        self.week_no = week_no
        self.date = date
        self.current_weight = current_weight
        self.mealtime_list = ['breakfast','smoothie','lunch','snack','salad','dinner']
        self.meal_list = [[] for _ in self.mealtime_list]
        self.load_calorie_dict()

    def load_calorie_dict(self):
        cd = pd.read_excel('calorie_dict.xlsx',engine = 'openpyxl')
        self.measures = list(cd['measure'])
        self.food_items = list(cd['food_item'])
        self.calories = list(cd['calories'])
        self.protein = list(cd['protein'])
        self.fats = list(cd['fats'])
        self.carbohydrates = list(cd['carbohydrates'])
    
    def update_excel_file(self,df,fname):
        with pd.ExcelWriter(fname, engine="openpyxl", mode="a") as writer:
            workBook = writer.book
            try:
                workBook.remove(workBook["Sheet1"])
            except:
                print("Worksheet does not exist")
            finally:
                df.to_excel(writer, sheet_name="Sheet1",index=False)
                writer.save()

    def get_calories_per_food_item(self,ingredient):
        self.load_calorie_dict()
        match_items = list()
        for key in self.food_items:
            if ingredient in key:
                match_items.append(key)
        if len(match_items) < 1:
            print(ingredient,"not found")
            return None,None,None,None,None
        elif len(match_items) == 1:
            key = match_items[0]
            index = self.food_items.index(key)         
            return int(self.calories[index]), self.measures[index],int(self.protein[index]),int(self.fats[index]),int(self.carbohydrates[index]) 
        else: 
            match_string = ""
            for i,item in enumerate(match_items):
                match_string += f"Index{i}:{item},"
            match_string = match_string[:-1]
            st.text_input(label=f"Pick index of the items which matches \"{ingredient}\":\n  {match_string}:"
            , key='add_item')
            key = match_items[int(st.session_state["add_item"])]
            if not key in match_items:
                return None,None,None,None,None
            index = self.food_items.index(key)
            return int(self.calories[index]), self.measures[index],int(self.protein[index]),int(self.fats[index]),int(self.carbohydrates[index]) 

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

    def add_meal_for_the_day(self,type_of_meal,meal,quantity,ismeal=True):
        calories,measure,protein,fats,carbohydrates = self.get_calories_per_food_item(meal)
        if not calories:
            if (ismeal):
                print("Adding new meal.")
                fname = "new_recipe.json" 
                f = open(fname)
                recipe = json.load(f)
                f.close() 
                if not (meal in recipe.keys()):
                    print("Add the meal to new_recipe.json")
                    return 
                self.adding_new_and_update_recipes()
            else:
                self.add_item_to_dictionary(meal)
                
        index = self.mealtime_list.index(type_of_meal)
        calories,measure,protein,fats,carbohydrates = self.get_calories_per_food_item(meal)
        self.meal_list[index].append((meal,quantity,calories * quantity,protein * quantity,fats * quantity,carbohydrates * quantity))
        print(f"Type of meal {type_of_meal}, Meal {meal} Quantity {quantity} Calories {calories*quantity}")

    def get_nutrition_facts(self,recipe,no_of_servings):       
        for recipe_name,recip in recipe.items():
            ingre_dict = dict()
            total_cals = 0
            total_protein = 0
            total_fats = 0
            total_carbs = 0
            for ingredient,quantity in recip.items():
                print("For ingredient: "+ingredient)
                quantity = float(quantity)
                calories,measure,protein,fats,carbohydrates = self.get_calories_per_food_item(ingredient)
                if calories == None:
                    print(f"Ingredient {ingredient} Details:")
                    self.add_item_to_dictionary(ingredient)
                    self.load_calorie_dict()
                    calories,measure,protein,fats,carbohydrates = self.get_calories_per_food_item(ingredient)
                measure = str(measure)
                measure_list = measure.split(" ")
                if len(measure_list) > 1:
                    measure = measure.split(" ").pop()
                else:
                    measure = ""
                ingre_dict[ingredient] = str(quantity) + " " + measure
                total_cals += calories * quantity
                total_protein += protein * quantity
                total_fats += fats * quantity
                total_carbs += carbohydrates * quantity
        total_cals /= no_of_servings
        total_protein /= no_of_servings
        total_fats /= no_of_servings
        total_carbs /= no_of_servings
        return recipe_name,ingre_dict,total_cals,total_protein,total_fats,total_carbs

    def write_to_recipes_json_file(self,recipes):
        file = 'recipes.json'
        if (os.path.exists(file)):
            os.remove(file)
        json_object = json.dumps(recipes, indent=4)
        with open("recipes.json", "w") as outfile:
            outfile.write(json_object)

    def adding_new_and_update_recipes(self):        
        f = open('new_recipe.json')
        recipes = json.load(f)
        for recipe,ingredients in recipes.items():
            recipe_json_file = open('recipes.json')
            available_recipes = json.load(recipe_json_file)
            recipe_json_file.close()
            if recipe in available_recipes.keys():
                update_meal = 1
                create_meal = 0
            else:
                update_meal = 0
                create_meal = 1
            self.load_calorie_dict()
            st.text_input(label=f"No of servings for {recipe}: ", key='no_of_servings')
            no_of_servings = float(st.session_state["no_of_servings"])
            recipe_dict = dict()
            recipe_dict[recipe] = ingredients 
            recipe_name,ingre_dict,total_cals,total_protein,total_fats,total_carbs = self.get_nutrition_facts(recipe_dict,no_of_servings)

            f = open('recipes.json')
            recipes_json = json.load(f)
            f.close()
            ingre_dict['total_cals'] = total_cals
            ingre_dict['total_protein'] = total_protein
            ingre_dict['total_fats'] = total_fats
            ingre_dict['total_carbs'] = total_carbs
            ingre_dict['no_of_servings'] = no_of_servings
            recipes_json[recipe_name] = ingre_dict
            self.write_to_recipes_json_file(recipes_json)
            
            calorie_dict_file = 'calorie_dict.xlsx'
            calorie_dict_dataframe = pd.read_excel(calorie_dict_file,engine = 'openpyxl')
            recipes_excel = 'recipes.xlsx'
            recipes_excel_dataframe = pd.read_excel(recipes_excel,engine = 'openpyxl')
            if create_meal == 1 and update_meal == 0:
                calorie_dict_dataframe_intermediate = {'food_item':recipe_name,'measure':'1 serving','calories':total_cals,"protein":total_protein,"fats":total_fats,"carbohydrates":total_carbs}
                calorie_dict_dataframe = calorie_dict_dataframe.append(calorie_dict_dataframe_intermediate, ignore_index = True)
            
                recipes_excel_dataframe_intermediate = {'Recipe Name':recipe_name,'Ingredients':ingre_dict,'No of servings':no_of_servings,"Total Cals":total_cals,"Total protein":total_protein,"Total fats":total_fats,"Total Carbs":total_carbs}
                recipes_excel_dataframe = recipes_excel_dataframe.append(recipes_excel_dataframe_intermediate, ignore_index = True)
            elif create_meal == 0 and update_meal == 1:
                calorie_dict_index = calorie_dict_dataframe.index[calorie_dict_dataframe['food_item']==recipe]
                calorie_dict_dataframe.iloc[calorie_dict_index] = [recipe,'1 serving',total_cals,total_protein,total_fats,total_carbs]
                
                recipes_excel_index = recipes_excel_dataframe.index[recipes_excel_dataframe['Recipe Name']==recipe]
                recipes_excel_dataframe.iloc[recipes_excel_index] = [recipe,ingre_dict,no_of_servings,total_cals,total_protein,total_fats,total_carbs]
                
            self.update_excel_file(calorie_dict_dataframe,calorie_dict_file)
            self.update_excel_file(recipes_excel_dataframe,recipes_excel)
            self.load_calorie_dict()

    def print_calorie_data(self,calories_burnt_with_exercise):
        fpath = 'ww' + str(self.week_no) + '_calorie_tracker'
        if not (os.path.exists(fpath)):
            os.mkdir(fpath)
        fname = fpath + os.sep + self.date + '.txt'
        if (os.path.exists(fname)):
            os.remove(fname)
        f = open(fname,"w")
        full_total_stats = [0,0,0,0,0,0]
        
        df2 = dict()
        df2["Date"] = self.date        
        for index,type_of_meal in enumerate(self.mealtime_list):
            total_stats = [0,0,0,0]
            text = ""
            f.write(f"{type_of_meal.capitalize()}: \n")
            for stats in self.meal_list[index]:
                item = f"{stats[0]}:{stats[2]} quantity:{stats[1]}"
                f.write(item+"\n")
                text += item+","
                for i in range(len(total_stats)):
                    total_stats[i] += stats[i + 2]  
            meal_total = f"Total Cals:{total_stats[0]} Total Protein:{total_stats[1]} Total Fats:{total_stats[2]} Total Carbs:{total_stats[3]}"        
            f.write(meal_total + "\n")
            text += meal_total
            for i in range(len(total_stats)):
                    full_total_stats[i] += total_stats[i]
            df2[type_of_meal.capitalize()] = text

        bmr = (10 * self.current_weight) + (6.25 * 155) - (5 * 29) - 161
        total_cals_to_consume_per_day = 1.55 *  bmr
        calorie_deficit = total_cals_to_consume_per_day - full_total_stats[0] + calories_burnt_with_exercise
        full_total_stats[4] = total_cals_to_consume_per_day
        full_total_stats[5] = calorie_deficit
        
        columns = ['Total cals','Total protein','Total fats','Total carbs','Total cals to consume per day','Calorie deficit']
        for i,column in enumerate(columns):
            f.write(f'{column}: {str(full_total_stats[i])} \n')
            df2[column] = full_total_stats[i]

        fname = 'calorie_dairy.xlsx'
        df = pd.read_excel(fname,engine = 'openpyxl')
        dates = df['Date'].to_list()
        if self.date in dates:
            index = df.index[df['Date']==self.date]
            df.iloc[index] = df2.values()
        else:
            df = df.append(df2, ignore_index = True)
        self.update_excel_file(df,fname)
