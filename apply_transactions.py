"""Apply scraped transaction data from manageyourcellar.com to our database.

This script:
1. Matches cellar wines to their scraped transaction records (by wine name)
2. Sets acquisition dates, prices, sources, and original quantities
3. Links consumed wines to their cellar parents
4. Creates missing consumed wine records for consumption events in the transaction data
"""
import json
import re
import os
from datetime import datetime, date
from app import app, db
from models import User, Wine


def parse_wine_name(full_name):
    """Parse '2015 Almaviva (Proprietary Blend) (750ml) RATED' into (vintage, name)."""
    full_name = full_name.strip()
    # Remove RATED suffix
    full_name = re.sub(r'\s*RATED\s*$', '', full_name)
    # Try to extract vintage and size
    m = re.match(r'^(\d{4})\s+(.+?)\s*\((\d+(?:\.\d+)?(?:ml|l))\)\s*$', full_name)
    if m:
        return int(m.group(1)), m.group(2).strip()
    # Try without size
    m2 = re.match(r'^(\d{4})\s+(.+?)$', full_name)
    if m2:
        name = m2.group(2).strip()
        # Remove trailing (750ml) etc if present
        name = re.sub(r'\s*\(\d+(?:\.\d+)?(?:ml|l)\)\s*$', '', name).strip()
        return int(m2.group(1)), name
    # No vintage
    name = re.sub(r'\s*\(\d+(?:\.\d+)?(?:ml|l)\)\s*$', '', full_name).strip()
    return None, name


def parse_date_str(date_str):
    """Parse 'February 22, 2013' into a date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%B %d, %Y').date()
    except ValueError:
        return None


def normalize_name(name):
    """Normalize a wine name for fuzzy matching."""
    if not name:
        return ''
    # Lowercase, strip, remove extra spaces
    n = re.sub(r'\s+', ' ', name.lower().strip())
    # Remove common punctuation variations
    n = n.replace("'", "'").replace("'", "'").replace('"', '')
    return n


def apply_transactions():
    with app.app_context():
        # Ensure new columns exist
        db.create_all()

        user = User.query.filter_by(username='bread').first()
        if not user:
            print("User 'bread' not found!")
            return

        # Load transaction data
        txn_path = os.path.join(os.path.dirname(__file__), 'wine_transactions.json')
        if not os.path.exists(txn_path):
            print("wine_transactions.json not found!")
            return

        with open(txn_path) as f:
            txns = json.load(f)
        print(f"Loaded {len(txns)} transaction records")

        # Get all cellar wines for bread
        cellar_wines = Wine.query.filter_by(user_id=user.id, status='cellar').filter(
            db.or_(Wine.on_order == False, Wine.on_order.is_(None))
        ).all()
        print(f"Found {len(cellar_wines)} cellar wines in DB")

        # Get all consumed wines for bread
        consumed_wines = Wine.query.filter_by(user_id=user.id, status='consumed').all()
        print(f"Found {len(consumed_wines)} consumed wines in DB")

        # Build lookup for cellar wines by normalized (vintage, name)
        cellar_lookup = {}
        for w in cellar_wines:
            key = (w.vintage, normalize_name(w.name))
            cellar_lookup[key] = w

        # Step 1: Match cellar wines to transaction records and update acquisition data
        matched = 0
        unmatched_txns = []
        for txn in txns:
            if 'error' in txn:
                continue
            vintage, name = parse_wine_name(txn['wine_name'])
            key = (vintage, normalize_name(name))
            wine = cellar_lookup.get(key)

            if not wine:
                # Try fuzzy match - remove trailing size info
                for ckey, cw in cellar_lookup.items():
                    if ckey[0] == vintage and normalize_name(name).startswith(ckey[1][:20]):
                        wine = cw
                        break

            if not wine:
                unmatched_txns.append(txn['wine_name'][:60])
                continue

            matched += 1

            # Update acquisition data from first acq event
            acq_events = txn.get('acq_events', [])
            if acq_events:
                first_acq = acq_events[0]
                acq_date = parse_date_str(first_acq.get('date'))
                if acq_date:
                    wine.acq_date = acq_date
                if first_acq.get('price'):
                    wine.price = first_acq['price']
                if first_acq.get('from'):
                    wine.acq_from = first_acq['from'].split('\n')[0].strip()

            # Set original_quantity from transaction summary
            wine.original_quantity = txn.get('acquired', wine.quantity)

            # Update current quantity to match "in_cellar" from original
            if txn.get('in_cellar', 0) > 0:
                wine.quantity = txn['in_cellar']

        db.session.flush()
        print(f"\nStep 1: Matched {matched} cellar wines to transaction records")
        if unmatched_txns:
            print(f"  Unmatched: {len(unmatched_txns)} transactions")
            for name in unmatched_txns[:5]:
                print(f"    - {name}")

        # Step 2: Link consumed wines to their cellar parents
        linked = 0
        for cw in consumed_wines:
            if cw.parent_wine_id:
                continue  # Already linked
            key = (cw.vintage, normalize_name(cw.name))
            parent = cellar_lookup.get(key)
            if parent:
                cw.parent_wine_id = parent.id
                linked += 1

        db.session.flush()
        print(f"\nStep 2: Linked {linked} consumed wines to cellar parents")

        # Step 3: Create missing consumed wine records from transaction consumption events
        created = 0
        for txn in txns:
            if 'error' in txn or not txn.get('consumed_events'):
                continue

            vintage, name = parse_wine_name(txn['wine_name'])
            key = (vintage, normalize_name(name))
            parent = cellar_lookup.get(key)
            if not parent:
                continue

            # Check existing consumed copies for this parent
            existing_consumed = Wine.query.filter_by(
                user_id=user.id, status='consumed', parent_wine_id=parent.id
            ).all()

            # Also find consumed wines matching by name that could be linked
            name_matches = [w for w in consumed_wines
                           if w.vintage == vintage
                           and normalize_name(w.name) == normalize_name(parent.name)
                           and not w.parent_wine_id]

            # Link name matches first
            for nm in name_matches:
                nm.parent_wine_id = parent.id
                linked += 1

            existing_consumed = Wine.query.filter_by(
                user_id=user.id, status='consumed', parent_wine_id=parent.id
            ).all()
            existing_count = sum(c.quantity for c in existing_consumed)
            expected_count = txn.get('consumed', 0)

            if existing_count >= expected_count:
                continue  # Already have enough consumed records

            # Match consumption events to existing consumed records by date
            existing_dates = set()
            for ec in existing_consumed:
                if ec.date_consumed:
                    existing_dates.add(ec.date_consumed)

            for evt in txn['consumed_events']:
                evt_date = parse_date_str(evt.get('date'))
                evt_qty = evt.get('quantity', 1)

                # Check if we already have a consumed record for this date
                if evt_date and evt_date in existing_dates:
                    continue

                # Update existing consumed record's date if it matches by qty
                updated = False
                for ec in existing_consumed:
                    if not ec.date_consumed and ec.quantity == evt_qty:
                        ec.date_consumed = evt_date
                        updated = True
                        break

                if not updated and existing_count < expected_count:
                    # Create new consumed wine record
                    consumed = Wine(
                        user_id=user.id,
                        name=parent.name, producer=parent.producer,
                        vintage=parent.vintage, wine_type=parent.wine_type,
                        appellation=parent.appellation,
                        varietal1=parent.varietal1, varietal2=parent.varietal2,
                        varietal3=parent.varietal3, varietal4=parent.varietal4,
                        size_ml=parent.size_ml, alcohol_pct=parent.alcohol_pct,
                        price=parent.price, quantity=evt_qty,
                        acq_from=parent.acq_from,
                        status='consumed',
                        date_consumed=evt_date,
                        parent_wine_id=parent.id,
                        rating=parent.rating,
                        drink_from=parent.drink_from, drink_to=parent.drink_to
                    )
                    db.session.add(consumed)
                    created += 1
                    existing_count += evt_qty

        db.session.flush()
        print(f"\nStep 3: Created {created} new consumed wine records from transaction events")
        print(f"  Additional linked: {linked}")

        # Step 4: Update consumed-only wines (no cellar entry) with acquisition dates
        # These are wines that were fully consumed - find them in consumed_wines that
        # don't have a parent_wine_id
        orphan_consumed = [w for w in consumed_wines if not w.parent_wine_id]
        print(f"\nStep 4: {len(orphan_consumed)} consumed wines with no cellar parent (fully consumed)")

        db.session.commit()
        print("\nDone! All changes committed.")

        # Final stats
        cellar_with_acq = Wine.query.filter_by(user_id=user.id, status='cellar').filter(
            Wine.acq_date.isnot(None)
        ).count()
        total_linked = Wine.query.filter_by(user_id=user.id, status='consumed').filter(
            Wine.parent_wine_id.isnot(None)
        ).count()
        print(f"\nFinal stats:")
        print(f"  Cellar wines with acq_date: {cellar_with_acq}")
        print(f"  Consumed wines linked to parents: {total_linked}")


if __name__ == '__main__':
    apply_transactions()
