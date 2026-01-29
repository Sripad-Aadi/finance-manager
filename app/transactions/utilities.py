from io import BytesIO
from flask import make_response
from datetime import datetime
import pandas as pd
from app.models import Transaction
from sqlalchemy import func

def export_transactions_excel(transactions, username):
    """
    Export transactions to Excel with multiple sheets including summary and category breakdown
    
    Args:
        transactions: List of Transaction objects
        username: Current user's username
    
    Returns:
        Flask response object with Excel file
    """
    # Prepare data for DataFrame
    data = []
    total_income = 0
    total_expense = 0
    
    for transaction in transactions:
        date_str = transaction.date.strftime('%Y-%m-%d') if transaction.date else 'N/A'
        
        if transaction.type == 'income':
            amount = float(transaction.amount)
            total_income += amount
        else:
            amount = -float(transaction.amount)
            total_expense += abs(amount)
        
        data.append({
            'Date': date_str,
            'Description': transaction.description,
            'Category': transaction.category.title() if transaction.category else 'N/A',
            'Type': transaction.type.capitalize(),
            'Amount': amount
        })
    
    df = pd.DataFrame(data)
    
    # Calculate category breakdown
    category_breakdown = {}
    for transaction in transactions:
        cat = transaction.category.title() if transaction.category else 'N/A'
        amount = float(transaction.amount)
        
        if cat not in category_breakdown:
            category_breakdown[cat] = {'income': 0, 'expense': 0}
        
        if transaction.type == 'income':
            category_breakdown[cat]['income'] += amount
        else:
            category_breakdown[cat]['expense'] += amount
    
    # Prepare category breakdown data
    category_data = []
    for category, amounts in sorted(category_breakdown.items()):
        category_data.append({
            'Category': category,
            'Income': amounts['income'],
            'Expense': amounts['expense'],
            'Net': amounts['income'] - amounts['expense']
        })
    
    category_df = pd.DataFrame(category_data) if category_data else None
    
    # Create summary sheet
    net_balance = total_income - total_expense
    summary_data = {
        'Metric': [
            'Total Transactions',
            'Income Transactions',
            'Expense Transactions',
            'Total Income',
            'Total Expenses',
            'Net Balance',
            'Export Date'
        ],
        'Value': [
            len(transactions),
            len([t for t in transactions if t.type == 'income']),
            len([t for t in transactions if t.type == 'expense']),
            total_income,
            total_expense,
            net_balance,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    
    # Create Excel file in memory
    output = BytesIO()
    
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write summary sheet first
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Write transactions sheet
            df.to_excel(writer, sheet_name='Transactions', index=False)
            
            # Write category breakdown sheet if data exists
            if category_df is not None and not category_df.empty:
                category_df.to_excel(writer, sheet_name='Category Breakdown', index=False)
        
        output.seek(0)
    except Exception as e:
        print(f"Error creating Excel file: {e}")
        raise
    
    # Create response
    response = make_response(output.read())
    response.headers["Content-Disposition"] = f"attachment; filename=transactions_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response

def apply_transaction_filters(query, filters):
    """
    Apply filters to transaction query
    
    Args:
        query: SQLAlchemy query object
        filters: Dictionary of filter parameters
    
    Returns:
        Filtered query object
    """
    # Search filter (description)
    if filters.get('search'):
        search_term = f"%{filters['search']}%"
        query = query.filter(Transaction.description.ilike(search_term))
    
    # Transaction type filter
    if filters.get('type'):
        query = query.filter(Transaction.type == filters['type'])
    
    # Category filter
    if filters.get('category'):
        query = query.filter(Transaction.category == filters['category'])
    
    # Date from filter
    if filters.get('date_from'):
        try:
            date_from = datetime.strptime(filters['date_from'], '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= date_from)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    # Date to filter
    if filters.get('date_to'):
        try:
            date_to = datetime.strptime(filters['date_to'], '%Y-%m-%d').date()
            query = query.filter(Transaction.date <= date_to)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    # Amount range filter (optional)
    if filters.get('min_amount'):
        try:
            min_amount = float(filters['min_amount'])
            query = query.filter(Transaction.amount >= min_amount)
        except ValueError:
            pass
    
    if filters.get('max_amount'):
        try:
            max_amount = float(filters['max_amount'])
            query = query.filter(Transaction.amount <= max_amount)
        except ValueError:
            pass
    
    return query

def get_filter_summary(transactions, filters):
    """
    Calculate summary statistics for filtered transactions
    
    Args:
        transactions: List of Transaction objects
        filters: Dictionary of active filters
    
    Returns:
        Dictionary with summary data
    """
    total_income = sum(float(t.amount) for t in transactions if t.type == 'income')
    total_expense = sum(float(t.amount) for t in transactions if t.type == 'expense')
    
    return {
        'count': len(transactions),
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': total_income - total_expense,
        'active_filters': {k: v for k, v in filters.items() if v}
    }