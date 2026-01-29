from app.models import Transaction
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

def get_spending_by_category(user_id, start_date=None, end_date=None, transaction_type='expense'):
    """
    Get spending/income grouped by category
    
    Args:
        user_id: Current user's ID
        start_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
        transaction_type: 'expense' or 'income'
    
    Returns:
        List of tuples: [(category, total_amount), ...]
    """
    query = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == transaction_type
    )
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    # Group by category and order by total descending
    results = query.group_by(Transaction.category)\
                  .order_by(func.sum(Transaction.amount).desc())\
                  .all()
    
    return [(cat, float(total)) for cat, total in results]


def get_category_breakdown(user_id, transaction_type='expense', period='this_month'):
    """
    Get detailed category breakdown with percentages
    
    Args:
        user_id: Current user's ID
        transaction_type: 'expense' or 'income'
        period: 'this_month', 'last_month', 'last_3_months', 'this_year', 'all_time'
    
    Returns:
        Dictionary with category data
    """
    # Calculate date range based on period
    today = datetime.now().date()
    
    if period == 'this_month':
        start_date = today.replace(day=1)
        end_date = today
    elif period == 'last_month':
        last_month = today.replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1)
        end_date = last_month
    elif period == 'last_3_months':
        start_date = today - timedelta(days=90)
        end_date = today
    elif period == 'this_year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:  # all_time
        start_date = None
        end_date = None
    
    # Get category totals
    categories = get_spending_by_category(user_id, start_date, end_date, transaction_type)
    
    # Calculate total and percentages
    total_amount = sum(amount for _, amount in categories)
    
    category_data = []
    for category, amount in categories:
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
        category_data.append({
            'name': category,
            'amount': amount,
            'percentage': round(percentage, 1)
        })
    
    return {
        'categories': category_data,
        'total': total_amount,
        'period': period,
        'start_date': start_date,
        'end_date': end_date
    }


def get_dashboard_stats(user_id):
    """
    Get comprehensive dashboard statistics
    
    Returns:
        Dictionary with all dashboard data
    """
    # Current month dates
    today = datetime.now().date()
    first_day = today.replace(day=1)
    
    # Total balance (all time)
    total_income = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.user_id == user_id, Transaction.type == 'income')\
        .scalar() or 0
    
    total_expense = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.user_id == user_id, Transaction.type == 'expense')\
        .scalar() or 0
    
    # This month's data
    month_income = db.session.query(func.sum(Transaction.amount))\
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == 'income',
            Transaction.date >= first_day
        ).scalar() or 0
    
    month_expense = db.session.query(func.sum(Transaction.amount))\
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.date >= first_day
        ).scalar() or 0
    
    # Get category breakdown
    expense_breakdown = get_category_breakdown(user_id, 'expense', 'this_month')
    income_breakdown = get_category_breakdown(user_id, 'income', 'this_month')
    
    # Recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=user_id)\
        .order_by(Transaction.date.desc(), Transaction.created_at.desc())\
        .limit(5)\
        .all()
    
    # Transaction count
    total_transactions = Transaction.query.filter_by(user_id=user_id).count()
    
    return {
        'balance': float(total_income - total_expense),
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'month_income': float(month_income),
        'month_expense': float(month_expense),
        'expense_breakdown': expense_breakdown,
        'income_breakdown': income_breakdown,
        'recent_transactions': recent_transactions,
        'total_transactions': total_transactions,
        'savings_rate': round((month_income - month_expense) / month_income * 100, 1) if month_income > 0 else 0
    }


def get_category_icon(category):
    """
    Return Font Awesome icon for category
    
    Args:
        category: Category name (lowercase)
    
    Returns:
        Icon class name
    """
    icons = {
        # Expense categories
        'food': 'fa-utensils',
        'entertainment': 'fa-film',
        'grocery': 'fa-shopping-cart',
        'travel': 'fa-car',
        'transfers': 'fa-exchange-alt',
        'investment': 'fa-chart-line',
        'shopping': 'fa-shopping-bag',
        'medical': 'fa-heartbeat',
        'bills': 'fa-file-invoice',
        'miscellaneous': 'fa-ellipsis-h',
        'other_expense': 'fa-ellipsis-h',
        
        # Income categories
        'salary': 'fa-money-bill-wave',
        'freelance': 'fa-laptop',
        'business': 'fa-briefcase',
        'investment_profit': 'fa-chart-line',
        'gift': 'fa-gift',
        'bonus': 'fa-star',
        'other_income': 'fa-plus-circle'
    }
    
    # Convert category to lowercase for matching
    category_lower = category.lower() if category else ''
    return icons.get(category_lower, 'fa-circle')


def get_category_color(category):
    """
    Return color class for category
    
    Args:
        category: Category name (lowercase)
    
    Returns:
        Bootstrap color class
    """
    # Expense categories
    colors = {
        # Expense Categories (avoiding danger red and success green for transaction types)
        'food': 'info',
        'entertainment': 'info',
        'grocery': 'warning',
        'travel': 'primary',
        'transfers': 'secondary',
        'investment': 'warning',
        'shopping': 'primary',
        'medical': 'info',
        'bills': 'warning',
        'miscellaneous': 'secondary',
        'other_expense': 'secondary',
        
        # Income Categories (avoiding danger red and success green for transaction types)
        'salary': 'warning',
        'freelance': 'info',
        'business': 'primary',
        'investment_profit': 'warning',
        'gift': 'info',
        'bonus': 'primary',
        'other_income': 'secondary'
    }
    
    # Convert category to lowercase for matching
    category_lower = category.lower() if category else ''
    return colors.get(category_lower, 'secondary')