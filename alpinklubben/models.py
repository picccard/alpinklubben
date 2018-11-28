from alpinklubben import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Sette fremmednøkklene til sammensatt primærnøkkel
class SoldHeiskort(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)  # dag, uke, sesong
    heiskort_id = db.Column(db.Integer, db.ForeignKey(
        'heiskort.id'), nullable=False)  # adult or child
    fromdate = db.Column(db.String(20), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Heiskort(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # dag, uke, sesong
    age = db.Column(db.String(20), nullable=False)  # voksen, barn
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(120), nullable=False, default='skiheis.jpg')

    def __repr__(self):
        return f"Heiskort('{self.type}', '{self.age}', '{self.price}')"


class Skipakke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    desc = db.Column(db.String(20), nullable=False)
    hour_price = db.Column(db.Integer, nullable=False)
    day_price = db.Column(db.Integer, nullable=False)
    week_price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(120), nullable=False, default='skipakke.jpg')


class SoldSkipakke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)
    skipakke_id = db.Column(db.Integer, db.ForeignKey(
        'skipakke.id'), nullable=False)
    fromdate = db.Column(db.String(20), nullable=False)
    rent_type = db.Column(db.String(120), nullable=False)
    rent_length = db.Column(db.String(120), nullable=False)
    price_paid = db.Column(db.Integer, nullable=False)
