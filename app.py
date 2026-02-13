import os
from datetime import date, datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import func
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
    bottle_count = 0
    wine_count = 0
    latest_transactions = []
    if current_user.is_authenticated:
        cellar_wines = current_user.wines.filter_by(status='cellar').filter(
            db.or_(Wine.on_order == False, Wine.on_order.is_(None))
        ).all()
        bottle_count = sum(w.quantity for w in cellar_wines)
        wine_count = len(cellar_wines)
        latest_transactions = current_user.wines.order_by(Wine.date_added.desc()).limit(5).all()
    return render_template('home.html', recent_wines=recent_wines,
                           bottle_count=bottle_count, wine_count=wine_count,
                           latest_transactions=latest_transactions)


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
    # For cellar view, exclude on_order wines (matching original site behavior)
    if status == 'on_order':
        query = current_user.wines.filter_by(status='cellar', on_order=True)
    elif status == 'cellar':
        query = current_user.wines.filter_by(status='cellar').filter(
            db.or_(Wine.on_order == False, Wine.on_order.is_(None))
        )
    else:
        query = current_user.wines.filter_by(status=status)

    # Apply search filters (ignore placeholder text "Wine Finder")
    search_query = search_form.query.data
    if search_query and search_query.strip().lower() == 'wine finder':
        search_query = None
    if search_query:
        search_term = f"%{search_query}%"
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

    # Sorting - default by name, case-insensitive to match original site
    sort_by = search_form.sort_by.data or 'name'
    sort_order = search_form.sort_order.data or 'asc'
    sort_col_map = {
        'name': func.lower(Wine.name),
        'vintage': Wine.vintage,
        'producer': func.lower(Wine.producer),
        'appellation': func.lower(Wine.appellation),
        'varietal': func.lower(Wine.varietal1),
        'wine_type': Wine.wine_type,
        'rating': Wine.rating,
        'price': Wine.price,
        'date_added': Wine.date_added,
    }
    sort_col = sort_col_map.get(sort_by, func.lower(Wine.name))
    if sort_order == 'desc':
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    # Get all wines first, then paginate in Python (simpler, avoids double query)
    all_wines = query.all()
    total_wines = len(all_wines)
    total_bottles = sum(w.quantity for w in all_wines)

    # Pagination: 50 per page (matching original), "All" shows everything
    submit_action = request.args.get('submitAction', '')
    page = int(request.args.get('page', 1))
    limit = 50
    show_all = (submit_action == 'All' or request.args.get('show_all') == '1')

    if submit_action == 'Next':
        page = page + 1
    elif submit_action == 'Previous':
        page = max(1, page - 1)
    elif submit_action == 'Search':
        page = 1  # Reset to page 1 on new search

    total_pages = max(1, (total_wines + limit - 1) // limit)
    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1

    if show_all:
        wines = all_wines
    else:
        start = (page - 1) * limit
        wines = all_wines[start:start + limit]

    # Build varietal list from user's wines for the filter dropdown
    varietal_set = set()
    for w in current_user.wines.all():
        for v in [w.varietal1, w.varietal2, w.varietal3, w.varietal4]:
            if v:
                varietal_set.add(v)
    varietals = sorted(varietal_set)

    status_labels = {
        'cellar': f"Wines in {current_user.username}'s Cellar",
        'consumed': 'Consumed Wines',
        'on_order': 'Wines on Order',
        'wishlist': 'Wish List'
    }

    return render_template('cellar.html',
                           wines=wines,
                           status=status,
                           status_label=status_labels.get(status, 'Wines in Cellar'),
                           search_form=search_form,
                           varietals=varietals,
                           current_year=date.today().year,
                           page=page,
                           total_pages=total_pages,
                           total_wines=total_wines,
                           total_bottles=total_bottles,
                           show_all=show_all)


@app.route('/cellar/ready')
@login_required
def ready_to_drink():
    current_year = date.today().year
    all_wines = current_user.wines.filter_by(status='cellar').filter(
        Wine.drink_from <= current_year,
        db.or_(Wine.drink_to >= current_year, Wine.drink_to.is_(None))
    ).order_by(func.lower(Wine.name).asc()).all()

    total_wines = len(all_wines)
    total_bottles = sum(w.quantity for w in all_wines)

    # Pagination
    submit_action = request.args.get('submitAction', '')
    page = int(request.args.get('page', 1))
    limit = 50
    show_all = (submit_action == 'All' or request.args.get('show_all') == '1')

    if submit_action == 'Next':
        page = page + 1
    elif submit_action == 'Previous':
        page = max(1, page - 1)

    total_pages = max(1, (total_wines + limit - 1) // limit)
    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1

    if show_all:
        wines = all_wines
    else:
        start = (page - 1) * limit
        wines = all_wines[start:start + limit]

    return render_template('ready.html', wines=wines, current_year=current_year,
                           page=page, total_pages=total_pages,
                           total_wines=total_wines, total_bottles=total_bottles,
                           show_all=show_all)


# ─── Add to Cellar (Acquisition) ──────────────────────────────────

@app.route('/wine/<int:wine_id>/add-to-cellar', methods=['GET', 'POST'])
@login_required
def add_to_cellar(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    if wine.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('cellar'))

    if request.method == 'GET':
        return render_template('add_to_cellar_form.html', wine=wine, today=date.today())

    # POST: process the acquisition form
    submit_action = request.form.get('submitAction', '')
    if submit_action == 'Cancel':
        return redirect(url_for('wine_detail', wine_id=wine.id))

    # Parse acquisition date
    try:
        year = int(request.form.get('year', date.today().year))
        month = int(request.form.get('month', date.today().month))
        day = int(request.form.get('day', date.today().day))
        acq_date = date(year, month, day)
    except (ValueError, TypeError):
        acq_date = date.today()

    # Parse quantity
    try:
        qty = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        qty = 1
    if qty < 1:
        qty = 1

    # Parse price
    try:
        price = float(request.form.get('price', 0))
    except (ValueError, TypeError):
        price = None

    # Parse other fields
    from_name = request.form.get('otherPartyName', '').strip()
    winery_is_from = request.form.get('wineryIsOtherParty', '')
    if winery_is_from and not from_name:
        from_name = wine.producer
    is_on_order = bool(request.form.get('isOnOrder', ''))
    stored = request.form.get('storingInfo', '').strip()
    alcohol_str = request.form.get('alcohol', '').strip()
    description = request.form.get('description', '').strip()

    # Parse alcohol
    alcohol_pct = None
    if alcohol_str:
        try:
            alcohol_pct = float(alcohol_str)
        except ValueError:
            pass

    # Update the wine record: add bottles to existing quantity
    wine.quantity += qty
    wine.acq_date = acq_date
    if price and price > 0:
        wine.price = price
    if from_name:
        wine.acq_from = from_name
    if is_on_order:
        wine.on_order = True
    if stored:
        wine.stored = stored
    if alcohol_pct is not None:
        wine.alcohol_pct = alcohol_pct
    if description:
        wine.acq_description = description

    # If the wine was consumed or on wishlist, move it back to cellar
    if wine.status != 'cellar':
        wine.status = 'cellar'

    db.session.commit()
    flash(f'Added {qty} bottle(s) of {wine.name} to your cellar!', 'success')
    return redirect(url_for('wine_detail', wine_id=wine.id))


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

    # Get consumption records linked to this wine
    consumed_copies = []
    total_acquired = wine.original_quantity or wine.quantity
    total_consumed = 0
    parent = None

    if wine.status == 'cellar':
        consumed_copies = wine.consumed_copies.order_by(Wine.date_consumed.asc()).all()
        total_consumed = sum(c.quantity for c in consumed_copies)
    elif wine.status == 'consumed' and wine.parent_wine_id:
        # This is a consumed wine - show the parent's transaction data
        parent = Wine.query.get(wine.parent_wine_id)
        if parent:
            total_acquired = parent.original_quantity or parent.quantity
            consumed_copies = parent.consumed_copies.order_by(Wine.date_consumed.asc()).all()
            total_consumed = sum(c.quantity for c in consumed_copies)
    elif wine.status == 'consumed':
        # Standalone consumed wine (fully consumed, no cellar entry)
        total_acquired = wine.quantity
        total_consumed = wine.quantity

    actual_in_cellar = total_acquired - total_consumed if wine.status == 'cellar' else (
        (parent.quantity if parent else 0) if wine.status == 'consumed' and wine.parent_wine_id else 0
    )

    # The "acquisition wine" is the cellar parent (or the wine itself if cellar)
    acq_wine = parent if parent else wine

    # Find related wines: other wines by same producer in user's cellar
    related_wines = Wine.query.filter(
        Wine.user_id == current_user.id,
        Wine.producer == wine.producer,
        Wine.id != wine.id,
        Wine.status == 'cellar'
    ).limit(5).all()

    # Gather tasting notes from both the wine and its consumed copies (deduplicated)
    seen_note_ids = set()
    all_tasting_notes = []
    for note in tasting_notes:
        if note.id not in seen_note_ids:
            all_tasting_notes.append(note)
            seen_note_ids.add(note.id)
    for cc in consumed_copies:
        for note in cc.tasting_notes.all():
            if note.id not in seen_note_ids:
                all_tasting_notes.append(note)
                seen_note_ids.add(note.id)
    # Sort by date desc
    all_tasting_notes.sort(key=lambda n: n.tasting_date or datetime.min, reverse=True)

    return render_template('wine_detail.html', wine=wine, tasting_notes=all_tasting_notes,
                           consumed_copies=consumed_copies,
                           total_acquired=total_acquired,
                           total_consumed=total_consumed,
                           actual_in_cellar=actual_in_cellar,
                           parent_wine=parent,
                           acq_wine=acq_wine,
                           related_wines=related_wines)


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


@app.route('/wine/<int:wine_id>/consume', methods=['GET', 'POST'])
@login_required
def consume_wine(wine_id):
    wine = Wine.query.get_or_404(wine_id)
    if wine.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('cellar'))

    if request.method == 'GET':
        # Show the Remove from Cellar form (matching original site's flow)
        return render_template('consume_form.html', wine=wine, today=date.today())

    # POST: process the consumption form
    submit_action = request.form.get('submitAction', '')
    if submit_action == 'Cancel':
        return redirect(url_for('wine_detail', wine_id=wine.id))

    # Parse consumption date
    try:
        year = int(request.form.get('year', date.today().year))
        month = int(request.form.get('month', date.today().month))
        day = int(request.form.get('day', date.today().day))
        consume_date = date(year, month, day)
    except (ValueError, TypeError):
        consume_date = date.today()

    # Parse quantity
    try:
        qty = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        qty = 1
    qty = min(qty, wine.quantity)  # Can't consume more than available

    # Build tasting note description from form fields
    note_parts = []
    occasion = request.form.get('occasion', '').strip()
    meal = request.form.get('meal', '').strip()
    participants = request.form.get('participants', '').strip()
    food_pairing = request.form.get('foodPairing', '').strip()
    description = request.form.get('description', '').strip()

    if occasion:
        note_parts.append(f'Occasion: {occasion}')
    if meal:
        note_parts.append(f'Meal: {meal}')
    if participants:
        note_parts.append(f'Participants: {participants}')
    if food_pairing:
        note_parts.append(f'Food Pairing: {food_pairing}')
    if description:
        note_parts.append(description)

    # Parse tasting descriptors
    color_map = {
        '0': 'dark', '1': 'deep', '2': 'bright', '3': 'pale', '4': 'evolved', '5': 'cloudy'
    }
    nose_map = {
        '0': 'intense', '1': 'complex', '2': 'fragrant', '3': 'discreet', '4': 'closed', '5': 'corky'
    }
    aroma_map = {
        '0': 'mineral', '1': 'buttery', '2': 'nutty', '3': 'floral', '4': 'herbal',
        '5': 'spicy', '6': 'woody', '7': 'sweet', '8': 'citrus fruit', '9': 'tropical fruit',
        '10': 'tree fruit', '11': 'red berry', '12': 'black berry', '13': 'dried fruit'
    }
    acidity_map = {'0': 'green', '1': 'crisp', '2': 'lively', '3': 'supple', '4': 'flat'}
    sweetness_map = {'0': 'dry', '1': 'medium dry', '2': 'sweet'}
    body_map = {
        '0': 'tannic', '1': 'alcoholic', '2': 'full-bodied', '3': 'firm',
        '4': 'medium-bodied', '5': 'light-bodied', '6': 'thin'
    }
    finish_map = {'0': 'short', '1': 'medium', '2': 'persistent', '3': 'very persistent'}
    overall_map = {
        '0': 'well balanced', '1': 'elegant', '2': 'rich', '3': 'bold',
        '8': 'pleasant', '4': 'easy', '5': 'weak', '7': 'slightly unbalanced', '6': 'unbalanced'
    }

    appearance = color_map.get(request.form.get('color', ''), '')
    nose_val = nose_map.get(request.form.get('nose', ''), '')
    aromas = request.form.getlist('multipleAromas')
    aroma_text = ', '.join(aroma_map.get(a, '') for a in aromas if a and a in aroma_map)
    nose_text = '; '.join(filter(None, [nose_val, aroma_text]))

    acidity = acidity_map.get(request.form.get('acidity', ''), '')
    sweetness = sweetness_map.get(request.form.get('sweetness', ''), '')
    body = body_map.get(request.form.get('body', ''), '')
    finish = finish_map.get(request.form.get('finish', ''), '')
    palate_text = '; '.join(filter(None, [acidity, sweetness, body, finish]))

    overall_impression = overall_map.get(request.form.get('overall', ''), '')

    # Parse rating
    score = None
    star_rating = request.form.get('starRating', '')
    point_rating = request.form.get('pointRating', '').strip()
    if point_rating:
        try:
            score = int(float(point_rating))
        except ValueError:
            pass
    elif star_rating:
        # Convert star rating to 100-point scale
        import re
        star_match = re.match(r'([\d.]+)\s*stars?', star_rating)
        if star_match:
            score = int(float(star_match.group(1)) * 20)

    # Parse drinking window
    from_year = request.form.get('fromYear', '').strip()
    to_year = request.form.get('toYear', '').strip()
    drink_now = request.form.get('drinkNow', '')

    # Create consumed wine copy / update original
    if wine.quantity > qty:
        wine.quantity -= qty
        # Create a consumed copy
        consumed = Wine(
            user_id=current_user.id,
            name=wine.name, producer=wine.producer, vintage=wine.vintage,
            wine_type=wine.wine_type, appellation=wine.appellation,
            varietal1=wine.varietal1, varietal2=wine.varietal2,
            varietal3=wine.varietal3, varietal4=wine.varietal4,
            size_ml=wine.size_ml, alcohol_pct=wine.alcohol_pct,
            description=wine.description,
            price=wine.price, quantity=qty,
            acq_from=wine.acq_from, stored=wine.stored,
            status='consumed', rating=score if score else wine.rating,
            date_consumed=consume_date,
            drink_from=int(from_year) if from_year else wine.drink_from,
            drink_to=int(to_year) if to_year else wine.drink_to,
            parent_wine_id=wine.id
        )
        db.session.add(consumed)
        db.session.flush()
        consumed_wine_id = consumed.id
    else:
        wine.status = 'consumed'
        wine.date_consumed = consume_date
        wine.quantity = qty
        if score:
            wine.rating = score
        if from_year:
            wine.drink_from = int(from_year)
        if to_year:
            wine.drink_to = int(to_year)
        consumed_wine_id = wine.id

    # Create tasting note if any tasting data was provided
    overall_text = '; '.join(filter(None, [overall_impression] + note_parts))
    if any([appearance, nose_text, palate_text, overall_text, score]):
        note = TastingNote(
            wine_id=consumed_wine_id,
            user_id=current_user.id,
            tasting_date=consume_date,
            appearance=appearance or None,
            nose=nose_text or None,
            palate=palate_text or None,
            overall=overall_text or None,
            score=score
        )
        db.session.add(note)

    db.session.commit()
    flash(f'Enjoyed a bottle of {wine.name}!', 'success')
    return redirect(url_for('wine_detail', wine_id=wine_id))


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
    cellar_wines = current_user.wines.filter_by(status='cellar').filter(
        db.or_(Wine.on_order == False, Wine.on_order.is_(None))
    ).all()
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


# ─── Cellar Import ────────────────────────────────────────────

@app.route('/import', methods=['GET', 'POST'])
@login_required
def cellar_import():
    if request.method == 'POST':
        import csv
        from io import StringIO, TextIOWrapper

        file = request.files.get('csv_file')
        if not file or not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'danger')
            return redirect(url_for('cellar_import'))

        try:
            content = file.stream.read().decode('utf-8-sig')
            reader = csv.reader(StringIO(content))

            # Find the header row
            header = None
            for row in reader:
                cleaned = [c.strip() for c in row]
                if 'Name' in cleaned and 'Producer' in cleaned:
                    header = cleaned
                    break

            if not header:
                flash('Could not find header row with Name and Producer columns.', 'danger')
                return redirect(url_for('cellar_import'))

            # Map column indices
            col = {}
            for i, h in enumerate(header):
                col[h.lower()] = i

            wine_count = 0
            note_count = 0

            # Track wines we create so we can attach tasting notes to consumed copies
            wine_cache = {}  # key: (vintage, name, producer) -> wine_id

            for row in reader:
                if len(row) < len(header):
                    row.extend([''] * (len(header) - len(row)))

                name = row[col.get('name', 1)].strip() if col.get('name') is not None else ''
                producer = row[col.get('producer', 2)].strip() if col.get('producer') is not None else ''
                if not name or not producer:
                    continue

                vintage_str = row[col.get('vintage', 0)].strip() if col.get('vintage') is not None else ''
                appellation = row[col.get('appellation', 3)].strip() if col.get('appellation') is not None else ''
                varietal_str = row[col.get('varietal', 4)].strip() if col.get('varietal') is not None else ''
                size_str = row[col.get('size', 5)].strip() if col.get('size') is not None else ''
                qty_str = row[col.get('quantity', 6)].strip() if col.get('quantity') is not None else ''
                price_str = row[col.get('price', 7)].strip() if col.get('price') is not None else ''
                stored = row[col.get('stored', 8)].strip() if col.get('stored') is not None else ''
                notes = row[col.get('notes', 9)].strip() if col.get('notes') is not None else ''

                vintage = None
                if vintage_str:
                    try:
                        vintage = int(vintage_str)
                    except ValueError:
                        pass

                # Parse varietals (split by hyphen)
                varietals = [v.strip() for v in varietal_str.split('-') if v.strip()] if varietal_str else []

                size_ml = 750
                if size_str:
                    try:
                        size_ml = int(size_str)
                    except ValueError:
                        pass

                price = None
                if price_str:
                    try:
                        price = float(price_str)
                    except ValueError:
                        pass

                # Determine wine type from varietals
                white_grapes = {'Chardonnay', 'Sauvignon Blanc', 'Pinot Grigio', 'Pinot Gris',
                                'Riesling', 'Gewürztraminer', 'Viognier', 'Sémillon', 'Aligoté',
                                'Pinot Blanc', 'Chenin Blanc', 'Muscat', 'Grenache Blanc',
                                'Roussanne', 'Marsanne', 'Falanghina', 'Prosecco', 'Xarel-Lo',
                                'Macabeo', 'Parellada', 'Grenache Gris', 'Vermentino'}
                sparkling_keywords = {'Champagne', 'Brut', 'Sparkling', 'Prosecco', 'Franciacorta'}
                dessert_keywords = {'Sauternes', 'Barsac'}

                wine_type = 'Red'
                if any(kw.lower() in name.lower() for kw in sparkling_keywords):
                    wine_type = 'Sparkling'
                elif any(kw.lower() in appellation.lower() for kw in dessert_keywords):
                    wine_type = 'Dessert'
                elif varietals and all(v in white_grapes for v in varietals):
                    wine_type = 'White'
                elif 'Rosé' in name or 'Rose' in name:
                    wine_type = 'Rosé'

                cache_key = (vintage, name, producer)

                if qty_str:
                    # This is a cellar entry
                    quantity = int(qty_str) if qty_str else 1

                    wine = Wine(
                        user_id=current_user.id,
                        name=name,
                        producer=producer,
                        vintage=vintage,
                        appellation=appellation,
                        wine_type=wine_type,
                        varietal1=varietals[0] if len(varietals) > 0 else None,
                        varietal2=varietals[1] if len(varietals) > 1 else None,
                        varietal3=varietals[2] if len(varietals) > 2 else None,
                        varietal4=varietals[3] if len(varietals) > 3 else None,
                        size_ml=size_ml,
                        quantity=quantity,
                        price=price,
                        stored=stored,
                        description=notes if notes and 'Brad & Erica Sklar' not in notes else None,
                        status='cellar'
                    )
                    db.session.add(wine)
                    db.session.flush()
                    wine_cache[cache_key] = wine.id
                    wine_count += 1

                    # If there are tasting notes in the notes field for cellar wines
                    if notes and 'Brad & Erica Sklar' in notes:
                        _create_tasting_note(wine.id, current_user.id, notes)
                        note_count += 1

                elif notes:
                    # This is a consumed entry with tasting notes
                    # Find or create a consumed wine entry
                    wine_id = wine_cache.get(cache_key)
                    if not wine_id:
                        # Create consumed wine
                        wine = Wine(
                            user_id=current_user.id,
                            name=name,
                            producer=producer,
                            vintage=vintage,
                            appellation=appellation,
                            wine_type=wine_type,
                            varietal1=varietals[0] if len(varietals) > 0 else None,
                            varietal2=varietals[1] if len(varietals) > 1 else None,
                            varietal3=varietals[2] if len(varietals) > 2 else None,
                            varietal4=varietals[3] if len(varietals) > 3 else None,
                            size_ml=size_ml,
                            price=price,
                            stored=stored,
                            quantity=1,
                            status='consumed'
                        )
                        db.session.add(wine)
                        db.session.flush()
                        wine_cache[cache_key] = wine.id
                        wine_id = wine.id
                        wine_count += 1

                    _create_tasting_note(wine_id, current_user.id, notes)
                    note_count += 1

            db.session.commit()
            flash(f'Import complete: {wine_count} wines and {note_count} tasting notes imported!', 'success')
            return redirect(url_for('cellar'))

        except Exception as e:
            db.session.rollback()
            flash(f'Import error: {str(e)}', 'danger')
            return redirect(url_for('cellar_import'))

    return render_template('cellar_import.html')


def _create_tasting_note(wine_id, user_id, notes_text):
    """Parse tasting note text from ManageYourCellar CSV format and create a TastingNote."""
    import re

    # Parse "Brad & Erica Sklar: X stars  occasion description details"
    # or "Brad & Erica Sklar: X points  description"
    score = None
    overall = notes_text

    # Extract star rating
    star_match = re.search(r'(\d+(?:\.\d+)?)\s*stars?', notes_text)
    if star_match:
        stars = float(star_match.group(1))
        score = int(stars * 20)  # Convert 5-star to 100 scale

    # Extract point rating
    point_match = re.search(r'(\d+)\s*points?', notes_text)
    if point_match:
        score = int(point_match.group(1))

    # Clean up the text - remove the author prefix
    overall = re.sub(r'^\s*Brad\s*&\s*Erica\s*Sklar:\s*', '', overall)
    overall = re.sub(r'^\d+(?:\.\d+)?\s*(?:stars?|points?)\s*', '', overall)
    overall = overall.strip()

    # Try to parse out tasting descriptors
    appearance = None
    nose = None
    palate = None

    # Look for common tasting words
    descriptors = {
        'pale': 'appearance', 'bright': 'appearance', 'deep': 'appearance',
        'dark': 'appearance', 'evolved': 'appearance',
        'fragrant': 'nose', 'floral': 'nose', 'complex': 'nose',
        'intense': 'nose', 'discreet': 'nose', 'nutty': 'nose',
        'supple': 'palate', 'crisp': 'palate', 'lively': 'palate',
        'tannic': 'palate', 'flat': 'palate', 'woody': 'palate',
        'light-bodied': 'palate', 'medium-bodied': 'palate',
        'full-bodied': 'palate', 'alcoholic': 'palate',
    }

    appearance_words = []
    nose_words = []
    palate_words = []

    for word in overall.lower().split():
        word_clean = word.strip(',.;:')
        if word_clean in descriptors:
            cat = descriptors[word_clean]
            if cat == 'appearance':
                appearance_words.append(word_clean)
            elif cat == 'nose':
                nose_words.append(word_clean)
            elif cat == 'palate':
                palate_words.append(word_clean)

    if appearance_words:
        appearance = ', '.join(appearance_words)
    if nose_words:
        nose = ', '.join(nose_words)
    if palate_words:
        palate = ', '.join(palate_words)

    note = TastingNote(
        wine_id=wine_id,
        user_id=user_id,
        appearance=appearance,
        nose=nose,
        palate=palate,
        overall=overall if overall else None,
        score=score
    )
    db.session.add(note)


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
        # Ensure new columns exist (for SQLite upgrades)
        import sqlite3
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        db_path = db_uri.replace('sqlite:///', '')
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(wines)")
            cols = [row[1] for row in cursor.fetchall()]
            if 'parent_wine_id' not in cols:
                cursor.execute("ALTER TABLE wines ADD COLUMN parent_wine_id INTEGER REFERENCES wines(id)")
            if 'original_quantity' not in cols:
                cursor.execute("ALTER TABLE wines ADD COLUMN original_quantity INTEGER")
            if 'producer_url' not in cols:
                cursor.execute("ALTER TABLE wines ADD COLUMN producer_url VARCHAR(300)")
            if 'maturity_override' not in cols:
                cursor.execute("ALTER TABLE wines ADD COLUMN maturity_override VARCHAR(30)")
            if 'acq_price' not in cols:
                cursor.execute("ALTER TABLE wines ADD COLUMN acq_price FLOAT")
            conn.commit()

            # Tasting notes migration
            cursor.execute("PRAGMA table_info(tasting_notes)")
            tn_cols = [row[1] for row in cursor.fetchall()]
            for col in ['description', 'participants', 'recommended_with']:
                if col not in tn_cols:
                    cursor.execute(f"ALTER TABLE tasting_notes ADD COLUMN {col} TEXT")
            conn.commit()
            conn.close()
        except Exception:
            pass
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
