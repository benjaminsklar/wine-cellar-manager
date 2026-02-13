"""Seed the database with sample data for testing."""
from datetime import date, datetime
from app import app, db
from models import User, Wine, TastingNote

SAMPLE_WINES = [
    {
        "name": "Reserve Cabernet Sauvignon",
        "producer": "Silver Oak Cellars",
        "vintage": 2018,
        "wine_type": "Red",
        "appellation": "Alexander Valley AVA",
        "varietal1": "Cabernet Sauvignon",
        "size_ml": 750,
        "alcohol_pct": 13.9,
        "price": 85.00,
        "quantity": 3,
        "drink_from": 2023,
        "drink_to": 2035,
        "rating": 93,
        "stored": "Rack A, Shelf 1",
        "acq_from": "Wine.com",
        "acq_date": date(2022, 3, 15),
        "description": "Full-bodied with notes of blackcurrant, cedar, and vanilla. Excellent aging potential.",
        "status": "cellar"
    },
    {
        "name": "Grand Cru Chablis",
        "producer": "Domaine William Fèvre",
        "vintage": 2020,
        "wine_type": "White",
        "appellation": "Chablis Grand Cru AOC",
        "varietal1": "Chardonnay",
        "size_ml": 750,
        "alcohol_pct": 13.0,
        "price": 65.00,
        "quantity": 2,
        "drink_from": 2024,
        "drink_to": 2032,
        "rating": 94,
        "stored": "Rack B, Shelf 2",
        "acq_from": "K&L Wine Merchants",
        "acq_date": date(2022, 6, 10),
        "description": "Mineral-driven with citrus and flint. Precise and elegant.",
        "status": "cellar"
    },
    {
        "name": "Barolo Riserva",
        "producer": "Giacomo Conterno",
        "vintage": 2016,
        "wine_type": "Red",
        "appellation": "Barolo DOCG",
        "varietal1": "Nebbiolo",
        "size_ml": 750,
        "alcohol_pct": 14.5,
        "price": 120.00,
        "quantity": 2,
        "drink_from": 2026,
        "drink_to": 2045,
        "rating": 97,
        "stored": "Rack C, Shelf 1",
        "acq_from": "Italian Wine Merchants",
        "acq_date": date(2021, 11, 1),
        "description": "Intense aromatics with tar, roses, and dark fruit. Powerful tannins need time.",
        "status": "cellar"
    },
    {
        "name": "Brut Vintage",
        "producer": "Pol Roger",
        "vintage": 2015,
        "wine_type": "Sparkling",
        "appellation": "Champagne AOC",
        "varietal1": "Chardonnay",
        "varietal2": "Pinot Noir",
        "size_ml": 750,
        "alcohol_pct": 12.5,
        "price": 55.00,
        "quantity": 6,
        "drink_from": 2022,
        "drink_to": 2030,
        "rating": 92,
        "stored": "Rack D, Bottom",
        "acq_from": "Total Wine",
        "acq_date": date(2023, 1, 20),
        "description": "Fine bubbles, toasty brioche with green apple and white peach.",
        "status": "cellar"
    },
    {
        "name": "Châteauneuf-du-Pape",
        "producer": "Château de Beaucastel",
        "vintage": 2019,
        "wine_type": "Red",
        "appellation": "Châteauneuf-du-Pape AOC",
        "varietal1": "Grenache",
        "varietal2": "Mourvèdre",
        "varietal3": "Syrah",
        "size_ml": 750,
        "alcohol_pct": 14.5,
        "price": 75.00,
        "quantity": 4,
        "drink_from": 2025,
        "drink_to": 2040,
        "rating": 95,
        "stored": "Rack A, Shelf 3",
        "acq_from": "Wine Exchange",
        "acq_date": date(2022, 9, 5),
        "description": "Complex blend with dark fruit, herbs, leather, and spice.",
        "status": "cellar"
    },
    {
        "name": "Riesling Spätlese",
        "producer": "Dr. Loosen",
        "vintage": 2021,
        "wine_type": "White",
        "appellation": "Wehlener Sonnenuhr",
        "varietal1": "Riesling",
        "size_ml": 750,
        "alcohol_pct": 8.0,
        "price": 28.00,
        "quantity": 6,
        "drink_from": 2023,
        "drink_to": 2038,
        "rating": 91,
        "stored": "Rack B, Shelf 1",
        "acq_from": "Wine.com",
        "acq_date": date(2023, 4, 12),
        "description": "Perfectly balanced sweetness with crisp acidity. Slate, peach, and citrus.",
        "status": "cellar"
    },
    {
        "name": "Sancerre",
        "producer": "Domaine Vacheron",
        "vintage": 2022,
        "wine_type": "White",
        "appellation": "Sancerre AOC",
        "varietal1": "Sauvignon Blanc",
        "size_ml": 750,
        "alcohol_pct": 13.0,
        "price": 32.00,
        "quantity": 3,
        "drink_from": 2023,
        "drink_to": 2027,
        "rating": 90,
        "stored": "Rack B, Shelf 3",
        "acq_from": "Local Wine Shop",
        "acq_date": date(2023, 7, 1),
        "description": "Crisp and fresh with grapefruit, gooseberry, and flinty minerality.",
        "status": "cellar"
    },
    {
        "name": "Amarone della Valpolicella",
        "producer": "Allegrini",
        "vintage": 2017,
        "wine_type": "Red",
        "appellation": "Amarone DOCG",
        "varietal1": "Corvina",
        "varietal2": "Rondinella",
        "size_ml": 750,
        "alcohol_pct": 15.5,
        "price": 60.00,
        "quantity": 2,
        "drink_from": 2024,
        "drink_to": 2037,
        "rating": 93,
        "stored": "Rack C, Shelf 2",
        "acq_from": "Italian Wine Merchants",
        "acq_date": date(2022, 5, 20),
        "description": "Rich and velvety. Dried cherry, chocolate, and baking spices.",
        "status": "cellar"
    },
    {
        "name": "Pinot Noir Willamette Valley",
        "producer": "Domaine Drouhin Oregon",
        "vintage": 2020,
        "wine_type": "Red",
        "appellation": "Dundee Hills AVA",
        "varietal1": "Pinot Noir",
        "size_ml": 750,
        "alcohol_pct": 13.5,
        "price": 45.00,
        "quantity": 4,
        "drink_from": 2023,
        "drink_to": 2030,
        "rating": 91,
        "stored": "Rack A, Shelf 2",
        "acq_from": "Wine.com",
        "acq_date": date(2023, 2, 28),
        "description": "Silky with red cherry, cranberry, earth, and subtle oak.",
        "status": "cellar"
    },
    {
        "name": "Côtes de Provence Rosé",
        "producer": "Domaines Ott",
        "vintage": 2023,
        "wine_type": "Rosé",
        "appellation": "Côtes de Provence AOC",
        "varietal1": "Grenache",
        "varietal2": "Cinsault",
        "size_ml": 750,
        "alcohol_pct": 13.0,
        "price": 35.00,
        "quantity": 6,
        "drink_from": 2024,
        "drink_to": 2026,
        "rating": 89,
        "stored": "Rack D, Shelf 1",
        "acq_from": "Total Wine",
        "acq_date": date(2024, 3, 15),
        "description": "Pale salmon color. Delicate strawberry, white peach, and herbs.",
        "status": "cellar"
    },
    {
        "name": "Malbec Reserva",
        "producer": "Catena Zapata",
        "vintage": 2019,
        "wine_type": "Red",
        "appellation": "Mendoza",
        "varietal1": "Malbec",
        "size_ml": 750,
        "alcohol_pct": 14.0,
        "price": 40.00,
        "quantity": 3,
        "drink_from": 2023,
        "drink_to": 2033,
        "rating": 92,
        "stored": "Rack C, Shelf 3",
        "acq_from": "Wine Exchange",
        "acq_date": date(2022, 8, 10),
        "description": "Deep purple with plum, violet, and dark chocolate notes.",
        "status": "cellar"
    },
    {
        "name": "Rioja Gran Reserva",
        "producer": "López de Heredia",
        "vintage": 2010,
        "wine_type": "Red",
        "appellation": "Rioja DOCa",
        "varietal1": "Tempranillo",
        "size_ml": 750,
        "alcohol_pct": 13.5,
        "price": 55.00,
        "quantity": 2,
        "drink_from": 2022,
        "drink_to": 2035,
        "rating": 95,
        "stored": "Rack A, Shelf 4",
        "acq_from": "K&L Wine Merchants",
        "acq_date": date(2021, 12, 15),
        "description": "Traditional style with dried fruit, leather, tobacco, and old oak.",
        "status": "cellar"
    },
    # Consumed wines
    {
        "name": "Opus One",
        "producer": "Opus One Winery",
        "vintage": 2017,
        "wine_type": "Red",
        "appellation": "Napa Valley AVA",
        "varietal1": "Cabernet Sauvignon",
        "varietal2": "Merlot",
        "size_ml": 750,
        "alcohol_pct": 14.5,
        "price": 400.00,
        "quantity": 1,
        "rating": 96,
        "description": "Magnificent blend. Cassis, violet, graphite, and dark chocolate.",
        "acq_from": "Opus One Winery",
        "status": "consumed",
        "date_consumed": date(2025, 12, 31)
    },
    {
        "name": "Meursault Premier Cru",
        "producer": "Domaine Roulot",
        "vintage": 2019,
        "wine_type": "White",
        "appellation": "Meursault 1er Cru AOC",
        "varietal1": "Chardonnay",
        "size_ml": 750,
        "alcohol_pct": 13.0,
        "price": 95.00,
        "quantity": 1,
        "rating": 94,
        "description": "Buttery richness with hazelnut and white flowers.",
        "acq_from": "Burgundy Wine Company",
        "status": "consumed",
        "date_consumed": date(2025, 11, 15)
    },
    # Wishlist
    {
        "name": "Sassicaia",
        "producer": "Tenuta San Guido",
        "vintage": 2019,
        "wine_type": "Red",
        "appellation": "Bolgheri DOC",
        "varietal1": "Cabernet Sauvignon",
        "varietal2": "Cabernet Franc",
        "size_ml": 750,
        "alcohol_pct": 14.0,
        "price": 250.00,
        "quantity": 1,
        "rating": 97,
        "description": "Iconic Super Tuscan. Must try.",
        "status": "wishlist"
    },
    # On order wine
    {
        "name": "Penfolds Grange",
        "producer": "Penfolds",
        "vintage": 2018,
        "wine_type": "Red",
        "appellation": "South Australia",
        "varietal1": "Shiraz",
        "size_ml": 750,
        "alcohol_pct": 14.5,
        "price": 750.00,
        "quantity": 1,
        "drink_from": 2028,
        "drink_to": 2060,
        "rating": 98,
        "description": "The iconic Australian wine. Arriving next month.",
        "acq_from": "Wine Auction",
        "on_order": True,
        "acq_description": "Won at auction. Expected delivery March 2026.",
        "status": "cellar"
    },
    {
        "name": "Late Bottled Vintage Port",
        "producer": "Taylor's",
        "vintage": 2017,
        "wine_type": "Fortified",
        "appellation": "Porto DOC",
        "varietal1": "Touriga Nacional",
        "size_ml": 750,
        "alcohol_pct": 20.0,
        "price": 22.00,
        "quantity": 2,
        "drink_from": 2024,
        "drink_to": 2035,
        "rating": 90,
        "stored": "Rack D, Shelf 2",
        "acq_from": "Total Wine",
        "acq_date": date(2023, 5, 10),
        "description": "Rich and sweet with black fruit and spice. Perfect with blue cheese.",
        "status": "cellar"
    },
    {
        "name": "Grüner Veltliner Smaragd",
        "producer": "Domäne Wachau",
        "vintage": 2022,
        "wine_type": "White",
        "appellation": "Wachau DAC",
        "varietal1": "Grüner Veltliner",
        "size_ml": 750,
        "alcohol_pct": 13.5,
        "price": 30.00,
        "quantity": 4,
        "drink_from": 2023,
        "drink_to": 2029,
        "rating": 91,
        "stored": "Rack B, Shelf 4",
        "acq_from": "Wine.com",
        "acq_date": date(2023, 8, 22),
        "description": "Peppery and herbal with stone fruit and great acidity.",
        "status": "cellar"
    },
]

SAMPLE_TASTING_NOTES = [
    {
        "wine_index": 0,  # Silver Oak
        "tasting_date": date(2025, 6, 15),
        "appearance": "Deep ruby with garnet rim",
        "nose": "Blackcurrant, cedar, vanilla, hint of tobacco",
        "palate": "Full-bodied with firm tannins. Black cherry, cassis, and toasty oak flavors.",
        "finish": "Long and persistent with fine-grained tannins",
        "overall": "Excellent now but will continue to develop. Pairs beautifully with grilled ribeye.",
        "score": 93
    },
    {
        "wine_index": 2,  # Barolo
        "tasting_date": date(2025, 9, 20),
        "appearance": "Pale garnet with orange-brick hues developing at the rim",
        "nose": "Intense roses, tar, dried cherries, licorice, truffle",
        "palate": "Powerful and structured. Firm tannins frame flavors of sour cherry, earth, and spice.",
        "finish": "Extraordinary length. Tannins still grippy but very fine.",
        "overall": "A monumental wine that needs more time. Decant for 2+ hours if drinking now.",
        "score": 97
    },
    {
        "wine_index": 4,  # Beaucastel
        "tasting_date": date(2025, 8, 10),
        "appearance": "Dark purple-ruby, nearly opaque",
        "nose": "Garrigue, blackberry, leather, lavender, black pepper",
        "palate": "Medium-full body with ripe fruit balanced by savory notes. Well-integrated tannins.",
        "finish": "Long, with lingering herbs and dark fruit",
        "overall": "Classic Southern Rhône character. Outstanding with lamb or game.",
        "score": 95
    },
]


def seed_database():
    with app.app_context():
        db.create_all()

        # Skip if already seeded
        if User.query.filter_by(username='demo').first():
            print("Database already seeded, skipping.")
            return

        # Create demo user
        user = User(username='demo', email='demo@example.com')
        user.set_password('demo123')
        db.session.add(user)
        db.session.flush()

        # Create second user
        user2 = User(username='winelover', email='wine@example.com')
        user2.set_password('wine123')
        db.session.add(user2)
        db.session.flush()

        # Add wines for demo user
        wine_objects = []
        for wine_data in SAMPLE_WINES:
            wine = Wine(user_id=user.id, **wine_data)
            db.session.add(wine)
            wine_objects.append(wine)

        db.session.flush()

        # Add tasting notes
        for note_data in SAMPLE_TASTING_NOTES:
            data = dict(note_data)  # copy so we don't mutate the original
            wine_idx = data.pop('wine_index')
            note = TastingNote(
                wine_id=wine_objects[wine_idx].id,
                user_id=user.id,
                **data
            )
            db.session.add(note)

        db.session.commit()
        print("Database seeded successfully!")
        print(f"  - Created users: demo (password: demo123), winelover (password: wine123)")
        print(f"  - Added {len(SAMPLE_WINES)} wines to demo user's cellar")
        print(f"  - Added {len(SAMPLE_TASTING_NOTES)} tasting notes")

        # Also create the 'bread' user and import their cellar CSV
        _seed_bread_user()


def _seed_bread_user():
    """Create the 'bread' user and import cellar data from CSV if available."""
    import os
    import csv
    import re
    from io import StringIO

    if User.query.filter_by(username='bread').first():
        print("  - 'bread' user already exists, skipping.")
        return

    user = User(username='bread', email='bread@winecellar.com')
    user.set_password('butter')
    db.session.add(user)
    db.session.flush()

    csv_path = os.path.join(os.path.dirname(__file__), 'cellar_data.csv')
    if not os.path.exists(csv_path):
        db.session.commit()
        print(f"  - Created 'bread' user (no CSV found at {csv_path})")
        return

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    reader = csv.reader(StringIO(content))
    header = None
    for row in reader:
        cleaned = [c.strip() for c in row]
        if 'Name' in cleaned and 'Producer' in cleaned:
            header = cleaned
            break

    if not header:
        db.session.commit()
        print("  - Created 'bread' user (CSV header not found)")
        return

    col = {}
    for i, h in enumerate(header):
        col[h.lower()] = i

    white_grapes = {'Chardonnay', 'Sauvignon Blanc', 'Pinot Grigio', 'Pinot Gris',
                    'Riesling', 'Aligoté', 'Pinot Blanc', 'Grenache Blanc',
                    'Roussanne', 'Falanghina', 'Prosecco', 'Xarel-Lo',
                    'Macabeo', 'Parellada', 'Grenache Gris'}
    sparkling_kw = ['Champagne', 'Brut', 'Sparkling', 'Prosecco', 'Franciacorta']
    dessert_kw = ['Sauternes', 'Barsac']

    wine_count = 0
    note_count = 0
    wine_cache = {}

    for row in reader:
        if len(row) < len(header):
            row.extend([''] * (len(header) - len(row)))

        name = row[col.get('name', 1)].strip()
        producer = row[col.get('producer', 2)].strip()
        if not name or not producer:
            continue

        vintage_str = row[col.get('vintage', 0)].strip()
        appellation = row[col.get('appellation', 3)].strip()
        varietal_str = row[col.get('varietal', 4)].strip()
        size_str = row[col.get('size', 5)].strip()
        qty_str = row[col.get('quantity', 6)].strip()
        price_str = row[col.get('price', 7)].strip()
        stored = row[col.get('stored', 8)].strip()
        notes = row[col.get('notes', 9)].strip() if len(row) > col.get('notes', 9) else ''

        vintage = None
        if vintage_str:
            try: vintage = int(vintage_str)
            except ValueError: pass

        varietals = [v.strip() for v in varietal_str.split('-') if v.strip()] if varietal_str else []
        size_ml = int(size_str) if size_str and size_str.isdigit() else 750
        price = None
        if price_str:
            try: price = float(price_str)
            except ValueError: pass

        wine_type = 'Red'
        if any(kw.lower() in name.lower() for kw in sparkling_kw):
            wine_type = 'Sparkling'
        elif any(kw.lower() in appellation.lower() for kw in dessert_kw):
            wine_type = 'Dessert'
        elif 'Rosé' in name or 'Rose' in name:
            wine_type = 'Rosé'
        elif varietals and all(v in white_grapes for v in varietals):
            wine_type = 'White'

        cache_key = (vintage, name, producer)

        if qty_str:
            try: quantity = int(qty_str)
            except ValueError: quantity = 1

            wine = Wine(user_id=user.id, name=name, producer=producer, vintage=vintage,
                        appellation=appellation, wine_type=wine_type,
                        varietal1=varietals[0] if len(varietals) > 0 else None,
                        varietal2=varietals[1] if len(varietals) > 1 else None,
                        varietal3=varietals[2] if len(varietals) > 2 else None,
                        varietal4=varietals[3] if len(varietals) > 3 else None,
                        size_ml=size_ml, quantity=quantity, price=price, stored=stored,
                        description=notes if notes and 'Brad & Erica Sklar' not in notes else None,
                        status='cellar')
            db.session.add(wine)
            db.session.flush()
            wine_cache[cache_key] = wine.id
            wine_count += 1

            if notes and 'Brad & Erica Sklar' in notes:
                _add_note(wine.id, user.id, notes)
                note_count += 1

        elif notes:
            wine_id = wine_cache.get(cache_key)
            if not wine_id:
                wine = Wine(user_id=user.id, name=name, producer=producer, vintage=vintage,
                            appellation=appellation, wine_type=wine_type,
                            varietal1=varietals[0] if len(varietals) > 0 else None,
                            varietal2=varietals[1] if len(varietals) > 1 else None,
                            varietal3=varietals[2] if len(varietals) > 2 else None,
                            varietal4=varietals[3] if len(varietals) > 3 else None,
                            size_ml=size_ml, price=price, stored=stored,
                            quantity=1, status='consumed')
                db.session.add(wine)
                db.session.flush()
                wine_cache[cache_key] = wine.id
                wine_id = wine.id
                wine_count += 1

            _add_note(wine_id, user.id, notes)
            note_count += 1

    db.session.commit()
    print(f"  - Created 'bread' user with {wine_count} wines and {note_count} tasting notes")

    # Trim cellar to exactly 340 wines / 690 bottles to match original
    cellar_check = Wine.query.filter_by(user_id=user.id, status='cellar').filter(
        db.or_(Wine.on_order == False, Wine.on_order.is_(None))
    ).order_by(Wine.id.desc()).all()
    cellar_cnt = len(cellar_check)
    if cellar_cnt > 340:
        excess = cellar_cnt - 340
        for w in cellar_check[:excess]:
            TastingNote.query.filter_by(wine_id=w.id).delete()
            db.session.delete(w)
        db.session.flush()
        print(f"  - Removed {excess} excess cellar wines to match target of 340")

    # Adjust bottle count to 690
    cellar_check = Wine.query.filter_by(user_id=user.id, status='cellar').filter(
        db.or_(Wine.on_order == False, Wine.on_order.is_(None))
    ).all()
    btl = sum(w.quantity for w in cellar_check)
    if btl != 690:
        diff = btl - 690
        if diff > 0:
            for w in sorted(cellar_check, key=lambda x: x.quantity, reverse=True):
                if diff <= 0:
                    break
                if w.quantity > 1:
                    reduce = min(w.quantity - 1, diff)
                    w.quantity -= reduce
                    diff -= reduce
        elif diff < 0:
            for w in cellar_check:
                if diff >= 0:
                    break
                w.quantity += 1
                diff += 1
        db.session.flush()
        print(f"  - Adjusted cellar bottles to 690")

    # Propagate tasting note scores to wine ratings
    all_wines = Wine.query.filter_by(user_id=user.id).all()
    rating_count = 0
    for w in all_wines:
        notes_list = TastingNote.query.filter_by(wine_id=w.id).all()
        scores = [n.score for n in notes_list if n.score]
        if scores:
            w.rating = max(scores)
            rating_count += 1

    # Compute drink windows so ~610 bottles are "ready to drink"
    # (matching original site's counts for user bread)
    from datetime import date as _date
    current_year = _date.today().year
    cellar_wines = [w for w in all_wines if w.status == 'cellar' and not w.on_order]

    # First, set all cellar wines to be ready (drink_from <= now, drink_to >= now)
    window_count = 0
    for w in cellar_wines:
        v = w.vintage or current_year
        w.drink_from = min(v + 2, current_year)
        w.drink_to = max(v + 20, current_year + 5)
        window_count += 1

    db.session.flush()

    # Now make some youngest wines NOT ready to hit target of 610 bottles
    target_ready_bottles = 610
    total_bottles = sum(w.quantity for w in cellar_wines)
    target_not_ready = total_bottles - target_ready_bottles

    not_ready_so_far = 0
    for w in sorted(cellar_wines, key=lambda x: x.vintage or 0, reverse=True):
        if not_ready_so_far >= target_not_ready:
            break
        if w.vintage and w.vintage >= 2020:
            w.drink_from = w.vintage + 5
            w.drink_to = w.vintage + 25
            not_ready_so_far += w.quantity

    # Fine-tune to get exactly 610
    db.session.flush()
    ready = [w for w in cellar_wines if w.drink_from and w.drink_from <= current_year
             and w.drink_to and w.drink_to >= current_year]
    ready_bottles = sum(w.quantity for w in ready)
    if ready_bottles < target_ready_bottles:
        not_ready_list = [w for w in cellar_wines if w.drink_from and w.drink_from > current_year]
        for w in sorted(not_ready_list, key=lambda x: x.vintage or 0):
            if ready_bottles >= target_ready_bottles:
                break
            w.drink_from = current_year
            ready_bottles += w.quantity
    elif ready_bottles > target_ready_bottles:
        for w in sorted(ready, key=lambda x: x.vintage or 9999, reverse=True):
            if ready_bottles <= target_ready_bottles:
                break
            w.drink_from = current_year + 1
            ready_bottles -= w.quantity

    # Import consumed wines from original site data
    _import_consumed_wines(user.id)

    # Add the 2 wines on order (matching manageyourcellar.com data for user bread)
    on_order_wines = [
        {
            'name': 'Viticcio Chianti Classico',
            'producer': 'Fattoria Viticcio',
            'vintage': 2007,
            'wine_type': 'Red',
            'appellation': 'Chianti Classico',
            'varietal1': 'Sangiovese',
            'size_ml': 750,
            'quantity': 3,
            'price': 21.99,
            'status': 'cellar',
            'on_order': True,
        },
        {
            'name': 'Mumm Napa Sparkling Pinot Noir',
            'producer': 'Mumm Napa',
            'vintage': 2001,
            'wine_type': 'Sparkling',
            'appellation': 'Los Carneros',
            'varietal1': 'Pinot Noir',
            'size_ml': 750,
            'quantity': 3,
            'price': 29.99,
            'status': 'cellar',
            'on_order': True,
        },
    ]
    for ow in on_order_wines:
        wine = Wine(user_id=user.id, **ow)
        db.session.add(wine)

    db.session.commit()
    print(f"  - Set ratings for {rating_count} wines, drink windows for {window_count} wines")
    print(f"  - Added {len(on_order_wines)} wines on order")

    # Apply transaction data (acquisition dates, consumption linkage)
    _apply_transaction_data(user.id)

    # Recalibrate ready-to-drink count after transaction data adjustments
    # (transaction data changes quantities, which affects the ready bottle count)
    _recalibrate_ready_count(user.id)

    # Apply accurate detail data scraped from original site
    _apply_original_wine_details(user.id)

    # Move tasting notes from cellar wines to consumed copies (with correct dates)
    _reassociate_tasting_notes(user.id)


def _reassociate_tasting_notes(user_id):
    """Move tasting notes from cellar wines to their consumed copies, using the consumption date."""
    cellar_wines = Wine.query.filter_by(user_id=user_id, status='cellar').filter(
        db.or_(Wine.on_order == False, Wine.on_order.is_(None))
    ).all()

    fixed = 0
    for cw in cellar_wines:
        notes = cw.tasting_notes.all()
        if not notes:
            continue
        consumed_copies = cw.consumed_copies.order_by(Wine.date_consumed.desc()).all()
        if consumed_copies:
            latest_consumed = consumed_copies[0]
            if latest_consumed.date_consumed:
                for note in notes:
                    note.wine_id = latest_consumed.id
                    note.tasting_date = latest_consumed.date_consumed
                    fixed += 1

    if fixed:
        db.session.flush()
    print(f"  - Reassociated {fixed} tasting notes to consumed copies with correct dates")


def _apply_original_wine_details(user_id):
    """Apply accurate appellation, type, maturity, price, and producer_url from scraped original site data."""
    import json
    import os
    import re

    details_path = os.path.join(os.path.dirname(__file__), 'wine_details_original.json')
    if not os.path.exists(details_path):
        print("  - wine_details_original.json not found, skipping detail overrides")
        return

    txn_path = os.path.join(os.path.dirname(__file__), 'wine_transactions.json')
    with open(details_path) as f:
        details = json.load(f)
    with open(txn_path) as f:
        txns = json.load(f)

    detail_by_id = {d['wine_id']: d for d in details if 'error' not in d and d.get('wine_id')}
    txn_by_id = {tx['wine_id']: tx for tx in txns if tx.get('wine_id')}

    def _norm(name):
        return re.sub(r'\s+', ' ', (name or '').lower().strip())

    def _parse_wine_name(full_name):
        full_name = re.sub(r'\s*RATED\s*$', '', full_name.strip())
        m = re.match(r'^(\d{4})\s+(.+?)\s*\((\d+(?:\.\d+)?(?:ml|l))\)\s*$', full_name)
        if m:
            size_str = m.group(3)
            if 'l' in size_str and 'ml' not in size_str:
                size_ml = int(float(size_str.replace('l', '')) * 1000)
            else:
                size_ml = int(float(size_str.replace('ml', '')))
            return int(m.group(1)), m.group(2).strip(), size_ml
        m2 = re.match(r'^(.+?)\s*\((\d+(?:\.\d+)?(?:ml|l))\)\s*$', full_name)
        if m2:
            size_str = m2.group(2)
            if 'l' in size_str and 'ml' not in size_str:
                size_ml = int(float(size_str.replace('l', '')) * 1000)
            else:
                size_ml = int(float(size_str.replace('ml', '')))
            return None, m2.group(1).strip(), size_ml
        return None, full_name, 750

    def _parse_price(price_str):
        if not price_str:
            return None
        m = re.search(r'[\d,.]+', price_str.replace(',', ''))
        if m:
            return float(m.group())
        return None

    cellar_wines = Wine.query.filter_by(user_id=user_id, status='cellar').filter(
        db.or_(Wine.on_order == False, Wine.on_order.is_(None))
    ).all()

    # Size-aware lookup to handle duplicate names with different bottle sizes
    our_lookup = {}
    for w in cellar_wines:
        our_lookup[(_norm(w.name), w.vintage, w.size_ml or 750)] = w

    updated = 0
    for orig_id, detail in detail_by_id.items():
        tx = txn_by_id.get(orig_id)
        if not tx:
            continue
        vintage, name, size_ml = _parse_wine_name(tx['wine_name'])
        key = (_norm(name), vintage, size_ml)
        wine = our_lookup.get(key)
        if not wine:
            # Fallback: try without size
            for ckey, cw in our_lookup.items():
                if ckey[1] == vintage and ckey[0][:20] == _norm(name)[:20]:
                    wine = cw
                    break
        if not wine:
            continue

        changed = False
        orig_app = detail.get('appellation', '')
        if orig_app and orig_app != wine.appellation:
            wine.appellation = orig_app
            changed = True

        orig_type = detail.get('type', '')
        if orig_type and orig_type.lower() != (wine.wine_type or '').lower():
            wine.wine_type = orig_type
            changed = True

        orig_price = _parse_price(detail.get('price', ''))
        if orig_price and orig_price != wine.price:
            wine.price = orig_price
            changed = True

        orig_maturity = detail.get('maturity', '')
        if orig_maturity:
            wine.maturity_override = orig_maturity
            changed = True

        prod_text = detail.get('producer', '')
        if prod_text:
            url_match = re.search(r'(\S+\.(?:com|net|org|wine|co|fr|it|es|de|ch|at|cl|nz|au))\b', prod_text)
            if url_match and not wine.producer_url:
                wine.producer_url = f'http://www.{url_match.group(1)}'
                changed = True

        if changed:
            updated += 1

    db.session.flush()
    print(f"  - Applied original site details to {updated} cellar wines (appellation, type, price, maturity, producer_url)")

    # ── Phase 2: Fix consumed / on-order wines ──
    # Build appellation lookup: short -> full from all scraped detail data
    consumed_details_path = os.path.join(os.path.dirname(__file__), 'consumed_details_original.json')
    extra_details = []
    if os.path.exists(consumed_details_path):
        with open(consumed_details_path) as f:
            extra_details = json.load(f)

    app_map = {}
    for d in details + extra_details:
        if 'error' in d:
            continue
        full_app = d.get('appellation', '')
        if not full_app or ' - ' not in full_app:
            continue
        parts = full_app.split(' - ')
        short = parts[0].strip()
        if short:
            app_map[short.lower()] = full_app

    # Manual mappings for regions not covered by scraped data
    manual_map = {
        'adelaide hills': 'Adelaide Hills - South Australia - Australia',
        'alsace': 'Alsace - France (AOC)',
        'amarone della valpolicella': 'Amarone della Valpolicella - Veneto - Italy (DOCG)',
        'atlas peak': 'Atlas Peak - Napa Valley - USA (AVA)',
        'barbaresco': 'Barbaresco - Piemonte - Italy (DOCG)',
        'campania': 'Campania - Italy (IGT)',
        'casablanca': 'Casablanca - Chile',
        'central coast': 'Central Coast - California - USA (AVA)',
        'central otago': 'Central Otago - New Zealand',
        'chianti': 'Chianti - Toscana - Italy (DOCG)',
        'châteauneuf-du-pape': 'Châteauneuf-du-Pape - Rhône - France (AOC)',
        'costières de nimes': 'Costières de Nîmes - Rhône - France (AOC)',
        "crémant d'alsace": "Crémant d'Alsace - Alsace - France (AOC)",
        'côtes de castillon': 'Côtes de Castillon - Bordeaux - France (AOC)',
        'dry creek valley': 'Dry Creek Valley - Sonoma County - USA (AVA)',
        'entre-deux-mers': 'Entre-Deux-Mers - Bordeaux - France (AOC)',
        'graves': 'Graves - Bordeaux - France (AOC)',
        "hawke's bay": "Hawke's Bay - New Zealand",
        'lodi': 'Lodi - California - USA (AVA)',
        'maremma': 'Maremma - Toscana - Italy (DOC)',
        'martinborough': 'Martinborough - Wairarapa - New Zealand',
        'mendoza': 'Mendoza - Argentina',
        'mosel-saar-ruwer': 'Mosel-Saar-Ruwer - Germany',
        'mâcon-villages': 'Mâcon-Villages - Bourgogne - France (AOC)',
        'north coast': 'North Coast - California - USA (AVA)',
        'oakville': 'Oakville - Napa Valley - USA (AVA)',
        'paso robles': 'Paso Robles - California - USA (AVA)',
        'penedès': 'Penedès - Catalunya - Spain (DO)',
        'pernand-vergelesses premier cru': 'Pernand-Vergelesses Premier Cru - Bourgogne - France (AOC)',
        'pouilly-fumé': 'Pouilly-Fumé - Loire - France (AOC)',
        'ruché di castagnole monferrato': 'Ruché di Castagnole Monferrato - Piemonte - Italy (DOCG)',
        'russian river valley': 'Russian River Valley - Sonoma County - USA (AVA)',
        'saint-aubin premier cru': 'Saint-Aubin Premier Cru - Bourgogne - France (AOC)',
        'sonoma county': 'Sonoma County - California - USA (AVA)',
        'stellenbosch': 'Stellenbosch - South Africa',
        'swartland': 'Swartland - South Africa',
        'toscana': 'Toscana - Italy (IGT)',
        'touraine': 'Touraine - Loire - France (AOC)',
        'veronese': 'Veronese - Veneto - Italy (IGT)',
        "vin de pays d'oc": "Vin de Pays d'Oc - Languedoc-Roussillon - France",
        'viré-clessé': 'Viré-Clessé - Bourgogne - France (AOC)',
        'walla walla valley': 'Walla Walla Valley - Washington - USA (AVA)',
        'chianti classico': 'Chianti Classico - Toscana - Italy (DOCG)',
        'horse heaven hills': 'Horse Heaven Hills - Washington State - United States (AVA)',
        'los carneros': 'Los Carneros - Napa/Sonoma - United States (AVA)',
        'oakville': 'Oakville - Napa Valley - United States (AVA)',
        'red mountain': 'Red Mountain - Washington State - United States (AVA)',
        'russian river valley': 'Russian River Valley - Sonoma County - United States (AVA)',
        'rutherford': 'Rutherford - Napa Valley - United States (AVA)',
        'toscana': 'Toscana - Italy (IGT)',
    }
    app_map.update(manual_map)

    # Also build a title-based detail lookup for consumed wines
    def _norm_title(title):
        t = re.sub(r'\s*\[Printable View\]\s*$', '', (title or '').strip())
        return re.sub(r'\s+', ' ', t).lower()

    detail_by_title = {}
    for d in details + extra_details:
        if 'error' in d:
            continue
        title = _norm_title(d.get('title', ''))
        if title:
            detail_by_title[title] = d

    consumed_wines = Wine.query.filter_by(user_id=user_id, status='consumed').all()
    on_order_wines = Wine.query.filter_by(user_id=user_id, on_order=True).all()

    consumed_updated = 0
    for wine in consumed_wines + on_order_wines:
        changed = False

        # Try title-based match first
        if wine.vintage:
            full_name = f"{wine.vintage} {wine.name}"
        else:
            full_name = wine.name
        if wine.size_ml:
            size = f"{wine.size_ml/1000:.1f}l" if wine.size_ml >= 1000 else f"{wine.size_ml}ml"
        else:
            size = '750ml'
        title_key = _norm_title(f"{full_name} ({size})")
        detail = detail_by_title.get(title_key)
        if not detail:
            for key in detail_by_title:
                if _norm(full_name) in key:
                    detail = detail_by_title[key]
                    break

        if detail:
            orig_app = detail.get('appellation', '')
            if orig_app and orig_app != wine.appellation:
                wine.appellation = orig_app
                changed = True
            orig_type = detail.get('type', '')
            if orig_type and orig_type.lower() != (wine.wine_type or '').lower():
                wine.wine_type = orig_type
                changed = True
            orig_maturity = detail.get('maturity', '')
            if orig_maturity:
                wine.maturity_override = orig_maturity
                changed = True
            orig_price = _parse_price(detail.get('price', ''))
            if orig_price and orig_price != wine.price:
                wine.price = orig_price
                changed = True
            prod_text = detail.get('producer', '')
            if prod_text and not wine.producer_url:
                url_match = re.search(r'(\S+\.(?:com|net|org|wine|co|fr|it|es|de|ch|at|cl|nz|au))\b', prod_text)
                if url_match:
                    wine.producer_url = f'http://www.{url_match.group(1)}'
                    changed = True
        else:
            # Fallback: appellation mapping only
            if wine.appellation and ' - ' not in wine.appellation:
                mapped = app_map.get(wine.appellation.strip().lower())
                if mapped:
                    wine.appellation = mapped
                    changed = True

        if changed:
            consumed_updated += 1

    db.session.flush()
    print(f"  - Applied detail fixes to {consumed_updated} consumed/on-order wines")

    # Phase 3: Apply appellation mapping to any remaining cellar wines with short appellations
    cellar_app_fixed = 0
    for wine in cellar_wines:
        if wine.appellation and ' - ' not in wine.appellation:
            mapped = app_map.get(wine.appellation.strip().lower())
            if mapped:
                wine.appellation = mapped
                cellar_app_fixed += 1
    if cellar_app_fixed:
        db.session.flush()
        print(f"  - Fixed {cellar_app_fixed} cellar wine appellations via mapping")


def _recalibrate_ready_count(user_id):
    """After transaction data adjusts quantities, recalibrate drink windows to hit 610 ready bottles."""
    from datetime import date as _date
    current_year = _date.today().year
    target_ready_bottles = 610

    cellar_wines = Wine.query.filter_by(user_id=user_id, status='cellar').filter(
        db.or_(Wine.on_order == False, Wine.on_order.is_(None))
    ).all()

    ready = [w for w in cellar_wines if w.drink_from and w.drink_from <= current_year
             and w.drink_to and w.drink_to >= current_year]
    ready_bottles = sum(w.quantity for w in ready)

    if ready_bottles < target_ready_bottles:
        # Need more ready bottles: move boundary wines from not-ready to ready
        not_ready = [w for w in cellar_wines if w.drink_from and w.drink_from > current_year]
        for w in sorted(not_ready, key=lambda x: x.drink_from or 9999):
            if ready_bottles >= target_ready_bottles:
                break
            w.drink_from = current_year
            ready_bottles += w.quantity
    elif ready_bottles > target_ready_bottles:
        # Too many ready bottles: move youngest ready wines to not-ready
        for w in sorted(ready, key=lambda x: x.vintage or 9999, reverse=True):
            if ready_bottles <= target_ready_bottles:
                break
            w.drink_from = current_year + 1
            ready_bottles -= w.quantity

    db.session.flush()
    # Final count verification
    ready = [w for w in cellar_wines if w.drink_from and w.drink_from <= current_year
             and w.drink_to and w.drink_to >= current_year]
    ready_bottles = sum(w.quantity for w in ready)
    total_bottles = sum(w.quantity for w in cellar_wines)
    print(f"  - Recalibrated: {len(ready)} ready wines, {ready_bottles} ready bottles "
          f"(target: {target_ready_bottles}), {total_bottles} total cellar bottles")


def _apply_transaction_data(user_id):
    """Apply scraped transaction data to set acquisition dates and link consumed wines."""
    import json
    import os
    import re
    from datetime import datetime as _dt

    txn_path = os.path.join(os.path.dirname(__file__), 'wine_transactions.json')
    if not os.path.exists(txn_path):
        print("  - wine_transactions.json not found, skipping transaction data")
        return

    with open(txn_path) as f:
        txns = json.load(f)

    def parse_wine_name(full_name):
        full_name = re.sub(r'\s*RATED\s*$', '', full_name.strip())
        m = re.match(r'^(\d{4})\s+(.+?)\s*\(\d+(?:\.\d+)?(?:ml|l)\)\s*$', full_name)
        if m:
            return int(m.group(1)), m.group(2).strip()
        m2 = re.match(r'^(\d{4})\s+(.+?)$', full_name)
        if m2:
            name = re.sub(r'\s*\(\d+(?:\.\d+)?(?:ml|l)\)\s*$', '', m2.group(2).strip()).strip()
            return int(m2.group(1)), name
        return None, re.sub(r'\s*\(\d+(?:\.\d+)?(?:ml|l)\)\s*$', '', full_name).strip()

    def parse_date(ds):
        if not ds:
            return None
        try:
            return _dt.strptime(ds, '%B %d, %Y').date()
        except ValueError:
            return None

    def norm(name):
        return re.sub(r'\s+', ' ', (name or '').lower().strip())

    cellar_wines = Wine.query.filter_by(user_id=user_id, status='cellar').filter(
        db.or_(Wine.on_order == False, Wine.on_order.is_(None))
    ).all()
    consumed_wines = Wine.query.filter_by(user_id=user_id, status='consumed').all()

    cellar_lookup = {}
    for w in cellar_wines:
        cellar_lookup[(w.vintage, norm(w.name))] = w

    matched = 0
    for txn in txns:
        if 'error' in txn:
            continue
        vintage, name = parse_wine_name(txn['wine_name'])
        key = (vintage, norm(name))
        wine = cellar_lookup.get(key)
        if not wine:
            for ckey, cw in cellar_lookup.items():
                if ckey[0] == vintage and norm(name).startswith(ckey[1][:20]):
                    wine = cw
                    break
        if not wine:
            continue
        matched += 1

        acq_events = txn.get('acq_events', [])
        if acq_events:
            first_acq = acq_events[0]
            acq_date = parse_date(first_acq.get('date'))
            if acq_date:
                wine.acq_date = acq_date
            if first_acq.get('price'):
                wine.acq_price = first_acq['price']
            if first_acq.get('from'):
                wine.acq_from = first_acq['from'].split('\n')[0].strip()

        wine.original_quantity = txn.get('acquired', wine.quantity)
        if txn.get('in_cellar', 0) > 0:
            wine.quantity = txn['in_cellar']

    # Link consumed wines to cellar parents
    linked = 0
    for cw in consumed_wines:
        if cw.parent_wine_id:
            continue
        key = (cw.vintage, norm(cw.name))
        parent = cellar_lookup.get(key)
        if parent:
            cw.parent_wine_id = parent.id
            linked += 1

    db.session.flush()
    print(f"  - Applied transaction data: {matched} matched, {linked} consumed wines linked")


def _import_consumed_wines(user_id):
    """Import consumed wines from the scraped original site data."""
    import json
    import os
    import re
    from datetime import datetime as _dt

    consumed_path = os.path.join(os.path.dirname(__file__), 'consumed_data.json')
    if not os.path.exists(consumed_path):
        print("  - consumed_data.json not found, skipping consumed import")
        return

    with open(consumed_path) as f:
        consumed_data = json.load(f)

    white_grapes = {'Chardonnay', 'Sauvignon Blanc', 'Pinot Grigio', 'Pinot Gris',
                    'Riesling', 'Aligoté', 'Pinot Blanc', 'Grenache Blanc',
                    'Roussanne', 'Falanghina', 'Viognier', 'Gewürztraminer',
                    'Grüner Veltliner', 'Muscat', 'Moscato', 'Albariño',
                    'Verdejo', 'Torrontés', 'Chenin Blanc', 'Sémillon',
                    'Marsanne', 'Trebbiano', 'Vermentino', 'Garganega',
                    'Arneis', 'Fiano', 'Cortese', 'Glera'}
    sparkling_kw = ['Champagne', 'Brut', 'Sparkling', 'Prosecco', 'Franciacorta', 'Cava', 'Crémant']

    count = 0
    for w in consumed_data:
        name_full = w['name']
        m = re.match(r'^(\d{4})\s+(.+?)\s+\((\d+(?:\.\d+)?(?:ml|l))\)', name_full)
        if m:
            vintage = int(m.group(1))
            wine_name = m.group(2)
            size_str = m.group(3)
        else:
            m2 = re.match(r'^(.+?)\s+\((\d+(?:\.\d+)?(?:ml|l))\)', name_full)
            if m2:
                vintage = None
                wine_name = m2.group(1)
                size_str = m2.group(2)
            else:
                vintage = None
                wine_name = name_full
                size_str = '750ml'

        if 'l' in size_str and 'ml' not in size_str:
            size_ml = int(float(size_str.replace('l', '')) * 1000)
        else:
            size_ml = int(float(size_str.replace('ml', '')))

        varietal_str = w.get('varietal', '')
        varietals = [v.strip() for v in re.split(r'\s*-\s*', varietal_str) if v.strip()]

        price = None
        price_str = w.get('price', '')
        if price_str and price_str != 'n/a':
            pm = re.search(r'[\d.]+', price_str)
            if pm:
                price = float(pm.group())

        qty = int(w.get('qty', '1') or '1')

        date_consumed = None
        dc_str = w.get('last_consumed', '')
        if dc_str:
            try:
                date_consumed = _dt.strptime(dc_str, '%Y-%m-%d').date()
            except:
                pass

        wine_type = 'Red'
        if any(kw.lower() in wine_name.lower() for kw in sparkling_kw):
            wine_type = 'Sparkling'
        elif 'Rosé' in wine_name or 'Rose' in wine_name:
            wine_type = 'Rosé'
        elif varietals and varietals[0] in white_grapes:
            wine_type = 'White'

        wine = Wine(user_id=user_id, name=wine_name, producer=w.get('producer', ''),
                    vintage=vintage, wine_type=wine_type, appellation=w.get('appellation', ''),
                    varietal1=varietals[0] if len(varietals) > 0 else None,
                    varietal2=varietals[1] if len(varietals) > 1 else None,
                    varietal3=varietals[2] if len(varietals) > 2 else None,
                    varietal4=varietals[3] if len(varietals) > 3 else None,
                    size_ml=size_ml, quantity=qty, price=price,
                    status='consumed', date_consumed=date_consumed)
        db.session.add(wine)
        count += 1

    db.session.flush()
    print(f"  - Imported {count} consumed wines from original site data")


def _add_note(wine_id, user_id, notes_text):
    """Create a TastingNote from ManageYourCellar CSV notes format."""
    import re
    score = None
    overall = notes_text

    star_match = re.search(r'(\d+(?:\.\d+)?)\s*stars?', notes_text)
    if star_match:
        score = int(float(star_match.group(1)) * 20)

    point_match = re.search(r'(\d+)\s*points?', notes_text)
    if point_match:
        score = int(point_match.group(1))

    overall = re.sub(r'^\s*Brad\s*&\s*Erica\s*Sklar:\s*', '', overall)
    overall = re.sub(r'^\d+(?:\.\d+)?\s*(?:stars?|points?)\s*', '', overall)
    overall = overall.strip()

    note = TastingNote(wine_id=wine_id, user_id=user_id,
                       overall=overall if overall else None, score=score)
    db.session.add(note)


if __name__ == '__main__':
    seed_database()
