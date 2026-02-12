#!/usr/bin/env python3
"""
Import cellar CSV data for a specific user.
Usage: python import_cellar.py <csv_file> <username> <password>
"""
import sys
import csv
import re
from io import StringIO
from app import app, db
from models import User, Wine, TastingNote


def parse_tasting_note(wine_id, user_id, notes_text):
    """Parse tasting note text from ManageYourCellar CSV format."""
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

    # Clean up the text
    overall = re.sub(r'^\s*Brad\s*&\s*Erica\s*Sklar:\s*', '', overall)
    overall = re.sub(r'^\d+(?:\.\d+)?\s*(?:stars?|points?)\s*', '', overall)
    overall = overall.strip()

    # Parse tasting descriptors
    appearance_words = []
    nose_words = []
    palate_words = []

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

    note = TastingNote(
        wine_id=wine_id,
        user_id=user_id,
        appearance=', '.join(appearance_words) if appearance_words else None,
        nose=', '.join(nose_words) if nose_words else None,
        palate=', '.join(palate_words) if palate_words else None,
        overall=overall if overall else None,
        score=score
    )
    return note


def detect_wine_type(name, appellation, varietals):
    """Detect wine type from name, appellation, and varietals."""
    white_grapes = {'Chardonnay', 'Sauvignon Blanc', 'Pinot Grigio', 'Pinot Gris',
                    'Riesling', 'Gewürztraminer', 'Viognier', 'Sémillon', 'Aligoté',
                    'Pinot Blanc', 'Chenin Blanc', 'Muscat', 'Grenache Blanc',
                    'Roussanne', 'Marsanne', 'Falanghina', 'Prosecco', 'Xarel-Lo',
                    'Macabeo', 'Parellada', 'Grenache Gris', 'Vermentino',
                    'Sauvignon Blanc-Sémillon'}
    sparkling_kw = ['Champagne', 'Brut', 'Sparkling', 'Prosecco', 'Franciacorta']
    dessert_kw = ['Sauternes', 'Barsac']

    if any(kw.lower() in name.lower() for kw in sparkling_kw):
        return 'Sparkling'
    if any(kw.lower() in appellation.lower() for kw in dessert_kw):
        return 'Dessert'
    if 'Rosé' in name or 'Rose' in name or 'Rosé' in name:
        return 'Rosé'
    if varietals and all(v in white_grapes for v in varietals):
        return 'White'
    return 'Red'


def import_csv(csv_path, username, password):
    with app.app_context():
        # Create or get user
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User '{username}' already exists. Clearing existing wines...")
            # Delete existing wines and notes for this user
            TastingNote.query.filter_by(user_id=user.id).delete()
            Wine.query.filter_by(user_id=user.id).delete()
            db.session.commit()
        else:
            user = User(username=username, email=f'{username}@winecellar.com')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Created user '{username}'")

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        reader = csv.reader(StringIO(content))

        # Find header row
        header = None
        for row in reader:
            cleaned = [c.strip() for c in row]
            if 'Name' in cleaned and 'Producer' in cleaned:
                header = cleaned
                break

        if not header:
            print("ERROR: Could not find header row")
            return

        col = {}
        for i, h in enumerate(header):
            col[h.lower()] = i
        print(f"Found columns: {list(col.keys())}")

        wine_count = 0
        note_count = 0
        wine_cache = {}  # (vintage, name, producer) -> wine_id

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
                try:
                    vintage = int(vintage_str)
                except ValueError:
                    pass

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

            wine_type = detect_wine_type(name, appellation, varietals)
            cache_key = (vintage, name, producer)

            if qty_str:
                # Cellar entry
                try:
                    quantity = int(qty_str)
                except ValueError:
                    quantity = 1

                wine = Wine(
                    user_id=user.id,
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

                if notes and 'Brad & Erica Sklar' in notes:
                    note = parse_tasting_note(wine.id, user.id, notes)
                    db.session.add(note)
                    note_count += 1

            elif notes:
                # Consumed wine with tasting note
                wine_id = wine_cache.get(cache_key)
                if not wine_id:
                    wine = Wine(
                        user_id=user.id,
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

                note = parse_tasting_note(wine_id, user.id, notes)
                db.session.add(note)
                note_count += 1

        db.session.commit()
        print(f"\nImport complete!")
        print(f"  Wines: {wine_count}")
        print(f"  Tasting notes: {note_count}")
        print(f"  User: {username}")


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python import_cellar.py <csv_file> <username> <password>")
        sys.exit(1)
    import_csv(sys.argv[1], sys.argv[2], sys.argv[3])
