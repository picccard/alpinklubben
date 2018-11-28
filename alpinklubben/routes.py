"""

	Title:	routes.py
    Pkg:    alpinklubben
	Date:	02.11.2018
	Author:	Eskil Uhlving Larsen

"""

from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from alpinklubben import app, db, bcrypt
from alpinklubben.forms import RegistrationForm, LoginForm, UpdateAccountForm, OrderHeiskortForm, OrderSkipakkeForm
from alpinklubben.models import User, Heiskort, SoldHeiskort, Skipakke, SoldSkipakke
import os
import secrets
from PIL import Image
import datetime


# Adds default heiskort and skipakker if none exists
allheiskort = Heiskort.query.all()
if len(allheiskort) < 1:
    db.session.add(Heiskort(type='Dagskort', age='Voksen', price=90))
    db.session.add(Heiskort(type='Ukeskort', age='Voksen',
                            price=400, image='heiskort01.jpg'))
    db.session.add(Heiskort(type='Sesongkort', age='Voksen',
                            price=2000, image='skipass3.jpg'))
    db.session.add(Heiskort(type='Dagskort', age='Barn', price=50))
    db.session.add(Heiskort(type='Ukeskort', age='Barn', price=2500))
    db.session.add(Heiskort(type='Sesongkort', age='Barn', price=1200))
    db.session.commit()
allskipakker = Skipakke.query.all()
if len(allskipakker) < 1:
    db.session.add(Skipakke(name='Skipakke01', desc='Skipakke for nybegynner',
                            hour_price=150, day_price=700, week_price=3000))
    db.session.add(Skipakke(name='Skipakke02', desc='Skipakke for erfaren alpinist',
                            hour_price=150, day_price=700, week_price=3000))
    db.session.add(Skipakke(name='Skipakke03', desc='Skipakke med twin-tip',
                            hour_price=150, day_price=700, week_price=3000))
    db.session.add(Skipakke(name='Skipakke04', desc='Skipakke for puddersnøkjøring',
                            hour_price=150, day_price=700, week_price=3000))
    db.session.add(Skipakke(name='Skipakke05', desc='Skipakke for barn under 14',
                            hour_price=150, day_price=700, week_price=3000))
    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Konto for {form.username.data} opprettet!', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registrer', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Innlogging feilet. Sjekk mail og passord en gang til.',
                  category='danger')
    return render_template('login.html', title='Logg inn', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('bye.html')


@app.route('/heiskort')
def show_heiskort():
    heiskort = Heiskort.query.all()
    # skilift_image = url_for('static', filename='imgs/skiheis.jpg')
    return render_template('heiskort.html', title='Tilgjengelige heiskort', heiskort=heiskort)


@app.route('/heiskort/bestill', methods=['GET', 'POST'])
@app.route('/heiskort/bestill/<string:card_type>/<string:card_age>', methods=['GET', 'POST'])
@login_required
def order_heiskort(card_type=None, card_age=None):
    if card_type and card_age:
        form = OrderHeiskortForm(card_type=card_type, card_age=card_age)
    elif card_type:
        form = OrderHeiskortForm(card_type=card_type)
    elif card_age:
        form = OrderHeiskortForm(card_age=card_age)
    else:
        form = OrderHeiskortForm()

    if form.validate_on_submit():
        card_type = form.card_type.data
        card_age = form.card_age.data
        fromdate = form.fromdate.data
        heiskort = Heiskort.query.filter((Heiskort.type == card_type) & (
            Heiskort.age == card_age)).first_or_404()
        user = current_user
        bought = SoldHeiskort(
            user_id=user.id, heiskort_id=heiskort.id, fromdate=fromdate)
        db.session.add(bought)
        db.session.commit()

        # Sjekk om brukeren har kjøpt andre heiskort, gi rabatt på heiskort nr3+
        heiskort_bought = SoldHeiskort.query.filter_by(
            user_id=user.id).all()
        if len(heiskort_bought) >= 3:
            RABATT = 0.90  # 10% rabatt
            price = heiskort.price * RABATT
        else:
            price = heiskort.price
        flash('Heiskort bestilt! Kostet: ' + str(price), category='success')
        return redirect(url_for('show_my_account'))

    return render_template('order_heiskort.html', title="Bestill heiskort", form=form)


@app.route('/skipakker')
def show_skipakker():
    skilift_image = url_for('static', filename='imgs/skiheis.jpg')
    skipakker = Skipakke.query.all()
    skipakke_image = url_for('static', filename='imgs/skipakke01.jpg')
    return render_template('skipakker.html', title="Tilgjengelige skipakker", skipakker=skipakker, skipakke_image=skipakke_image)


@app.route('/skipakker/bestill', methods=['GET', 'POST'])
@app.route('/skipakker/bestill/<string:id>', methods=['GET', 'POST'])
@login_required
def order_skipakker(id=None):
    if id:
        form = OrderSkipakkeForm(skipakke=id)
    else:
        form = OrderSkipakkeForm()

    if form.validate_on_submit():
        user = current_user
        skipakke_id = form.skipakke.data
        skipakke = Skipakke.query.get(skipakke_id)
        rent_type = form.rent_type.data
        rent_length = int(form.rent_length.data)
        fromdate = form.fromdate.data
        # Hardcoded rent_type not optimal
        if rent_type == 'Time':
            price = skipakke.hour_price
        elif rent_type == 'Dag':
            price = skipakke.day_price
        elif rent_type == 'Uke':
            price = skipakke.week_price
        price = price * rent_length
        # trenger ikke lagre pris i databasen, dette kan regnes ut ifra leie-type og lengde som allerede lagres

        to_rent = SoldSkipakke(user_id=user.id, skipakke_id=skipakke_id, fromdate=fromdate,
                               rent_type=rent_type, rent_length=rent_length, price_paid=price)
        db.session.add(to_rent)
        db.session.commit()
        flash('Skipakke leid! Kostet: ' + str(price), category='success')
        return redirect(url_for('show_my_account'))

    return render_template('order_skipakke.html', title="Lei skipakke", form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account/update', methods=['GET', 'POST'])
@login_required
def update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account Updated!', 'success')
        return redirect(url_for('show_my_account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route('/account', defaults={'username': None})
@app.route('/account/<string:username>')
@login_required
def show_my_account(username):
    form = UpdateAccountForm()
    update_btn = False
    if username == None:
        if current_user.is_authenticated == False:
            abort(404)
        else:
            user = current_user
            update_btn = True
            bought_heiskort = SoldHeiskort.query.filter_by(user_id=user.id)
            rented_skipakker = SoldSkipakke.query.filter_by(
                user_id=user.id)
    else:
        user = User.query.filter_by(username=username).first_or_404()
        bought_heiskort = None
        rented_skipakker = None

    form.username.render_kw = {'disabled': 'true'}
    form.email.render_kw = {'disabled': 'true'}
    del form.submit
    del form.picture
    form.username.data = user.username
    form.email.data = user.email
    image_file = url_for(
        'static', filename='profile_pics/' + user.image_file)
    return render_template('account.html', title=username,
                           image_file=image_file, form=form, update_btn=update_btn,
                           bought_heiskort=bought_heiskort, rented_skipakker=rented_skipakker)


@app.route('/kart')
def show_map():
    return render_template('map.html')


@app.route('/stats')
def show_stats():
    all_heiskort = Heiskort.query.all()
    all_heiskort_sold = SoldHeiskort.query.all()
    heiskort_type = []
    heiskort_sold = []
    for kort in all_heiskort:
        heiskort_type.append(f'{kort.type} ({kort.age})')
        kort_id = kort.id
        count_type = SoldHeiskort.query.filter_by(heiskort_id=kort.id).all()
        heiskort_sold.append(len(count_type))

    return render_template('stats.html', heiskort_type=heiskort_type, heiskort_sold=heiskort_sold)
