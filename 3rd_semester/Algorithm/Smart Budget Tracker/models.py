import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, date
import hashlib
import json
from typing import List, Dict, Any

class Database:
    """Database connection manager"""
    def __init__(self, db_name='finance.db'):
        self.db_name = db_name
        self.create_tables()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        with self.get_connection() as conn:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Transactions table (for both income and expenses)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Budgets table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    period TEXT NOT NULL CHECK(period IN ('daily', 'monthly', 'yearly')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()


class User:
    """User class for authentication and user management"""
    def __init__(self, id=None, username=None, email=None, password_hash=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
    
    @staticmethod
    def hash_password(password):
        """Hash a password for storing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password):
        """Verify a stored password against one provided by user"""
        return self.password_hash == self.hash_password(password)
    
    def save(self):
        """Save user to database"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            if self.id is None:
                cursor.execute(
                    'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                    (self.username, self.email, self.password_hash)
                )
                self.id = cursor.lastrowid
            else:
                cursor.execute(
                    'UPDATE users SET username=?, email=?, password_hash=? WHERE id=?',
                    (self.username, self.email, self.password_hash, self.id)
                )
            conn.commit()
    
    @staticmethod
    def get_by_username(username):
        """Get a user by username"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                return User(id=row['id'], username=row['username'], 
                           email=row['email'], password_hash=row['password_hash'],
                           created_at=row['created_at'])
            return None
    
    @staticmethod
    def get_by_id(user_id):
        """Get a user by ID"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return User(id=row['id'], username=row['username'], 
                           email=row['email'], password_hash=row['password_hash'],
                           created_at=row['created_at'])
            return None


class Transaction(ABC):
    """Abstract base class for transactions"""
    def __init__(self, user_id, amount, category, description, date=None):
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date or datetime.now()
    
    @abstractmethod
    def save(self):
        pass
    
    @staticmethod
    def get_all_by_user(user_id, limit=None, type_filter=None):
        """Get all transactions for a user, optionally filtered by type"""
        with Database().get_connection() as conn:
            query = 'SELECT * FROM transactions WHERE user_id = ?'
            params = [user_id]
            
            if type_filter:
                query += ' AND type = ?'
                params.append(type_filter)
            
            query += ' ORDER BY date DESC'
            
            if limit:
                query += ' LIMIT ?'
                params.append(limit)
                
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    @staticmethod
    def delete(transaction_id, user_id):
        """Delete a transaction"""
        with Database().get_connection() as conn:
            conn.execute(
                'DELETE FROM transactions WHERE id = ? AND user_id = ?',
                (transaction_id, user_id)
            )
            conn.commit()


class Income(Transaction):
    """Income transaction class"""
    def __init__(self, user_id, amount, category, description, date=None):
        super().__init__(user_id, amount, category, description, date)
        self.type = 'income'
    
    def save(self):
        """Save income to database"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO transactions (user_id, type, amount, category, description, date) VALUES (?, ?, ?, ?, ?, ?)',
                (self.user_id, self.type, self.amount, self.category, self.description, self.date)
            )
            conn.commit()
            return cursor.lastrowid


class Expense(Transaction):
    """Expense transaction class"""
    def __init__(self, user_id, amount, category, description, date=None):
        super().__init__(user_id, amount, category, description, date)
        self.type = 'expense'
    
    def save(self):
        """Save expense to database"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO transactions (user_id, type, amount, category, description, date) VALUES (?, ?, ?, ?, ?, ?)',
                (self.user_id, self.type, self.amount, self.category, self.description, self.date)
            )
            conn.commit()
            return cursor.lastrowid


class Budget(ABC):
    """Abstract base class for budgets"""
    def __init__(self, user_id, category, amount, period):
        self.user_id = user_id
        self.category = category
        self.amount = amount
        self.period = period
    
    @abstractmethod
    def save(self):
        pass
    
    @staticmethod
    def get_all_by_user(user_id):
        """Get all budgets for a user"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM budgets WHERE user_id = ? ORDER BY period, category',
                (user_id,)
            )
            return cursor.fetchall()
    
    @staticmethod
    def get_by_category(user_id, category, period):
        """Get a budget for a specific category and period"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM budgets WHERE user_id = ? AND category = ? AND period = ?',
                (user_id, category, period)
            )
            return cursor.fetchone()
    
    @staticmethod
    def delete(budget_id, user_id):
        """Delete a budget"""
        with Database().get_connection() as conn:
            conn.execute(
                'DELETE FROM budgets WHERE id = ? AND user_id = ?',
                (budget_id, user_id)
            )
            conn.commit()


class DailyBudget(Budget):
    """Daily budget class"""
    def __init__(self, user_id, category, amount):
        super().__init__(user_id, category, amount, 'daily')
    
    def save(self):
        """Save daily budget to database"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            # Check if budget already exists for this category and period
            existing = Budget.get_by_category(self.user_id, self.category, self.period)
            if existing:
                cursor.execute(
                    'UPDATE budgets SET amount = ? WHERE id = ?',
                    (self.amount, existing['id'])
                )
            else:
                cursor.execute(
                    'INSERT INTO budgets (user_id, category, amount, period) VALUES (?, ?, ?, ?)',
                    (self.user_id, self.category, self.amount, self.period)
                )
            conn.commit()


class MonthlyBudget(Budget):
    """Monthly budget class"""
    def __init__(self, user_id, category, amount):
        super().__init__(user_id, category, amount, 'monthly')
    
    def save(self):
        """Save monthly budget to database"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            # Check if budget already exists for this category and period
            existing = Budget.get_by_category(self.user_id, self.category, self.period)
            if existing:
                cursor.execute(
                    'UPDATE budgets SET amount = ? WHERE id = ?',
                    (self.amount, existing['id'])
                )
            else:
                cursor.execute(
                    'INSERT INTO budgets (user_id, category, amount, period) VALUES (?, ?, ?, ?)',
                    (self.user_id, self.category, self.amount, self.period)
                )
            conn.commit()


class YearlyBudget(Budget):
    """Yearly budget class"""
    def __init__(self, user_id, category, amount):
        super().__init__(user_id, category, amount, 'yearly')
    
    def save(self):
        """Save yearly budget to database"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            # Check if budget already exists for this category and period
            existing = Budget.get_by_category(self.user_id, self.category, self.period)
            if existing:
                cursor.execute(
                    'UPDATE budgets SET amount = ? WHERE id = ?',
                    (self.amount, existing['id'])
                )
            else:
                cursor.execute(
                    'INSERT INTO budgets (user_id, category, amount, period) VALUES (?, ?, ?, ?)',
                    (self.user_id, self.category, self.amount, self.period)
                )
            conn.commit()


class FinanceManager:
    """Main class for managing all financial operations"""
    def __init__(self, user_id):
        self.user_id = user_id
    
    def add_income(self, amount, category, description, date=None):
        """Add an income transaction"""
        income = Income(self.user_id, amount, category, description, date)
        return income.save()
    
    def add_expense(self, amount, category, description, date=None):
        """Add an expense transaction"""
        expense = Expense(self.user_id, amount, category, description, date)
        return expense.save()
    
    def get_balance(self):
        """Calculate current balance (total income - total expenses)"""
        with Database().get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total income
            cursor.execute(
                'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "income"',
                (self.user_id,)
            )
            total_income = cursor.fetchone()['total']
            
            # Get total expenses
            cursor.execute(
                'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "expense"',
                (self.user_id,)
            )
            total_expenses = cursor.fetchone()['total']
            
            return total_income - total_expenses
    
    def get_recent_transactions(self, limit=10):
        """Get recent transactions"""
        return Transaction.get_all_by_user(self.user_id, limit)
    
    def get_transactions_by_type(self, type_filter, limit=None):
        """Get transactions filtered by type"""
        return Transaction.get_all_by_user(self.user_id, limit, type_filter)
    
    def get_category_summary(self, type_filter, start_date=None, end_date=None):
        """Get summary of transactions by category"""
        with Database().get_connection() as conn:
            query = '''
                SELECT category, SUM(amount) as total 
                FROM transactions 
                WHERE user_id = ? AND type = ?
            '''
            params = [self.user_id, type_filter]
            
            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)
            
            query += ' GROUP BY category ORDER BY total DESC'
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def check_budget_alerts(self):
        """Check if expenses exceed 40% of income in any category"""
        alerts = []
        
        # Get total income
        total_income = 0
        income_data = self.get_category_summary('income')
        for item in income_data:
            total_income += item['total']
        
        if total_income == 0:
            return alerts
        
        # Get expenses by category
        expenses_by_category = self.get_category_summary('expense')
        
        for expense in expenses_by_category:
            category = expense['category']
            expense_total = expense['total']
            
            # Check if expenses exceed 40% of total income
            if expense_total > 0.4 * total_income:
                alerts.append({
                    'category': category,
                    'expense_total': expense_total,
                    'percentage': (expense_total / total_income) * 100
                })
        
        return alerts


class ReportGenerator:
    """Class for generating financial reports"""
    def __init__(self, user_id):
        self.user_id = user_id
        self.finance_manager = FinanceManager(user_id)
    
    def generate_spending_by_category_report(self, period='monthly'):
        """Generate spending by category report"""
        now = datetime.now()
        
        if period == 'daily':
            start_date = datetime(now.year, now.month, now.day)
            end_date = datetime(now.year, now.month, now.day, 23, 59, 59)
        elif period == 'monthly':
            start_date = datetime(now.year, now.month, 1)
            next_month = now.month + 1 if now.month < 12 else 1
            next_year = now.year if now.month < 12 else now.year + 1
            end_date = datetime(next_year, next_month, 1)
        else:  # yearly
            start_date = datetime(now.year, 1, 1)
            end_date = datetime(now.year, 12, 31, 23, 59, 59)
        
        expenses = self.finance_manager.get_category_summary(
            'expense', start_date, end_date
        )
        
        return {
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'data': expenses
        }
    
    def generate_income_vs_expense_report(self, period='monthly'):
        """Generate income vs expense report over time"""
        now = datetime.now()
        
        if period == 'monthly':
            # Get data for the last 6 months
            months = []
            income_data = []
            expense_data = []
            
            for i in range(5, -1, -1):
                month = now.month - i
                year = now.year
                if month <= 0:
                    month += 12
                    year -= 1
                
                start_date = datetime(year, month, 1)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1)
                else:
                    end_date = datetime(year, month + 1, 1)
                
                # Get income for the month
                income = self.finance_manager.get_category_summary(
                    'income', start_date, end_date
                )
                total_income = sum(item['total'] for item in income)
                
                # Get expenses for the month
                expenses = self.finance_manager.get_category_summary(
                    'expense', start_date, end_date
                )
                total_expenses = sum(item['total'] for item in expenses)
                
                months.append(f"{year}-{month:02d}")
                income_data.append(total_income)
                expense_data.append(total_expenses)
            
            return {
                'labels': months,
                'income': income_data,
                'expenses': expense_data
            }
        
        # For other periods, you could implement similar logic
        return {}
    
    def export_to_csv(self, data, filename):
        """Export data to CSV format"""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            if 'data' in data:
                writer.writerow(['Category', 'Amount'])
                for item in data['data']:
                    writer.writerow([item['category'], item['total']])
            elif 'labels' in data:
                writer.writerow(['Period', 'Income', 'Expenses'])
                for i in range(len(data['labels'])):
                    writer.writerow([
                        data['labels'][i],
                        data['income'][i],
                        data['expenses'][i]
                    ])
        
        return filename
    
    def export_to_json(self, data, filename):
        """Export data to JSON format"""
        with open(filename, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=4, default=str)
        
        return filename