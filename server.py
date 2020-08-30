# This app uses Bootstrap framework

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask import  render_template,url_for,redirect,flash,request,jsonify
import random
import os

from werkzeug.routing import BaseConverter

# from stack overflow here: https://stackoverflow.com/questions/35437180/capture-a-list-of-integers-with-a-flask-route
class IntListConverter(BaseConverter):
    regex = r'\d+(?:,\d+)*,?'

    def to_python(self, value):
        return [int(x) for x in value.split(',')]

    def to_url(self, value):
        return ','.join(str(x) for x in value)

### This should be a path on server ###

# The server does not actually have a front-end
HOME = os.environ['HOME']
UPLOAD_FOLDER = os.path.join(HOME, 'Call_grandma/static/images/')
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['SECRET_KEY'] = '323b22caac41acbf'
app.config['SQLALCHEMY'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.url_map.converters['int_list'] = IntListConverter

db = SQLAlchemy(app)

association_table = db.Table('association',
    db.Column('young_id', db.Integer, db.ForeignKey('youngling.id'), primary_key=True),
    db.Column('elder_id', db.Integer, db.ForeignKey('elderly.id'), primary_key=True)
)

class Youngling(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(80))
    # elderlies = db.relationship('Elderly', \
    #     secondary=association_table, lazy='subquery', \
    #     backref=db.backref('younglings', lazy=True))

class Elderly(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    younglings = db.relationship('Youngling', \
        secondary=association_table, lazy='subquery', \
        backref=db.backref('elderlies', lazy=True))

db.create_all()
db.session.commit()
# shupeng = Youngling(name="Shupeng")
# db.session.add(shupeng)
# ella = Youngling(name="Ella")
# db.session.add(ella)
# db.session.commit()

#------------------------ Routes -------------------------#
# for i in range(10):
#     user = Youngling(name='Shupneg'+str(i))
#     db.session.add(user)
# for i in range(10):
#     user = Elderly(name='Yulan'+str(i))
#     user.younglings
# db.commit()    

@app.route("/")
@app.route("/youngling_home", methods=['GET', 'POST']) # actually login
def youngling_home():
    if request.method == "POST":
        name = request.form.get('name')
        user = db.session.query(Youngling).filter_by(name=name).one_or_none()
        if user == None:
            user = Youngling(name=name)
            db.session.add(user)
            db.session.commit()
        print(user)
        print(user.name)
        print(user.id)
        pic = request.files['file']
        # print(app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Youngling/')
        file_path = os.path.join(file_path, str(user.id))
        # pic.name = str(user.id)
        pic.save(file_path)
        return redirect(url_for('add_elderly_info', current_user=user.id))
    return render_template('youngling_home.html')
    
@app.route("/add_elderly_info/<current_user>", methods=['GET', 'POST'])
def add_elderly_info(current_user):
    print()
    print("current user: " + str(current_user))
    print()
    current_user = int(current_user)
    if request.method == "POST":
        name = request.form.get('name')
        user = db.session.query(Elderly).filter_by(name=name).one_or_none()
        if user == None:
            user = Elderly(name = name)
            pic = request.files['file']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Elderly/')
            file_path_full = os.path.join(file_path, str(user.id))
            pic.name = str(user.id)
            pic.save(file_path_full)
            # print(current_user)
            youngs = db.session.query(Youngling).all()
            print(len(youngs))
            for i in youngs:
                print(i.id)
            print()

            young = db.session.query(Youngling).filter_by(id=current_user).one()
            user.younglings.append(young)
        else:
            young = db.session.query(Youngling).filter_by(id=current_user).one()
            user.younglings.append(young)
        flash("Success") 
        return redirect(url_for('messaging_young'))
    return render_template('fill_elderly_info.html', id = current_user)

@app.route("/elderly_home", methods=['GET', 'POST'])
def elderly_register():
    if request.method == 'POST':
        #--- fake fake ---#
        ids = [1,2,3,4,5,6,7,8,9]
        return redirect(url_for('elderly_home_verify_pics', values = ids))
        #--- legit logic ---#
        # elderly_name = request.form.get('name')
        # # search in the db
        # elderlies = db.session.query(Elderly).filter_by(name=elderly_name).all()
        # if len(elderlies) == 1:
        #     return redirect(url_for('messaging_elder'))
        # else:
        #     ids = []
        #     for elderly in elderlies:
        #         # return a response with 9 pictures
        #         for young in elderly.younglings:
        #             ids.append(young.id)
        #     if len(ids) <= 9:
        #         max_ids = db.session.query(Youngling).count()
        #         l = len(ids)
        #         while l <= 9:
        #             ids.append(random.randint(len(ids), max_ids-1))
        #             l += 1
        #     # now len(ids) == 9
        #     random.shuffle(ids)
        #     return redirect(url_for('elderly_home_verify_pics', values = ids))

    return render_template('elderly_home.html', flag=0)    

@app.route("/elderly_home_verify_pics/", methods=['GET', 'POST'])
@app.route("/elderly_home_verify_pics/<int_list:values>", methods=['GET', 'POST'])
def elderly_home_verify_pics(values=None):
    # for each id in values there is a corresponding picture, render template with the pictures
    # pass in a list of file paths to html

    # fake 
    if request.method == 'POST' and values==None:
        return redirect(url_for('messaging_elder'))
    # legit verification
    path_lis = []
    for id in values:
        path = os.path.join("/static/images", 'Youngling/')
        path = os.path.join(path, str(id))
        path_lis.append(path)

    print(path_lis)
    print(values)
    if request.method == 'POST':
        # if it is post, the user already selected some pictures
        selected_ids = request.form.getlist('ids')
        elderly_name = request.form.get('name')
        elderlies = db.session.query(Elderly).filter_by(name=elderly_name).all()
        for elderly in elderlies:
            youngling_ids = [i.id for i in elderly.younglings]
            flag = 0
            if all(id in youngling_ids for id in selected_ids):
                flag = 1
            if flag == 0:
                flash("Wrong selections")
                return render_template('elderly_home.html', path_lis=path_lis)
            else:
                return redirect(url_for('messaging_elder'))
    
    return render_template('elderly_home2.html', path_lis=path_lis, id_lis=values)

@app.route("/messaging_elder", methods=['GET', 'POST'])
def messaging_elder():
    return render_template('messaging_elder1.html')
    # POST accepts a form which contains eid, yid, message as a file 
    # POST then sends the message to young with yid  HOW???

@app.route("/messaging_young", methods=['GET', 'POST'])
def messaging_young():
    # return render_template('messaging_young.html')
    return "Here should be the messsages from the elderly!"

#------------------------------------------------------------#

app.run(host="localhost", port=8000, debug=True)