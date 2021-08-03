from app import app, db
from flask import (Flask,
                   render_template,
                   request,
                   url_for,
                   flash,
                   redirect,
                   session)
from app.forms import (SearchForm,
                       LoginForm,
                       RegistrationForm,
                       AddToFoodLogForm,
                       RemoveFood,
                       FoodLogDatePicker,
                       SetMacroForm,
                       SetMacroGrams,
                       QuickAddCals,
                       CopyMealForm)
from app.models import User, Food
import requests
from jinja2 import Template
from flask_login import login_required, logout_user, current_user, login_user
from werkzeug.urls import url_parse
from datetime import datetime, timedelta
from sqlalchemy import desc
from sqlalchemy.orm.session import make_transient


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
@app.route('/search/<string:date>/<string:meal>', methods=['GET', 'POST'])
@login_required
def search(date=None, meal=None):
    form = SearchForm()

    if request.method == 'GET':
        food_list_clean = []
        recent_list = True
        recent_foods = Food.query.filter_by(user_id=current_user.get_id()).order_by(
            desc(Food.id)).group_by(Food.food_name)

        for food in recent_foods:
            food_list_clean.append((food.food_name, food.ndbno, food.id))

        return render_template('search.html', form=form, food_list_clean=food_list_clean,
                               recent_list=recent_list, date=date, meal=meal)

    if request.method == 'POST':
        if request.form["action"] == "multiadd":
            food_ids = request.form.getlist("selected")

            if meal == None:
                meal = request.form.get('mealselect')

            for food_id in food_ids:
                food = Food.query.filter_by(id=food_id).first()
                food = Food(food_name=food.food_name, count=food.count,
                            kcal=food.kcal,
                            protein=food.protein,
                            fat=food.fat,
                            carbs=food.carbs,
                            unit=food.unit, meal=meal,
                            ndbno=food.ndbno, date=date,
                            user_id=current_user.get_id())
                db.session.add(food)
                db.session.commit()
            return redirect(url_for('food_log', date_pick=date))

        else:
            recent_list = False

            # get user input from search bar
            food_search = form.search.data
            if food_search == "":
                return redirect(url_for('search', date=date, meal=meal))

            # build API URL to search for food
            search_url = "https://api.nal.usda.gov/ndb/search/?format=json"
            params = dict(
                q=food_search,
                sort="r",
                max="100",
                offset="0",
                ds="Standard Reference",
                api_key="ozs0jISJX6KiGzDWdXI7h9hCFBwYvk3m11HKkKbe"
            )

            # build list of tuples w/ name of food and associated ndbno (unique ID)
            resp = requests.get(url=search_url, params=params)
            if "zero results" in str(resp.json()):
                flash("No results found.")
                return redirect(url_for('search'))
            else:
                food_list = resp.json()['list']['item']
                food_list_clean = []

                for i in food_list:
                    food_list_clean.append((i['name'], i['ndbno']))

                # return list of food to web page
                return render_template('search.html', date=date, meal=meal,
                                       food_list_clean=food_list_clean, form=form, recent_list=recent_list)


@app.route('/food/<string:ndbno>', methods=['GET', 'POST'])
@app.route('/food/<string:date>/<string:meal>/<string:ndbno>',
           methods=['GET', 'POST'])
@login_required
def get_nutrition(ndbno, meal=None, date=datetime.now()):
    form1 = AddToFoodLogForm()

    search_url = "https://api.nal.usda.gov/ndb/nutrients/?format=json"
    params = dict(
        api_key="ozs0jISJX6KiGzDWdXI7h9hCFBwYvk3m11HKkKbe",
        nutrients=["205", "204", "208", "203"],
        ndbno=ndbno
    )

    resp = requests.get(url=search_url, params=params)

    if "No food" in str(resp.json()):
        flash("No foods found.")
        return redirect(url_for('search'))
    else:
        food_name = resp.json()['report']['foods'][0]['name']
        food_measure = resp.json()['report']['foods'][0]['measure']
        food_cals = resp.json()['report']['foods'][0]['nutrients'][0]['value']
        food_protein = resp.json(
        )['report']['foods'][0]['nutrients'][1]['value']
        food_fat = resp.json()['report']['foods'][0]['nutrients'][2]['value']
        food_carbs = resp.json()['report']['foods'][0]['nutrients'][3]['value']

    if request.method == 'GET':
        return render_template('nutrition.html',
                               meal=meal,
                               date=date,
                               food_name=food_name,
                               food_measure=food_measure,
                               food_cals=food_cals,
                               food_protein=food_protein,
                               food_fat=food_fat,
                               food_carbs=food_carbs,
                               ndbno=ndbno,
                               form1=form1,
                               )

    if request.method == 'POST':
        if meal is None:
            meal_choice = form1.meal.data
        else:
            meal_choice = meal

        try:
            quant_choice = float(form1.quantity.data)
        except:
            flash("Please enter valid values.")
            return redirect(url_for('get_nutrition', ndbno=ndbno,
                                    meal=meal, date=date))
        else:
            if quant_choice > 10000 or meal_choice not in ("Breakfast", "Lunch", "Dinner", "Snacks"):
                flash("Please enter valid values.")
                return redirect(url_for('get_nutrition', ndbno=ndbno,
                                        meal=meal, date=date))
            else:
                food = Food(food_name=food_name, count=quant_choice,
                            kcal=quant_choice * float(food_cals),
                            protein=quant_choice * float(food_protein),
                            fat=quant_choice * float(food_fat),
                            carbs=quant_choice * float(food_carbs),
                            unit=food_measure, meal=meal_choice,
                            date=date, ndbno=ndbno, user_id=current_user.get_id())
                db.session.add(food)
                db.session.commit()

                return redirect(url_for('food_log', date_pick=date))


