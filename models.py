from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    wines = db.relationship('Wine', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    tasting_notes = db.relationship('TastingNote', backref='author', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def cellar_value(self):
        return sum(w.price * w.quantity for w in self.wines.filter_by(status='cellar') if w.price)

    def total_bottles(self):
        return sum(w.quantity for w in self.wines.filter_by(status='cellar'))

    def __repr__(self):
        return f'<User {self.username}>'


class Wine(db.Model):
    __tablename__ = 'wines'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # ── Wine Information ──
    name = db.Column(db.String(200), nullable=False)
    vintage = db.Column(db.Integer)
    producer = db.Column(db.String(200), nullable=False)
    wine_type = db.Column(db.String(30), default='Red')  # Red, White, Rosé, Sparkling, Dessert, Fortified
    appellation = db.Column(db.String(200))
    varietal1 = db.Column(db.String(100))
    varietal2 = db.Column(db.String(100))
    varietal3 = db.Column(db.String(100))
    varietal4 = db.Column(db.String(100))
    size_ml = db.Column(db.Integer, default=750)
    alcohol_pct = db.Column(db.Float)
    description = db.Column(db.Text)

    # ── Acquisition Information ──
    acq_date = db.Column(db.Date)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)
    acq_from = db.Column(db.String(200))       # Where purchased
    on_order = db.Column(db.Boolean, default=False)
    stored = db.Column(db.String(200))          # Cellar location
    acq_description = db.Column(db.Text)        # Acquisition notes

    # ── Internal tracking ──
    # Status: cellar, consumed, wishlist
    status = db.Column(db.String(20), default='cellar')
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_consumed = db.Column(db.Date)

    # Drinking window
    drink_from = db.Column(db.Integer)  # year
    drink_to = db.Column(db.Integer)    # year

    # Rating (1-100 scale)
    rating = db.Column(db.Integer)

    tasting_notes = db.relationship('TastingNote', backref='wine', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def varietals_display(self):
        """Return comma-separated list of varietals."""
        parts = [v for v in [self.varietal1, self.varietal2, self.varietal3, self.varietal4] if v]
        return ', '.join(parts) if parts else ''

    @property
    def is_ready_to_drink(self):
        current_year = date.today().year
        if self.drink_from and self.drink_to:
            return self.drink_from <= current_year <= self.drink_to
        if self.drink_from:
            return current_year >= self.drink_from
        return True

    @property
    def drinking_window_display(self):
        if self.drink_from and self.drink_to:
            return f"{self.drink_from} - {self.drink_to}"
        if self.drink_from:
            return f"From {self.drink_from}"
        if self.drink_to:
            return f"Until {self.drink_to}"
        return "Anytime"

    @property
    def size_display(self):
        if not self.size_ml:
            return ''
        if self.size_ml >= 1000:
            return f"{self.size_ml / 1000:.1f}L"
        return f"{self.size_ml}ml"

    @property
    def maturity_display(self):
        """Return maturity text matching ManageYourCellar format."""
        current_year = date.today().year
        if not self.drink_from and not self.drink_to:
            return ''
        if self.drink_to and current_year > self.drink_to:
            return 'Mature'
        if self.drink_from and self.drink_to:
            if current_year < self.drink_from:
                return 'Hold'
            elif current_year >= self.drink_from and current_year <= self.drink_to:
                mid = (self.drink_from + self.drink_to) / 2
                if current_year < mid:
                    return 'Hold/Drink'
                else:
                    return 'Drink'
            else:
                return 'Drink/Mature'
        if self.drink_from:
            if current_year < self.drink_from:
                return 'Hold'
            elif current_year >= self.drink_from:
                return 'Drink'
        if self.drink_to:
            if current_year <= self.drink_to:
                return 'Drink'
            else:
                return 'Mature'
        return ''

    @property
    def rating_text(self):
        """Convert numeric rating to text matching ManageYourCellar format."""
        if not self.rating:
            return 'n/a'
        if self.rating >= 96:
            return 'Outstanding'
        elif self.rating >= 90:
            return 'Excellent'
        elif self.rating >= 85:
            return 'Very Good'
        elif self.rating >= 80:
            return 'Good/Very Good'
        elif self.rating >= 75:
            return 'Good'
        elif self.rating >= 70:
            return 'Fair'
        else:
            return 'Poor'

    @property
    def name_display(self):
        """Return name in ManageYourCellar format: vintage\\nName (size)"""
        parts = []
        if self.vintage:
            parts.append(str(self.vintage))
        name_with_size = self.name
        if self.size_ml:
            name_with_size += f' ({self.size_ml}ml)'
        parts.append(name_with_size)
        return parts

    @property
    def has_rating(self):
        return self.rating is not None

    def __repr__(self):
        return f'<Wine {self.vintage} {self.name}>'


class TastingNote(db.Model):
    __tablename__ = 'tasting_notes'

    id = db.Column(db.Integer, primary_key=True)
    wine_id = db.Column(db.Integer, db.ForeignKey('wines.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    tasting_date = db.Column(db.Date, default=date.today)
    appearance = db.Column(db.String(200))
    nose = db.Column(db.Text)
    palate = db.Column(db.Text)
    finish = db.Column(db.Text)
    overall = db.Column(db.Text)
    score = db.Column(db.Integer)  # 1-100
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TastingNote {self.wine_id} by {self.user_id}>'
