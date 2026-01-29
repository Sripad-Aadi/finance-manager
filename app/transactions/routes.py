from datetime import datetime
from flask import Blueprint,render_template,flash,redirect,url_for,request,jsonify,abort
from flask_login import current_user,login_required
from sqlalchemy import func
from app import db
from app.forms import TransactionForm
from app.models import Transaction,TransactionType,IncomeCategory,ExpenseCategory
from app.transactions.utilities import export_transactions_excel,apply_transaction_filters,get_filter_summary

transactions=Blueprint('transactions',__name__)

@transactions.route('/transaction/add',methods=['GET','POST'])
@login_required
def add_transaction():
    form=TransactionForm()
    selected_type = form.type.data or TransactionType.EXPENSE.value

    if selected_type == TransactionType.INCOME.value:
        form.category.choices = [(c.value, c.name.replace('_',' ').title()) for c in IncomeCategory]
    else:
        form.category.choices = [(c.value, c.name.replace('_',' ').title()) for c in ExpenseCategory]
    if form.validate_on_submit():
        transaction=Transaction(type=TransactionType(form.type.data),
                                category=form.category.data,
                                amount=form.amount.data,
                                user_id=current_user.id,
                                date=form.date.data,
                                description=form.description.data)
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully','success')
        return redirect(url_for('main.home'))
    return render_template('add_update_transaction.html',form=form,purpose='Add')

@transactions.route('/transaction/categories')
@login_required
def get_categories():
    tx_type = request.args.get('type')

    if tx_type == TransactionType.INCOME.value:
        categories = [
            {"value": c.value, "label": c.name.replace('_',' ').title()}
            for c in IncomeCategory
        ]
    else:
        categories = [
            {"value": c.value, "label": c.name.replace('_',' ').title()}
            for c in ExpenseCategory
        ]

    return jsonify(categories)


@transactions.route('/view_transactions')
@login_required
def view_transactions():
    
    filters = {
        'search': request.args.get('search', '').strip(),
        'type': request.args.get('type', ''),
        'category': request.args.get('category', ''),
        'date_from': request.args.get('date_from', ''),
        'date_to': request.args.get('date_to', ''),
        'min_amount': request.args.get('min_amount', ''),
        'max_amount': request.args.get('max_amount', ''),
    }
    
    sort_by = request.args.get('sort', 'date_desc')
    page = request.args.get('page', 1, type=int)
    
    if page < 1:
        page = 1
    transactions=Transaction.query.filter(Transaction.user_id==current_user.id)
    transactions=apply_transaction_filters(transactions,filters)
    
    if sort_by == 'date_desc':
        transactions = transactions.order_by(Transaction.date.desc(), Transaction.created_at.desc())
    elif sort_by == 'date_asc':
        transactions = transactions.order_by(Transaction.date.asc(), Transaction.created_at.asc())
    elif sort_by == 'amount_desc':
        transactions = transactions.order_by(Transaction.amount.desc())
    elif sort_by == 'amount_asc':
        transactions = transactions.order_by(Transaction.amount.asc())
    elif sort_by == 'category':
        transactions = transactions.order_by(Transaction.category.asc())
    
    all_filtered = transactions.all()  # Get all for summary (without pagination)
    transactions = transactions.paginate(page=page, per_page=5 , error_out=False)
    
    summary = get_filter_summary(all_filtered, filters)
    
    categories = db.session.query(Transaction.category)\
                          .filter_by(user_id=current_user.id)\
                          .distinct()\
                          .order_by(Transaction.category)\
                          .all()
    categories = [c[0] for c in categories]
        
    return render_template('transactions.html',
                           transactions=transactions,
                           filters=filters,
                           categories=categories,
                           sort_by=sort_by,
                           summary=summary)
    
@transactions.route('/update_transaction/<int:trans_id>',methods=['GET','POST'])
@login_required
def update_transaction(trans_id):
    transaction=Transaction.query.get_or_404(trans_id)
    if transaction.user_id != current_user.id:
        abort(403)
    form=TransactionForm()
    selected_type = form.type.data or TransactionType.EXPENSE.value

    if selected_type == TransactionType.INCOME.value:
        form.category.choices = [(c.value, c.name.replace('_',' ').title()) for c in IncomeCategory]
    else:
        form.category.choices = [(c.value, c.name.replace('_',' ').title()) for c in ExpenseCategory]
    if form.validate_on_submit():
        transaction.type=form.type.data
        transaction.category=form.category.data
        transaction.amount=form.amount.data
        transaction.description=form.description.data
        transaction.date=form.date.data
        db.session.commit()
        flash('Transaction updated successfully','success')
        return redirect(url_for('transactions.view_transactions'))
    elif request.method=='GET':
        form.type.data=transaction.type
        form.category.data=transaction.category
        form.amount.data=transaction.amount
        form.description.data=transaction.description
        form.date.data=transaction.date
    return render_template('add_update_transaction.html',form=form,purpose='Update')

@transactions.route('/delete_transaction/<int:trans_id>',methods=['POST'])
def delete_transaction(trans_id):
    transaction=Transaction.query.get_or_404(trans_id)
    if transaction.user_id != current_user.id:
        abort(403)
    db.session.delete(transaction)
    db.session.commit()
    flash('Your transaction is deleted','danger')
    return redirect(url_for('transactions.view_transactions'))

@transactions.route('/transactions/export')
@login_required
def export_transactions():
    # Get filter parameters from URL
    transaction_type = request.args.get('type', '')  # income, expense
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if transaction_type:
        query = query.filter_by(type=transaction_type)
    
    if category:
        query = query.filter_by(category=category)
    
    if date_from:
        try:
            parsed_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Transaction.date >= parsed_date)
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('transactions.view_transactions'))  
          
    if date_to:
        try:
            query = query.filter(Transaction.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('transactions.view_transactions'))
    
    # Order by date descending
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Check if any transactions exist
    if not transactions:
        flash('No transactions to export!', 'warning')
        return redirect(url_for('transactions.view_transactions'))
    
    # Export based on format
    return export_transactions_excel(transactions, current_user.username)