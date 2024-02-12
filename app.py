import flask
from flask import Flask, jsonify, after_this_request, abort, make_response
from flask import render_template, request, send_file, redirect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase
import re
import os
import sys
import pickle
from sqlitedict import SqliteDict
from flask_cors import CORS
from flask import Response
import traceback 
import requests
import json 
import random as rd
import csv
import sqlite3
import io
from tqdm import tqdm
import phases.first_phase       #on sait jamais de combien de librairies on a besoin

# Check for empty strings and convert to integers
def convert_to_int(value):
    if value != '':
        return(int(value)) 
    else:
        return 0

def convert_bonus_to_list(bonus):
    if bonus=='':
        return([0,0,0])
    else:
        return([int(elt) for elt in bonus.split(',')])

# Read TSV file and parse card data
def read_card_data(file_path):
    cards = []
    with open(file_path, 'r', newline='', encoding='utf-8') as mycsv:
        reader = csv.DictReader(mycsv, delimiter='\t')
        for idx, row in enumerate(reader):
            if row['Oui_R'] == '':
                break

            bonus_oui = convert_bonus_to_list(row.get('bonus_oui_RCI', ''))
            bonus_non = convert_bonus_to_list(row.get('bonus_non_RCI', ''))

            card = {
                'index': idx,
                'name': row['Choix'],
                'effect_yes_R':  convert_to_int(row['Oui_R']),
                'effect_yes_C': convert_to_int(row['Oui_C']),
                'effect_yes_I': convert_to_int(row['Oui_I ']),
                'effect_yes_D': convert_to_int(row['Oui_D']),
            
                'effect_no_R': convert_to_int(row['Non_R']),
                'effect_no_C': convert_to_int(row['Non_C ']),
                'effect_no_I': convert_to_int(row['Non_I ']),
                'effect_no_D': convert_to_int(row['Non_D']),

                'fire_defense': convert_to_int(row['feu']),
                'earth_defense': convert_to_int(row['terre']),
                'air_defense': convert_to_int(row['air']),
                'water_defense': convert_to_int(row['eau']),

                'bonus_oui_R': bonus_oui[0],
                'bonus_oui_C': bonus_oui[1],
                'bonus_oui_I': bonus_oui[2],
                
                'bonus_non_R': bonus_non[0],
                'bonus_non_C': bonus_non[1],
                'bonus_non_I': bonus_non[2],

                'intro': row.get('intro', ''),
                'outro': row.get('outro', ''),

            }

            cards.append(card)
    return cards

def create_app():
    from database.table import UserMetrics
    basedir = os.path.abspath(os.path.dirname(__file__))

    #Generate the cards only once
    cards = read_card_data('./static/cartes_action_test.tsv')

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data.db')}"
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    @app.route('/')
    def login():
        return render_template("login.html")
    
    #tableauprevention
    @app.route('/tableauprevention')
    def tableauprevention():
        return render_template("tableauprevention.html")

    #débrief1
    @app.route('/debrief1')
    def debrief1():
        return render_template("debrief1.html")
    
    #phase2
    @app.route('/second_phase')
    def second_phase():
        return render_template("second_phase.html")
    
    #débrief2
    @app.route('/debrief2')
    def debrief2():
        return render_template("debrief2.html")

    #phase3/fin?
    @app.route('/third_phase')
    def third_phase():
        return render_template("third_phase.html")
    
    @app.route('/session', methods=['POST'])
    def identification():
        if request.method=='POST':
            try:
                id = request.form.get('number')
                nouvelles_metrics = UserMetrics(
                    id=int(id),
                    jauge_i=50,
                    jauge_r=50,
                    jauge_c=50,
                    jauge_d=0, 
                    bonus_i=0,
                    bonus_r=0,
                    bonus_c=0,           
                    air_defense=0,
                    water_defense=0,
                    earth_defense=0,
                    fire_defense=0, 
                    compteur_cartes=0, 
                    timer_total=0
                )
                db.session.add(nouvelles_metrics)
                db.session.commit()
            except:
                None
        resp = jsonify(success=True)
        return render_template("index.html")

    # Flask endpoint to serve card data
    @app.route('/api/cards')
    def get_cards():
        return jsonify({'cards': cards}) 

    with app.app_context():
        meta = db.metadata
        db.create_all()

    @app.route('/get-jauge/<user>')
    def getjauge(user):
        userMetrics = db.session.query(UserMetrics).get(user)
        return jsonify({'jauge_c': userMetrics.jauge_c, 
                        'jauge_i': userMetrics.jauge_i, 
                        'jauge_r':userMetrics.jauge_r, 
                        'jauge_d':userMetrics.jauge_d, 
                        'bonus_i':userMetrics.bonus_i,
                        'bonus_r':userMetrics.bonus_r,
                        'bonus_c':userMetrics.bonus_c,  
                        'water_defense':userMetrics.water_defense, 
                        'earth_defense': userMetrics.earth_defense, 
                        'air_defense':userMetrics.air_defense, 
                        'fire_defense': userMetrics.fire_defense, 
                        'compteur_cartes':userMetrics.compteur_cartes, 
                        'timer_total':userMetrics.timer_total})

    @app.route('/put-jauge/<user>', methods=['PUT'])
    def putjauge(user):
        userMetrics = db.session.query(UserMetrics).get(user)

        if userMetrics:
            data = request.get_json()

            userMetrics.jauge_i += data.get('jauge_i', 0)
            userMetrics.jauge_r += data.get('jauge_r', 0)
            userMetrics.jauge_c += data.get('jauge_c', 0)
            userMetrics.jauge_d += data.get('jauge_d', 0)
            userMetrics.bonus_i += data.get('bonus_i', 0)
            userMetrics.bonus_r += data.get('bonus_r', 0)
            userMetrics.bonus_c += data.get('bonus_c', 0)
            userMetrics.water_defense += data.get('water_defense', 0)
            userMetrics.earth_defense += data.get('earth_defense', 0)
            userMetrics.fire_defense += data.get('fire_defense', 0)
            userMetrics.air_defense += data.get('air_defense', 0)

            if 'timer_total' in data:
                userMetrics.timer_total = data['timer_total']
                userMetrics.compteur_cartes += 1

            db.session.commit()

            return jsonify({'message': 'UserMetrics updated successfully'})
        else:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

    @app.route('/reset-jauge/<user>')
    def resetjauge(user):
        userMetrics = db.session.query(UserMetrics).get(user)

        if userMetrics:
            userMetrics.jauge_i = 50
            userMetrics.jauge_r = 50
            userMetrics.jauge_c = 50
            userMetrics.jauge_d = 0
            userMetrics.air_defense=0
            userMetrics.water_defense=0
            userMetrics.earth_defense=0
            userMetrics.fire_defense=0
            userMetrics.compteur_cartes=0
            userMetrics.timer_total=0
            db.session.commit()

            return jsonify({'message': 'UserMetrics updated successfully'})
        else:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
    @app.route('/download_debrief1')
    def export_data():
        conn = sqlite3.connect('./data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_metrics')
        data = cursor.fetchall()

        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerows(data)

        return csv_data.getvalue()

    @app.route('/download-rpg-game')
    def dowloadgame():
        return send_file('../MyFirstGameSetup.exe',as_attachment=True)

    return app

    


class Base(DeclarativeBase):
   pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()


if __name__ == '__main__':
    app = create_app()
    app.run(port=10407)


