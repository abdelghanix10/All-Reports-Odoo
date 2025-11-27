from odoo import models, api, fields
from datetime import datetime, time
import pytz
import logging

_logger = logging.getLogger(__name__)

class AllReportsDashboard(models.TransientModel):
    _name = 'all_reports.dashboard'
    _description = 'All Reports Dashboard Logic'

    @api.model
    def get_dashboard_data(self, date_str):
        debug_logs = []
        def log(msg):
            _logger.info(msg)
            debug_logs.append(str(msg))

        log(f"AllReportsDashboard: get_dashboard_data called with {date_str}")
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            user_tz = pytz.timezone(self.env.user.tz or 'UTC')
            
            start_of_day_user = user_tz.localize(datetime.combine(target_date, time.min))
            end_of_day_user = user_tz.localize(datetime.combine(target_date, time.max))
            
            start_of_day_utc = start_of_day_user.astimezone(pytz.UTC).replace(tzinfo=None)
            end_of_day_utc = end_of_day_user.astimezone(pytz.UTC).replace(tzinfo=None)

            # 1. Sessions
            # Use sudo() to ensure we can read all sessions and their orders
            sessions = self.env['pos.session'].sudo().search([
                ('start_at', '>=', start_of_day_utc),
                ('start_at', '<=', end_of_day_utc)
            ])
            
            log(f"Found {len(sessions)} sessions for date {date_str}")

            sessions_data = []
            for session in sessions:
                try:
                    log(f"Processing Session: {session.name} (ID: {session.id})")
                    orders = session.order_ids
                    log(f" - Order Count: {len(orders)}")
                    
                    category_data = {}
                    
                    for order in orders:
                        for line in order.lines:
                            # Fix for pos_categ_id error: Check for pos_categ_ids (Many2many) or pos_categ_id (Many2one)
                            cat_name = 'Uncategorized'
                            product = line.product_id
                            
                            if 'pos_categ_ids' in product._fields and product.pos_categ_ids:
                                cat_name = product.pos_categ_ids[0].name
                            elif 'pos_categ_id' in product._fields and product.pos_categ_id:
                                cat_name = product.pos_categ_id.name

                            if cat_name not in category_data:
                                category_data[cat_name] = {'name': cat_name, 'products': [], 'total': 0.0}
                            
                            found = False
                            for p in category_data[cat_name]['products']:
                                if p['name'] == line.product_id.name:
                                    p['qty'] += line.qty
                                    p['amount'] += line.price_subtotal_incl
                                    found = True
                                    break
                            if not found:
                                category_data[cat_name]['products'].append({
                                    'name': line.product_id.name,
                                    'qty': line.qty,
                                    'amount': line.price_subtotal_incl
                                })
                            
                            category_data[cat_name]['total'] += line.price_subtotal_incl

                    breakdown = list(category_data.values())

                    gross_sales = sum(orders.mapped('amount_total'))
                    tax = sum(orders.mapped('amount_tax'))
                    returns = sum(orders.filtered(lambda o: o.amount_total < 0).mapped('amount_total'))
                    
                    discount = 0.0
                    for order in orders:
                        for line in order.lines:
                            if line.discount:
                                discount += (line.price_unit * line.qty * line.discount / 100)

                    # Safe field access
                    opening_balance = 0.0
                    if 'cash_register_balance_start' in session._fields:
                        opening_balance = session.cash_register_balance_start
                    
                    closing_balance = 0.0
                    # Try 'cash_register_balance_end_real' (Counted) first, then 'cash_register_balance_end' (Computed)
                    if 'cash_register_balance_end_real' in session._fields:
                        closing_balance = session.cash_register_balance_end_real
                    
                    if closing_balance == 0.0 and 'cash_register_balance_end' in session._fields:
                         closing_balance = session.cash_register_balance_end

                    difference = 0.0
                    if 'cash_register_difference' in session._fields:
                        difference = session.cash_register_difference
                    
                    total = 0.0
                    if 'amount_total_incl' in session._fields:
                        total = session.amount_total_incl
                    
                    # Fallback to summing orders if total is still 0
                    if total == 0.0:
                        total = sum(orders.mapped('amount_total'))

                    log(f" - Opening: {opening_balance}, Closing: {closing_balance}, Total: {total}")

                    sessions_data.append({
                        'name': session.name,
                        'id': session.id,
                        'opened_date': session.start_at,
                        'closed_date': session.stop_at,
                        'status': session.state,
                        'opening_balance': opening_balance,
                        'closing_balance': closing_balance,
                        'difference': difference,
                        'gross_sales': gross_sales,
                        'tax': tax,
                        'returns': returns,
                        'discount': discount,
                        'total': total,
                        'breakdown': breakdown
                    })
                except Exception as e:
                    log(f"Error processing session {session.id}: {e}")
                    continue

            # 2. Production
            production_moves = self.env['stock.move'].search([
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'production'),
                ('location_dest_id.usage', '=', 'internal'),
                ('date', '>=', start_of_day_utc),
                ('date', '<=', end_of_day_utc)
            ])
            
            production_data = []
            for move in production_moves:
                production_data.append({
                    'product_name': move.product_id.display_name,
                    'quantity': move.quantity,
                    'status': move.state
                })

            # 3. Lost Products
            lost_moves = self.env['stock.move'].search([
                ('state', '=', 'done'),
                ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '=', 'inventory'),
                ('date', '>=', start_of_day_utc),
                ('date', '<=', end_of_day_utc)
            ])
            
            lost_data = []
            for move in lost_moves:
                lost_data.append({
                    'product_name': move.product_id.display_name,
                    'quantity': move.quantity,
                    'status': move.state
                })

            return {
                'sessions': sessions_data,
                'production': production_data,
                'lost_products': lost_data,
                'debug_logs': debug_logs
            }
        except Exception as e:
            log(f"Error in get_dashboard_data: {e}")
            raise e
