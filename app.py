import os
from datetime import date, datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Wine, TastingNote
from flask_wtf.csrf import generate_csrf
from forms import LoginForm, RegisterForm, WineForm, TastingNoteForm, SearchForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'wine-cellar-dev-secret-key-2026')

# Use /tmp for writable DB on Render (ephemeral), or local instance/ for dev
if os.environ.get('RENDER'):
    db_path = '/tmp/winecellar.db'
else:
    db_path = os.path.join(app.instance_path, 'winecellar.db')
    os.makedirs(app.instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Public Routes ────────────────────────────────────────────────

@app.route('/')
def home():
    recent_wines = Wine.query.order_by(Wine.date_added.desc()).limit(5).all()
    return render_template('home.html', recent_wines=recent_wines)


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/best-values')
@login_required
def best_values():
    wines = current_user.wines.filter_by(status='cellar').filter(
        Wine.price.isnot(None), Wine.rating.isnot(None)
    ).all()
    # Sort by value score: rating / price (higher = better value)
    wines_with_value = [(w, w.rating / w.price if w.price > 0 else 0) for w in wines]
    wines_with_value.sort(key=lambda x: x[1], reverse=True)
    return render_template('best_values.html', wines_with_value=wines_with_value[:20])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('cellar'))
    form = LoginForm()

    # Handle both WTForms login AND the inline home-page login form
    if request.method == 'POST':
        username = form.username.data or request.form.get('username', '')
        password = form.password.data or request.form.get('password', '')
        if username and password:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Welcome back!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('cellar'))
            flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('cellar'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created! Welcome to your wine cellar.', 'success')
        return redirect(url_for('cellar'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


# ─── Cellar Routes ────────────────────────────────────────────────

@app.route('/cellar')
@login_required
def cellar():
    status = request.args.get('status', 'cellar')
    search_form = SearchForm(request.args)

    # For on_order view, show cellar wines where on_order=True
    if status == 'on_order':
        query = current_user.wines.filter_by(status='cellar', on_order=True)
    else:
        query = current_user.wines.filter_by(status=status)

    # Apply search filters
    if search_form.query.data:
        search_term = f"%{search_form.query.data}%"
        query = query.filter(
            db.or_(
                Wine.name.ilike(search_term),
                Wine.producer.ilike(search_term),
                Wine.varietal1.ilike(search_term),
                Wine.varietal2.ilike(search_term),
                Wine.varietal3.ilike(search_term),
                Wine.varietal4.ilike(search_term),
                Wine.appellation.ilike(search_term),
                Wine.acq_from.ilike(search_term)
            )
        )
    if search_form.wine_type.data:
        query = query.filter_by(wine_type=search_form.wine_type.data)
    if search_form.appellation.data:
        query = query.filter(Wine.appellation.ilike(f"%{search_form.appellation.data}%"))
    if search_form.varietal.data:
        vterm = f"%{search_form.varietal.data}%"
        query = query.filter(
            db.or_(
                Wine.varietal1.ilike(vterm),
                Wine.varietal2.ilike(vterm),
                Wine.varietal3.ilike(vterm),
                Wine.varietal4.ilike(vterm)
            )
        )
    if search_form.min_vintage.data:
        query = query.filter(Wine.vintage >= search_form.min_vintage.data)
    if search_form.max_vintage.data:
        query = query.filter(Wine.vintage <= search_form.max_vintage.data)

    # Sorting
    sort_by = search_form.sort_by.data or 'name'
    sort_map = {
        'name': Wine.name,
        'vintage': Wine.vintage.desc(),
        'producer': Wine.producer,
        'rating': Wine.rating.desc(),
        'price': Wine.price.desc(),
        'date_added': Wine.date_added.desc(),
    }
    query = query.order_by(sort_map.get(sort_by, Wine.name))

    wines = query.all()

    status_labels = {
        'cellar': 'Wines in Cellar',
        'consumed': 'Wines Consumed',
        'on_order': 'Wines on Order',
        'wishlist': 'Wish List'
    }

    return render_template('cellar.html',
                           wines=wines,
                           status=status,
                           status_label=status_labels.get(status, 'Wines in Cellar'),
                           search_form=search_form,
                           current_year=date.today().year)


@app.route('/cellar/ready')
@login_required
def ready_to_drink():
    current_year = date.today().year
    wines = current_user.wines.filter_by(status='cellar').filter(
        Wine.drink_from <= current_year,
        db.or_(Wine.drink_to >= current_year, Wine.drink_to.is_(None))
    ).order_by(Wine.drink_to.asc()).all()
    return render_template('ready.html', wines=wines, current_year=current_year)


# ─── Wine CRUD ────────────────────────────────────────────────────

@app.route('/wine/add', methods=['GET', 'POST'])
@login_required
def add_wine():
    form = WineForm()
    if form.validate_on_submit():
        wine = Wine(user_id=current_user.id)
        form.populate_obj(wine)
        db.session.add(wine)
        db.session.commit()
        flash(f'"{wine.name}" added to your cellar!', 'success')
        return redirect(url_for('cellar', status=wine.status))
    return render_template('wine_form.html', form=form, title='Add Wine')


@app.route('/wine/<int:wine_id>')
@login_required
def wine_detail(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    if wine.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('cellar'))
    tasting_notes = wine.tasting_notes.order_by(TastingNote.tasting_date.desc()).all()
    return render_template('wine_detail.html', wine=wine, tasting_notes=tasting_notes)


@app.route('/wine/<int:wine_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_wine(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    if wine.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('cellar'))
    form = WineForm(obj=wine)
    if form.validate_on_submit():
        form.populate_obj(wine)
        db.session.commit()
        flash(f'"{wine.name}" updated.', 'success')
        return redirect(url_for('wine_detail', wine_id=wine.id))
    return render_template('wine_form.html', form=form, title='Edit Wine', wine=wine)


@app.route('/wine/<int:wine_id>/delete', methods=['POST'])
@login_required
def delete_wine(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    if wine.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('cellar'))
    name = wine.name
    db.session.delete(wine)
    db.session.commit()
    flash(f'"{name}" removed.', 'success')
    return redirect(url_for('cellar'))


@app.route('/wine/<int:wine_id>/consume', methods=['POST'])
@login_required
def consume_wine(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    if wine.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('cellar'))
    if wine.quantity > 1:
        wine.quantity -= 1
        # Create a consumed copy
        consumed = Wine(
            user_id=current_user.id,
            name=wine.name, producer=wine.producer, vintage=wine.vintage,
            wine_type=wine.wine_type, appellation=wine.appellation,
            varietal1=wine.varietal1, varietal2=wine.varietal2,
            varietal3=wine.varietal3, varietal4=wine.varietal4,
            size_ml=wine.size_ml, alcohol_pct=wine.alcohol_pct,
            description=wine.description,
            price=wine.price, quantity=1,
            acq_from=wine.acq_from, stored=wine.stored,
            status='consumed', rating=wine.rating,
            date_consumed=date.today(),
            drink_from=wine.drink_from, drink_to=wine.drink_to
        )
        db.session.add(consumed)
    else:
        wine.status = 'consumed'
        wine.date_consumed = date.today()
    db.session.commit()
    flash(f'Enjoyed a bottle of {wine.name}!', 'success')
    return redirect(url_for('cellar'))


# ─── Tasting Notes ────────────────────────────────────────────────

@app.route('/wine/<int:wine_id>/tasting/add', methods=['GET', 'POST'])
@login_required
def add_tasting_note(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    if wine.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('cellar'))
    form = TastingNoteForm()
    if not form.tasting_date.data:
        form.tasting_date.data = date.today()
    if form.validate_on_submit():
        note = TastingNote(wine_id=wine.id, user_id=current_user.id)
        form.populate_obj(note)
        db.session.add(note)
        db.session.commit()
        flash('Tasting note added!', 'success')
        return redirect(url_for('wine_detail', wine_id=wine.id))
    return render_template('tasting_form.html', form=form, wine=wine)


@app.route('/tastings')
@login_required
def tasting_list():
    notes = TastingNote.query.filter_by(user_id=current_user.id)\
        .order_by(TastingNote.tasting_date.desc()).all()
    return render_template('tastings.html', notes=notes)


# ─── Statistics ───────────────────────────────────────────────────

@app.route('/stats')
@login_required
def stats():
    cellar_wines = current_user.wines.filter_by(status='cellar').all()
    consumed_wines = current_user.wines.filter_by(status='consumed').all()

    total_bottles = sum(w.quantity for w in cellar_wines)
    total_value = sum((w.price or 0) * w.quantity for w in cellar_wines)
    avg_price = total_value / total_bottles if total_bottles > 0 else 0

    # By type
    type_breakdown = {}
    for w in cellar_wines:
        type_breakdown[w.wine_type] = type_breakdown.get(w.wine_type, 0) + w.quantity

    # By appellation
    appellation_breakdown = {}
    for w in cellar_wines:
        key = w.appellation or 'Unknown'
        appellation_breakdown[key] = appellation_breakdown.get(key, 0) + w.quantity

    # By varietal (use varietal1 as primary)
    varietal_breakdown = {}
    for w in cellar_wines:
        key = w.varietal1 or 'Unknown'
        varietal_breakdown[key] = varietal_breakdown.get(key, 0) + w.quantity

    # Top rated
    top_rated = sorted([w for w in cellar_wines if w.rating], key=lambda w: w.rating, reverse=True)[:10]

    # Ready to drink count
    current_year = date.today().year
    ready_count = sum(1 for w in cellar_wines if w.is_ready_to_drink)

    # Sort breakdowns by count
    type_breakdown = dict(sorted(type_breakdown.items(), key=lambda x: x[1], reverse=True))
    appellation_breakdown = dict(sorted(appellation_breakdown.items(), key=lambda x: x[1], reverse=True))
    varietal_breakdown = dict(sorted(varietal_breakdown.items(), key=lambda x: x[1], reverse=True))

    return render_template('stats.html',
                           total_bottles=total_bottles,
                           total_value=total_value,
                           avg_price=avg_price,
                           consumed_count=len(consumed_wines),
                           type_breakdown=type_breakdown,
                           appellation_breakdown=appellation_breakdown,
                           varietal_breakdown=varietal_breakdown,
                           top_rated=top_rated,
                           ready_count=ready_count)


# ─── Search ───────────────────────────────────────────────────────

@app.route('/search')
@login_required
def search():
    form = SearchForm(request.args)
    wines = []
    if any([form.query.data, form.wine_type.data, form.appellation.data, form.varietal.data]):
        query = current_user.wines
        if form.query.data:
            search_term = f"%{form.query.data}%"
            query = query.filter(
                db.or_(
                    Wine.name.ilike(search_term),
                    Wine.producer.ilike(search_term),
                    Wine.varietal1.ilike(search_term),
                    Wine.varietal2.ilike(search_term),
                    Wine.appellation.ilike(search_term)
                )
            )
        if form.wine_type.data:
            query = query.filter_by(wine_type=form.wine_type.data)
        if form.appellation.data:
            query = query.filter(Wine.appellation.ilike(f"%{form.appellation.data}%"))
        if form.varietal.data:
            vterm = f"%{form.varietal.data}%"
            query = query.filter(
                db.or_(
                    Wine.varietal1.ilike(vterm),
                    Wine.varietal2.ilike(vterm),
                    Wine.varietal3.ilike(vterm),
                    Wine.varietal4.ilike(vterm)
                )
            )
        wines = query.order_by(Wine.name).all()
    return render_template('search.html', form=form, wines=wines)


# ─── Quick Entry ──────────────────────────────────────────────────

@app.route('/quick-entry', methods=['GET', 'POST'])
@login_required
def quick_entry():
    if request.method == 'POST':
        count = 0
        names = request.form.getlist('name[]')
        producers = request.form.getlist('producer[]')
        vintages = request.form.getlist('vintage[]')
        varietals = request.form.getlist('varietal[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')

        for i in range(len(names)):
            if names[i].strip() and producers[i].strip():
                wine = Wine(
                    user_id=current_user.id,
                    name=names[i].strip(),
                    producer=producers[i].strip(),
                    vintage=int(vintages[i]) if vintages[i] else None,
                    varietal1=varietals[i].strip() if varietals[i] else None,
                    quantity=int(quantities[i]) if quantities[i] else 1,
                    price=float(prices[i]) if prices[i] else None,
                    status='cellar'
                )
                db.session.add(wine)
                count += 1

        db.session.commit()
        flash(f'{count} wine(s) added to your cellar!', 'success')
        return redirect(url_for('cellar'))
    return render_template('quick_entry.html')


# ─── Export ───────────────────────────────────────────────────────

@app.route('/export')
@login_required
def export_cellar():
    import csv
    from io import StringIO
    from flask import Response

    wines = current_user.wines.order_by(Wine.status, Wine.name).all()
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Name', 'Vintage', 'Producer', 'Type', 'Appellation',
                     'Varietal1', 'Varietal2', 'Varietal3', 'Varietal4',
                     'Size (ml)', 'Alcohol %', 'Description',
                     'Acq Date', 'Quantity', 'Price', 'From', 'On Order',
                     'Stored', 'Acq Description', 'Status', 'Rating',
                     'Drink From', 'Drink To'])
    for w in wines:
        writer.writerow([w.name, w.vintage, w.producer, w.wine_type, w.appellation,
                         w.varietal1, w.varietal2, w.varietal3, w.varietal4,
                         w.size_ml, w.alcohol_pct, w.description,
                         w.acq_date, w.quantity, w.price, w.acq_from,
                         'Yes' if w.on_order else 'No',
                         w.stored, w.acq_description, w.status, w.rating,
                         w.drink_from, w.drink_to])

    output = si.getvalue()
    return Response(output, mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment;filename=cellar_export.csv'})


# ─── API Endpoints ────────────────────────────────────────────────

@app.route('/api/wines')
@login_required
def api_wines():
    wines = current_user.wines.filter_by(status='cellar').all()
    return jsonify([{
        'id': w.id, 'name': w.name, 'producer': w.producer,
        'vintage': w.vintage, 'type': w.wine_type,
        'varietal': w.varietals_display, 'rating': w.rating,
        'price': w.price, 'quantity': w.quantity
    } for w in wines])


# ─── Initialize ───────────────────────────────────────────────────

def init_db():
    with app.app_context():
        db.create_all()
        # Auto-seed if DB is empty (handles Render's ephemeral /tmp)
        from models import User
        if not User.query.first():
            try:
                from seed import seed_database
                seed_database()
            except Exception as e:
                print(f"Seed error: {e}")


# Always initialize on import (needed for gunicorn)
init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
