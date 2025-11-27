
import sys
import os

# Add Odoo server to path
sys.path.append(r"c:\Program Files\Odoo 18.0.20251102\server")

import odoo
from odoo import api, SUPERUSER_ID

def run_check():
    # Set configuration
    odoo.tools.config['db_host'] = 'localhost'
    odoo.tools.config['db_port'] = 5432
    odoo.tools.config['db_user'] = 'openpg'
    odoo.tools.config['db_password'] = 'openpgpwd'
    
    # Try to connect to 'odoo' database
    db_name = 'odoo'
    
    try:
        registry = odoo.registry(db_name)
    except Exception as e:
        print(f"Failed to connect to database '{db_name}': {e}")
        return

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        print(f"Connected to database: {db_name}")
        
        # Find session POS/00205
        session = env['pos.session'].search([('name', '=', 'POS/00205')], limit=1)
        if not session:
            print("Session POS/00205 not found. Listing last 5 sessions:")
            sessions = env['pos.session'].search([], order='id desc', limit=5)
            for s in sessions:
                print(f" - {s.name} (ID: {s.id}) Start: {s.start_at}")
            return

        print(f"Found Session: {session.name} (ID: {session.id})")
        print(f"Start At: {session.start_at}")
        print(f"Stop At: {session.stop_at}")
        
        # Check Orders
        print(f"Order IDs count: {len(session.order_ids)}")
        if session.order_ids:
            print(f"First Order: {session.order_ids[0].name} Amount: {session.order_ids[0].amount_total}")

        # Check Fields existence and values
        fields_to_check = [
            'cash_register_balance_start',
            'cash_register_balance_end_real',
            'cash_register_balance_end',
            'cash_register_difference',
            'amount_total_incl'
        ]
        
        for field in fields_to_check:
            exists = field in session._fields
            value = getattr(session, field, 'N/A') if exists else 'Field not in model'
            print(f"Field '{field}': Exists={exists}, Value={value}")

        # Check computed total from orders
        total_orders = sum(session.order_ids.mapped('amount_total'))
        print(f"Sum of orders amount_total: {total_orders}")

if __name__ == "__main__":
    run_check()
