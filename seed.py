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

    # Propagate tasting note scores to wine ratings
    all_wines = Wine.query.filter_by(user_id=user.id).all()
    rating_count = 0
    for w in all_wines:
        notes_list = TastingNote.query.filter_by(wine_id=w.id).all()
        scores = [n.score for n in notes_list if n.score]
        if scores:
            w.rating = max(scores)
            rating_count += 1

    # Compute drink windows based on wine type and vintage
    from datetime import date as _date
    window_count = 0
    for w in all_wines:
        if w.vintage and not w.drink_from and not w.drink_to:
            v = w.vintage
            wtype = (w.wine_type or '').lower()
            if 'sparkling' in wtype:
                w.drink_from, w.drink_to = v + 1, v + 10
            elif 'dessert' in wtype or 'fortified' in wtype:
                w.drink_from, w.drink_to = v + 2, v + 30
            elif 'white' in wtype:
                w.drink_from, w.drink_to = v + 1, v + 7
            elif 'rosé' in wtype or 'rose' in wtype:
                w.drink_from, w.drink_to = v + 1, v + 4
            else:
                if w.price and w.price > 50:
                    w.drink_from, w.drink_to = v + 5, v + 20
                elif w.price and w.price > 25:
                    w.drink_from, w.drink_to = v + 3, v + 12
                else:
                    w.drink_from, w.drink_to = v + 2, v + 8
            window_count += 1

    db.session.commit()
    print(f"  - Set ratings for {rating_count} wines, drink windows for {window_count} wines")


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
