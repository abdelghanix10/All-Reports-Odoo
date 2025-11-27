
import odoo
from odoo import api, SUPERUSER_ID

def check_session_data(env):
    # Find session POS/00205
    session = env['pos.session'].search([('name', '=', 'POS/00205')], limit=1)
    if not session:
        print("Session POS/00205 not found. Listing last 5 sessions:")
        sessions = env['pos.session'].search([], order='id desc', limit=5)
        for s in sessions:
            print(f" - {s.name} (ID: {s.id})")
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

