from flask import render_template,Blueprint,request,current_app
from flask_login import current_user
from app.main.utilities import get_dashboard_stats,get_category_breakdown
from app import cache

main=Blueprint('main',__name__)

@main.route('/')
@main.route('/home')
def home():
    if current_user.is_authenticated:
        
        period = request.args.get('period', 'this_month')
        stats = get_dashboard_stats(current_user.id)
        
        expense_breakdown = get_category_breakdown(current_user.id, 'expense', period)
        income_breakdown = get_category_breakdown(current_user.id, 'income', period)
        
        stats['expense_breakdown'] = expense_breakdown
        stats['income_breakdown'] = income_breakdown
        stats['selected_period'] = period
        
        return render_template('home.html',stats=stats)
    else:
        return render_template('home.html')
        
