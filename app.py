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
                'nom': row['Choix'],
                'effet_Oui_R': convert_to_int(row['Oui_R']),
                'effet_Oui_C': convert_to_int(row['Oui_C']),
                'effet_Oui_I': convert_to_int(row['Oui_I ']),
                'effet_Oui_D': convert_to_int(row['Oui_D']),
            
                'effet_non_R': convert_to_int(row['Non_R']),
                'effet_non_C': convert_to_int(row['Non_C ']),
                'effet_non_I': convert_to_int(row['Non_I ']),
                'effet_non_D': convert_to_int(row['Non_D']),

                'defense_feu': convert_to_int(row['feu']),
                'defense_terre': convert_to_int(row['terre']),
                'defense_eau': convert_to_int(row['eau']),
                'defense_air': convert_to_int(row['air']),

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

    cards = read_card_data('./static/cartes_action_test.tsv')

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data.db')}"
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    @app.route('/')
    def login():
        return render_template("login.html")

    @app.route('/debrief1')
    def debrief1():
        return render_template("debrief1.html")
    
    @app.route('/phase2')
    def phase2():
        return render_template("phase2.html")

    @app.route('/debrief2')
    def debrief2():
        return render_template("debrief2.html")

    @app.route('/phase3')
    def phase3():
        return render_template("phase3.html")
    
    @app.route('/session', methods=['POST'])
    def identification():
        if request.method=='POST':
            try:
                id = request.form.get('number')
                nouvelles_metrics = UserMetrics(
                    id=int(id),
                    jauge_r=50,
                    jauge_c=50,
                    jauge_i=50,
                    jauge_d=0, 
                    bonus_r=0,
                    bonus_c=0,   
                    bonus_i=0,
                    defense_feu=0, 
                    defense_terre=0,
                    defense_eau=0,
                    defense_air=0,
                    compteur_cartes=0, 
                    timer_total=0
                )
                db.session.add(nouvelles_metrics)
                db.session.commit()
            except:
                None
        resp = jsonify(success=True)
        return render_template("phase1.html")

    @app.route('/api/cards')
    def get_cards():
        return jsonify({'cards': cards}) 

    with app.app_context():
        meta = db.metadata
        db.create_all()

    @app.route('/get-jauge/<user>')
    def getjauge(user):
        userMetrics = db.session.query(UserMetrics).get(user)
        return jsonify({
                        'jauge_r':userMetrics.jauge_r, 
                        'jauge_c': userMetrics.jauge_c, 
                        'jauge_i': userMetrics.jauge_i, 
                        'jauge_d':userMetrics.jauge_d, 
                        'bonus_r':userMetrics.bonus_r,
                        'bonus_c':userMetrics.bonus_c,
                        'bonus_i':userMetrics.bonus_i,
                        'defense_feu': userMetrics.defense_feu, 
                        'defense_terre': userMetrics.defense_terre, 
                        'defense_eau':userMetrics.defense_eau, 
                        'defense_air':userMetrics.defense_air, 
                        'compteur_cartes':userMetrics.compteur_cartes, 
                        'timer_total':userMetrics.timer_total})

    @app.route('/put-jauge/<user>', methods=['PUT'])
    def putjauge(user):
        userMetrics = db.session.query(UserMetrics).get(user)

        if userMetrics:
            data = request.get_json()
            
            userMetrics.jauge_r += data.get('jauge_r', 0)
            userMetrics.jauge_c += data.get('jauge_c', 0)
            userMetrics.jauge_i += data.get('jauge_i', 0)
            userMetrics.jauge_d += data.get('jauge_d', 0)
            userMetrics.bonus_r += data.get('bonus_r', 0)
            userMetrics.bonus_c += data.get('bonus_c', 0)
            userMetrics.bonus_i += data.get('bonus_i', 0)
            userMetrics.defense_feu += data.get('defense_feu', 0)
            userMetrics.defense_terre += data.get('defense_terre', 0)
            userMetrics.defense_eau += data.get('defense_eau', 0)
            userMetrics.defense_air += data.get('defense_air', 0)

            if 'timer_total' in data:
                userMetrics.timer_total = data['timer_total']
                userMetrics.compteur_cartes += 1

            db.session.commit()

            return jsonify({'message': 'UserMetrics mis à jour'})
        else:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404

    @app.route('/reset-jauge/<user>')
    def resetjauge(user):
        userMetrics = db.session.query(UserMetrics).get(user)

        if userMetrics:
            userMetrics.jauge_r = 50
            userMetrics.jauge_c = 50
            userMetrics.jauge_i = 50
            userMetrics.jauge_d = 0
            userMetrics.defense_feu=0
            userMetrics.defense_terre=0
            userMetrics.defense_eau=0
            userMetrics.defense_air=0
            userMetrics.compteur_cartes=0
            userMetrics.timer_total=0
            db.session.commit()

            return jsonify({'message': 'UserMetrics mis à jour'})
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


