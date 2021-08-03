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


