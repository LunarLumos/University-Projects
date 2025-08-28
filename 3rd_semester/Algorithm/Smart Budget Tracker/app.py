from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import User, Income, Expense, DailyBudget, MonthlyBudget, YearlyBudget, FinanceManager, ReportGenerator
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.get_by_username(username)
        if user and user.verify_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('signup.html')
        
        # Check if username already exists
        if User.get_by_username(username):
            flash('Username already exists.', 'danger')
            return render_template('signup.html')
        
        # Create new user
        password_hash = User.hash_password(password)
        user = User(username=username, email=email, password_hash=password_hash)
        user.save()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    finance_manager = FinanceManager(user_id)
    
    # Get financial summary
    balance = finance_manager.get_balance()
    recent_transactions = finance_manager.get_recent_transactions(10)
    
    # Get income and expense totals
    income_data = finance_manager.get_category_summary('income')
    expense_data = finance_manager.get_category_summary('expense')
    
    total_income = sum(item['total'] for item in income_data)
    total_expenses = sum(item['total'] for item in expense_data)
    
    # Check for budget alerts
    alerts = finance_manager.check_budget_alerts()
    
    return render_template('dashboard.html', 
                         balance=balance,
                         total_income=total_income,
                         total_expenses=total_expenses,
                         recent_transactions=recent_transactions,
                         alerts=alerts)

@app.route('/add_income', methods=['GET', 'POST'])
@login_required
def add_income():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        date_str = request.form.get('date')
        
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None
        
        finance_manager = FinanceManager(session['user_id'])
        finance_manager.add_income(amount, category, description, date)
        
        flash('Income added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Pass today's date to the template
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_income.html', today=today)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        date_str = request.form.get('date')
        
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None
        
        finance_manager = FinanceManager(session['user_id'])
        finance_manager.add_expense(amount, category, description, date)
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Pass today's date to the template
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_expense.html', today=today)

@app.route('/add_budget', methods=['GET', 'POST'])
@login_required
def add_budget():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        period = request.form['period']
        
        user_id = session['user_id']
        
        if period == 'daily':
            budget = DailyBudget(user_id, category, amount)
        elif period == 'monthly':
            budget = MonthlyBudget(user_id, category, amount)
        else:  # yearly
            budget = YearlyBudget(user_id, category, amount)
        
        budget.save()
        
        flash(f'{period.capitalize()} budget set for {category}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_budget.html')

@app.route('/reports')
@login_required
def reports():
    user_id = session['user_id']
    report_generator = ReportGenerator(user_id)
    
    # Get spending by category report
    spending_report = report_generator.generate_spending_by_category_report()
    
    # Get income vs expense report
    income_vs_expense = report_generator.generate_income_vs_expense_report()
    
    return render_template('reports.html', 
                         spending_report=spending_report,
                         income_vs_expense=income_vs_expense)

@app.route('/delete_transaction/<int:transaction_id>')
@login_required
def delete_transaction(transaction_id):
    Transaction.delete(transaction_id, session['user_id'])
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)