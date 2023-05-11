from flask import render_template, url_for, flash, redirect, request,session
from sign_package import app, db
from sign_package.forms import RegistrationForm, LoginForm
from sign_package.models import User
from flask_login import login_user, logout_user, login_required, current_user
import cv2
import numpy as np
import os
# import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import operator
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath

letters = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/')
@app.route("/home")
def home():
	return render_template('home_page.html')
@app.route("/numbers_lesson")

def lesson_number():
	return render_template('numbers_lessons_page.html')


@app.route("/alphabets_lesson")
@login_required
def lesson_alphabet():
	return render_template('alphabets_lessons_page.html')

@app.route("/alphabets_lesson2")
@login_required
def lesson_alphabet2():
	return render_template('alphabets_lessons_page2.html')


@app.route("/course_option")
@login_required
def course_option():
	return render_template('course_option.html')

@app.route("/profile")
@login_required
def profile_page():

	username = session["username"]
	user = User.query.filter_by(username = username).first()	
	return render_template('profile_page.html', user = user)	



@app.route("/chapter_page")
@login_required
def chapter():
	return render_template('chapter_page.html')		

@app.route("/about_sl")
def about():
	return render_template('about_sl.html')		




@app.route("/register", methods = ['GET', 'POST'])
def register():
	forms = RegistrationForm()
	if forms.validate_on_submit():
		user = User(name = forms.name.data, username = forms.username.data, email = forms.email.data, password = forms.password.data)
		# db.create_all()
		db.session.add(user)
		db.session.commit()
		flash(f' Account successfully created !')
		return redirect(url_for('home'))

	if (current_user.is_authenticated):
		return redirect(url_for('lesson'))

	else:
		return render_template('registration_page.html', forms = forms)		



@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route("/model_test")
def modelTest():
    test = np.random.randint(0,36)
    letters[test]
    return render_template('Model_Test.html', quiz=letters[test])

@app.route("/login", methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()

		if(user and user.password == form.password.data):
			session["username"] = user.username
			login_user(user)
			return redirect(url_for('course_option'))

		else:
			flash('Login unsuccessful')


	if (current_user.is_authenticated):
		return redirect(url_for('course_option'))	

	else:		
		return render_template('login.html', form = form)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@app.route("/model_test",methods=['GET', 'POST'])
def model_test():
    test = np.random.randint(0,36)
    if request.method == 'POST':
        name = request.form.get('name')
        
        classifier_1 = load_model(join(dirname(realpath(__file__)), 'static/models/main_number_classifier.h5'))
        classifier_2 = load_model(join(dirname(realpath(__file__)), 'static/models/main_alphabet_classifier.h5'))
        # check if the post request h       as the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            frame = cv2.imread(img_path)
            image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

            pixel_values= image.reshape((-1,3))
            pixel_values = np.float32(pixel_values)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,100,0.2)
            _, labels, (centers) = cv2.kmeans(pixel_values, 7, None, criteria, 10,cv2.KMEANS_RANDOM_CENTERS)
            centers = np.uint8(centers)
            labels = labels.flatten()
            segmented_image = centers[labels.flatten()]
            segmented_image = segmented_image.reshape(image.shape)
            if(test <= 9):
                name = 'numbers'
            else:
                name = 'alphabet'
            if (name == 'numbers'):
                classifier_1 = load_model(join(dirname(realpath(__file__)), 'static/models/main_number_classifier.h5'))
                result = classifier_1.predict(segmented_image.reshape(-1, 250, 250, 3))
                prediction = {'ZERO': result[0][0], 'ONE': result[0][1], 'TWO': result[0][2],'THREE': result[0][3],'FOUR': result[0][4],'FIVE': result[0][5],
                        'SIX': result[0][6], 'SEVEN': result[0][7], 'EIGHT': result[0][8],'NINE': result[0][9]}
                prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
                if(prediction[0][0] == letters[test]):
                    resul = "Your Answer is Correct, Predicted Letter is " + prediction[0][0]
                else:
                    resul = "Your Answer is Incorrect, Predicted Letter is " + prediction[0][0]
                
                return render_template('Model_Test.html', title='detection', pred = resul)
            elif(name == 'alphabet'):
                classifier_2 = load_model(join(dirname(realpath(__file__)), 'static/models/main_alphabet_classifier.h5'))
                result = classifier_2.predict(segmented_image.reshape(-1, 250, 250, 3))
                prediction = {'A': result[0][0],'B': result[0][1], 'C': result[0][2], 'D': result[0][3],'E': result[0][4],'F': result[0][5],
                  'G': result[0][6],'H': result[0][7], 'I': result[0][8], 'J': result[0][9],'K': result[0][10],'L': result[0][11],
                  'M': result[0][12],'N': result[0][13], 'O': result[0][14], 'P': result[0][15],'Q': result[0][16],'R': result[0][17],
                  'S': result[0][18],'T': result[0][19], 'U': result[0][20], 'V': result[0][21],'W': result[0][22],'X': result[0][23],
                  'Y': result[0][24],'Z': result[0][25]}
                prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
                if(prediction[0][0] == letters[test]):
                    resul = "Your Answer is Correct, Predicted Letter is " + prediction[0][0]
                else:
                    resul = "Your Answer is Incorrect, Predicted Letter is " + prediction[0][0]
                return render_template('Model_Test.html', title='detection', pred = resul)
    return render_template('Model_Test.html', title='detection', quiz=letters[test])