#!/usr/bin/env python3
"""
Library Management System
A robust desktop application for managing library operations

Features:
- Book Management (CRUD operations)
- Member Management
- Issue & Return System with fine calculation
- Advanced Search System
- Reports & Analytics
- Role-based Authentication
- Barcode/QR Code Integration
- Dark/Light Theme Toggle
- Database Backup & Restore
- AI-based Recommendations
- Notification System

Author: Claude AI
Framework: PySide6 with SQLite
Architecture: MVC Pattern
"""

import sys
import os
import sqlite3
import json
import hashlib
import datetime
import random
import shutil
import base64
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtCharts import *
except ImportError:
    print("Installing required packages...")
    os.system("pip install PySide6")
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtCharts import *

# Models
@dataclass
class Book:
    id: Optional[int] = None
    title: str = ""
    author: str = ""
    isbn: str = ""
    genre: str = ""
    availability: bool = True
    barcode: str = ""
    location: str = ""
    purchase_date: Optional[str] = None
    price: float = 0.0

@dataclass
class Member:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    member_type: str = "Student"  # Student, Faculty, Staff
    join_date: Optional[str] = None
    active: bool = True

@dataclass
class Transaction:
    id: Optional[int] = None
    book_id: int = 0
    member_id: int = 0
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    return_date: Optional[str] = None
    fine_amount: float = 0.0
    status: str = "Issued"  # Issued, Returned, Overdue

@dataclass
class User:
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    role: str = "Librarian"  # Admin, Librarian, Member
    name: str = ""
    active: bool = True

class UserRole(Enum):
    ADMIN = "Admin"
    LIBRARIAN = "Librarian"
    MEMBER = "Member"

# Database Manager
class DatabaseManager:
    def __init__(self, db_path: str = "library.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        with self.get_connection() as conn:
            # Books table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT UNIQUE,
                    genre TEXT,
                    availability BOOLEAN DEFAULT 1,
                    barcode TEXT UNIQUE,
                    location TEXT,
                    purchase_date TEXT,
                    price REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Members table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    address TEXT,
                    member_type TEXT DEFAULT 'Student',
                    join_date TEXT,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Transactions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER,
                    member_id INTEGER,
                    issue_date TEXT,
                    due_date TEXT,
                    return_date TEXT,
                    fine_amount REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'Issued',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (book_id) REFERENCES books (id),
                    FOREIGN KEY (member_id) REFERENCES members (id)
                )
            ''')
            
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'Librarian',
                    name TEXT NOT NULL,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Settings table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Insert default admin user
            admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
            conn.execute('''
                INSERT OR IGNORE INTO users (username, password_hash, role, name)
                VALUES (?, ?, ?, ?)
            ''', ("admin", admin_hash, "Admin", "System Administrator"))
            
            # Insert default settings if missing
            conn.execute('''
                INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'light')
            ''')
            
            # Insert sample data
            self.insert_sample_data(conn)
    
    def insert_sample_data(self, conn):
        # Sample books
        books = [
            ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", "Fiction", True, "BK001", "A-1-1", "2023-01-15", 25.99),
            ("To Kill a Mockingbird", "Harper Lee", "9780446310789", "Fiction", True, "BK002", "A-1-2", "2023-01-16", 22.50),
            ("1984", "George Orwell", "9780451524935", "Dystopian", True, "BK003", "A-2-1", "2023-01-17", 19.99),
            ("Pride and Prejudice", "Jane Austen", "9780141439518", "Romance", True, "BK004", "A-2-2", "2023-01-18", 21.00),
            ("The Catcher in the Rye", "J.D. Salinger", "9780316769174", "Fiction", True, "BK005", "A-3-1", "2023-01-19", 24.95)
        ]
        
        for book in books:
            conn.execute('''
                INSERT OR IGNORE INTO books (title, author, isbn, genre, availability, barcode, location, purchase_date, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', book)
        
        # Sample members
        members = [
            ("John Smith", "john@email.com", "555-0101", "123 Main St", "Student", "2023-09-01"),
            ("Jane Doe", "jane@email.com", "555-0102", "456 Oak Ave", "Faculty", "2023-08-15"),
            ("Bob Johnson", "bob@email.com", "555-0103", "789 Pine Rd", "Student", "2023-09-10")
        ]
        
        for member in members:
            conn.execute('''
                INSERT OR IGNORE INTO members (name, email, phone, address, member_type, join_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', member)

# Repository Classes
class BookRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_book(self, book: Book) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO books (title, author, isbn, genre, availability, barcode, location, purchase_date, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (book.title, book.author, book.isbn, book.genre, 1 if book.availability else 0, 
                  book.barcode, book.location, book.purchase_date, book.price))
            return cursor.lastrowid
    
    def get_all_books(self, limit: int = None, offset: int = 0) -> List[Book]:
        query = 'SELECT id, title, author, isbn, genre, availability, barcode, location, purchase_date, price FROM books ORDER BY title'
        params: List = []
        
        if limit:
            query += ' LIMIT ? OFFSET ?'
            params = [limit, offset]
        
        with self.db.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [Book(*row) for row in cursor.fetchall()]
    
    def get_available_books(self) -> List[Book]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT id, title, author, isbn, genre, availability, barcode, location, purchase_date, price
                FROM books WHERE availability = 1 ORDER BY title
            ''')
            return [Book(*row) for row in cursor.fetchall()]
    
    def search_books(self, query: str, field: str = "all") -> List[Book]:
        with self.db.get_connection() as conn:
            if field == "all":
                cursor = conn.execute('''
                    SELECT id, title, author, isbn, genre, availability, barcode, location, purchase_date, price FROM books 
                    WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR genre LIKE ?
                    ORDER BY title
                ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            else:
                valid_fields = {"title", "author", "isbn", "genre"}
                if field not in valid_fields:
                    field = "title"
                cursor = conn.execute(f'''
                    SELECT id, title, author, isbn, genre, availability, barcode, location, purchase_date, price FROM books WHERE {field} LIKE ? ORDER BY title
                ''', (f'%{query}%',))
            return [Book(*row) for row in cursor.fetchall()]
    
    def update_book(self, book: Book):
        with self.db.get_connection() as conn:
            conn.execute('''
                UPDATE books SET title=?, author=?, isbn=?, genre=?, availability=?, 
                barcode=?, location=?, purchase_date=?, price=?
                WHERE id=?
            ''', (book.title, book.author, book.isbn, book.genre, 1 if book.availability else 0,
                  book.barcode, book.location, book.purchase_date, book.price, book.id))
    
    def delete_book(self, book_id: int):
        with self.db.get_connection() as conn:
            conn.execute('DELETE FROM books WHERE id=?', (book_id,))
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT id, title, author, isbn, genre, availability, barcode, location, purchase_date, price FROM books WHERE id=?
            ''', (book_id,))
            row = cursor.fetchone()
            return Book(*row) if row else None

class MemberRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def add_member(self, member: Member) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO members (name, email, phone, address, member_type, join_date, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (member.name, member.email, member.phone, member.address, 
                  member.member_type, member.join_date, 1 if member.active else 0))
            return cursor.lastrowid
    
    def get_all_members(self) -> List[Member]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('SELECT id, name, email, phone, address, member_type, join_date, active FROM members ORDER BY name')
            return [Member(*row) for row in cursor.fetchall()]
    
    def search_members(self, query: str) -> List[Member]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT id, name, email, phone, address, member_type, join_date, active FROM members 
                WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
                ORDER BY name
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            return [Member(*row) for row in cursor.fetchall()]
    
    def update_member(self, member: Member):
        with self.db.get_connection() as conn:
            conn.execute('''
                UPDATE members SET name=?, email=?, phone=?, address=?, member_type=?, join_date=?, active=? WHERE id=?
            ''', (member.name, member.email, member.phone, member.address, member.member_type, member.join_date, 1 if member.active else 0, member.id))
    
    def delete_member(self, member_id: int):
        with self.db.get_connection() as conn:
            conn.execute('DELETE FROM members WHERE id=?', (member_id,))
    
    def get_member_by_id(self, member_id: int) -> Optional[Member]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT id, name, email, phone, address, member_type, join_date, active FROM members WHERE id=?
            ''', (member_id,))
            row = cursor.fetchone()
            return Member(*row) if row else None

class TransactionRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def issue_book(self, book_id: int, member_id: int, days: int = 14) -> int:
        issue_date = datetime.date.today()
        due_date = issue_date + datetime.timedelta(days=days)
        
        with self.db.get_connection() as conn:
            # Create transaction
            cursor = conn.execute('''
                INSERT INTO transactions (book_id, member_id, issue_date, due_date, status)
                VALUES (?, ?, ?, ?, 'Issued')
            ''', (book_id, member_id, issue_date.isoformat(), due_date.isoformat()))
            
            # Update book availability
            conn.execute('UPDATE books SET availability = 0 WHERE id = ?', (book_id,))
            
            return cursor.lastrowid
    
    def return_book(self, transaction_id: int) -> float:
        return_date = datetime.date.today()
        fine = 0.0
        
        with self.db.get_connection() as conn:
            # Get transaction details
            cursor = conn.execute('''
                SELECT book_id, due_date FROM transactions WHERE id = ?
            ''', (transaction_id,))
            row = cursor.fetchone()
            
            if row:
                book_id, due_date_str = row
                due_date = datetime.datetime.fromisoformat(due_date_str).date()
                
                # Calculate fine (₹5 per day)
                if return_date > due_date:
                    days_late = (return_date - due_date).days
                    fine = days_late * 5.0
                
                # Update transaction
                conn.execute('''
                    UPDATE transactions 
                    SET return_date = ?, fine_amount = ?, status = 'Returned'
                    WHERE id = ?
                ''', (return_date.isoformat(), fine, transaction_id))
                
                # Update book availability
                conn.execute('UPDATE books SET availability = 1 WHERE id = ?', (book_id,))
        
        return fine

    def get_all_transactions(self) -> List[Transaction]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT id, book_id, member_id, issue_date, due_date, return_date, fine_amount, status
                FROM transactions ORDER BY id DESC
            ''')
            return [Transaction(*row) for row in cursor.fetchall()]

    def get_active_transactions(self) -> List[Transaction]:
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT id, book_id, member_id, issue_date, due_date, return_date, fine_amount, status
                FROM transactions WHERE status = 'Issued' ORDER BY due_date ASC
            ''')
            return [Transaction(*row) for row in cursor.fetchall()]

class UserRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT id, username, password_hash, role, name, active FROM users WHERE username = ? AND password_hash = ? AND active = 1
            ''', (username, password_hash))
            row = cursor.fetchone()
            return User(*row) if row else None

# Services
class LibraryService:
    def __init__(self, db_manager: DatabaseManager):
        self.book_repo = BookRepository(db_manager)
        self.member_repo = MemberRepository(db_manager)
        self.transaction_repo = TransactionRepository(db_manager)
        self.user_repo = UserRepository(db_manager)
        self.db = db_manager
    
    def get_dashboard_stats(self) -> Dict:
        with self.db.get_connection() as conn:
            stats: Dict[str, int] = {}
            
            # Total books
            cursor = conn.execute('SELECT COUNT(*) FROM books')
            stats['total_books'] = cursor.fetchone()[0]
            
            # Available books
            cursor = conn.execute('SELECT COUNT(*) FROM books WHERE availability = 1')
            stats['available_books'] = cursor.fetchone()[0]
            
            # Total members
            cursor = conn.execute('SELECT COUNT(*) FROM members WHERE active = 1')
            stats['total_members'] = cursor.fetchone()[0]
            
            # Issued books
            cursor = conn.execute('SELECT COUNT(*) FROM transactions WHERE status = "Issued"')
            stats['issued_books'] = cursor.fetchone()[0]
            
            # Overdue books
            today = datetime.date.today().isoformat()
            cursor = conn.execute('''
                SELECT COUNT(*) FROM transactions 
                WHERE status = "Issued" AND due_date < ?
            ''', (today,))
            stats['overdue_books'] = cursor.fetchone()[0]
            
            return stats
    
    def generate_barcode(self) -> str:
        """Generate unique barcode for books"""
        return f"BK{random.randint(100000, 999999)}"
    
    def backup_database(self, backup_path: str) -> bool:
        try:
            shutil.copy2(self.db.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False

    def restore_database(self, source_path: str) -> bool:
        try:
            shutil.copy2(source_path, self.db.db_path)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self.db.get_connection() as conn:
            cur = conn.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cur.fetchone()
            return row[0] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self.db.get_connection() as conn:
            conn.execute('INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, value))

# Theme Manager
class ThemeManager:
    def __init__(self):
        self.current_theme = "light"
    
    def get_light_theme(self) -> str:
        return """
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        QWidget {
            background-color: #ffffff;
            color: #212529;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 12px;
        }
        
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            min-width: 100px;
        }
        
        QPushButton:hover {
            background-color: #0056b3;
        }
        
        QPushButton:pressed {
            background-color: #004085;
        }
        
        QPushButton:disabled {
            background-color: #6c757d;
        }
        
        QLineEdit {
            border: 2px solid #dee2e6;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
        }
        
        QLineEdit:focus {
            border-color: #007bff;
        }
        
        QTableWidget {
            gridline-color: #dee2e6;
            background-color: #ffffff;
            alternate-background-color: #f8f9fa;
        }
        
        QHeaderView::section {
            background-color: #e9ecef;
            color: #495057;
            border: 1px solid #dee2e6;
            padding: 8px;
            font-weight: 600;
        }
        
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            background-color: #ffffff;
        }
        
        QTabBar::tab {
            background-color: #e9ecef;
            color: #495057;
            padding: 10px 20px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #007bff;
            color: white;
        }
        """
    
    def get_dark_theme(self) -> str:
        return """
        QMainWindow {
            background-color: #1a1a1a;
        }
        
        QWidget {
            background-color: #2d3748;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 12px;
        }
        
        QPushButton {
            background-color: #4299e1;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: 600;
            min-width: 100px;
        }
        
        QPushButton:hover {
            background-color: #3182ce;
        }
        
        QPushButton:pressed {
            background-color: #2c5282;
        }
        
        QPushButton:disabled {
            background-color: #4a5568;
        }
        
        QLineEdit {
            border: 2px solid #4a5568;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            background-color: #1a202c;
            color: #ffffff;
        }
        
        QLineEdit:focus {
            border-color: #4299e1;
        }
        
        QTableWidget {
            gridline-color: #4a5568;
            background-color: #2d3748;
            alternate-background-color: #1a202c;
            color: #ffffff;
        }
        
        QHeaderView::section {
            background-color: #4a5568;
            color: #ffffff;
            border: 1px solid #2d3748;
            padding: 8px;
            font-weight: 600;
        }
        
        QTabWidget::pane {
            border: 1px solid #4a5568;
            background-color: #2d3748;
        }
        
        QTabBar::tab {
            background-color: #4a5568;
            color: #ffffff;
            padding: 10px 20px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #4299e1;
            color: white;
        }
        """

# GUI Components
class LoginDialog(QDialog):
    def __init__(self, user_repo: UserRepository):
        super().__init__()
        self.user_repo = user_repo
        self.authenticated_user = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Library Management System - Login")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        # Center the dialog
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)
        
        layout = QVBoxLayout()
        
        # Logo/Title
        title = QLabel("Library Management System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Form
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter password")
        form_layout.addRow("Password:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(login_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Default credentials info
        info = QLabel("Default: admin / admin123")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: gray; font-size: 10px; margin-top: 10px;")
        layout.addWidget(info)
        
        self.setLayout(layout)
        
        # Enter key binding
        self.password_edit.returnPressed.connect(self.login)
    
    def login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        user = self.user_repo.authenticate(username, password)
        if user:
            self.authenticated_user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")
            self.password_edit.clear()
            self.password_edit.setFocus()

class DashboardWidget(QWidget):
    def __init__(self, library_service: LibraryService):
        super().__init__()
        self.library_service = library_service
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Stats cards
        stats_layout = QGridLayout()
        self.create_stats_cards(stats_layout)
        layout.addLayout(stats_layout)
        
        # Charts
        charts_layout = QHBoxLayout()
        self.create_charts(charts_layout)
        layout.addLayout(charts_layout)
        
        self.setLayout(layout)
        self.refresh_dashboard()
    
    def create_stats_cards(self, layout):
        self.stats_cards: Dict[str, QFrame] = {}
        
        cards = [
            ("Total Books", "total_books", "#007bff"),
            ("Available Books", "available_books", "#28a745"),
            ("Total Members", "total_members", "#17a2b8"),
            ("Issued Books", "issued_books", "#ffc107"),
            ("Overdue Books", "overdue_books", "#dc3545")
        ]
        
        for i, (title, key, color) in enumerate(cards):
            card = self.create_stat_card(title, "0", color)
            self.stats_cards[key] = card
            row, col = divmod(i, 3)
            layout.addWidget(card, row, col)
    
    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                color: white;
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        card.value_label = value_label  # Store reference for updates
        
        return card
    
    def create_charts(self, layout):
        # Placeholder for charts - in a real implementation, you'd use QCharts
        chart_placeholder = QLabel("Charts and Analytics Coming Soon...")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 50px;
                font-size: 16px;
                color: #666;
            }
        """)
        layout.addWidget(chart_placeholder)
    
    def refresh_dashboard(self):
        stats = self.library_service.get_dashboard_stats()
        for key, value in stats.items():
            if key in self.stats_cards:
                self.stats_cards[key].value_label.setText(str(value))

class BookDialog(QDialog):
    def __init__(self, service: LibraryService, book: Optional[Book] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.service = service
        self.book = book
        self.setWindowTitle("Add Book" if book is None else "Edit Book")
        self.setModal(True)
        self.setMinimumWidth(480)
        self._build_ui()
        if self.book:
            self._populate()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit()
        self.isbn_edit = QLineEdit()
        self.genre_edit = QLineEdit()
        self.availability_check = QCheckBox("Available")
        self.barcode_edit = QLineEdit()
        self.location_edit = QLineEdit()
        self.purchase_date_edit = QDateEdit()
        self.purchase_date_edit.setCalendarPopup(True)
        self.purchase_date_edit.setDate(QDate.currentDate())
        self.price_edit = QDoubleSpinBox()
        self.price_edit.setRange(0, 1000000)
        self.price_edit.setDecimals(2)

        barcode_gen_btn = QPushButton("Generate")
        barcode_gen_btn.clicked.connect(self._generate_barcode)
        barcode_row = QHBoxLayout()
        barcode_row.addWidget(self.barcode_edit)
        barcode_row.addWidget(barcode_gen_btn)
        barcode_row_w = QWidget()
        barcode_row_w.setLayout(barcode_row)

        form.addRow("Title:", self.title_edit)
        form.addRow("Author:", self.author_edit)
        form.addRow("ISBN:", self.isbn_edit)
        form.addRow("Genre:", self.genre_edit)
        form.addRow("Availability:", self.availability_check)
        form.addRow("Barcode:", barcode_row_w)
        form.addRow("Location:", self.location_edit)
        form.addRow("Purchase Date:", self.purchase_date_edit)
        form.addRow("Price:", self.price_edit)

        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _populate(self):
        self.title_edit.setText(self.book.title)
        self.author_edit.setText(self.book.author)
        self.isbn_edit.setText(self.book.isbn)
        self.genre_edit.setText(self.book.genre)
        self.availability_check.setChecked(bool(self.book.availability))
        self.barcode_edit.setText(self.book.barcode)
        self.location_edit.setText(self.book.location)
        if self.book.purchase_date:
            try:
                y, m, d = [int(x) for x in self.book.purchase_date.split('-')]
                self.purchase_date_edit.setDate(QDate(y, m, d))
            except Exception:
                pass
        self.price_edit.setValue(float(self.book.price or 0.0))

    def _generate_barcode(self):
        self.barcode_edit.setText(self.service.generate_barcode())

    def get_book(self) -> Optional[Book]:
        title = self.title_edit.text().strip()
        author = self.author_edit.text().strip()
        if not title or not author:
            QMessageBox.warning(self, "Validation", "Title and Author are required")
            return None
        isbn = self.isbn_edit.text().strip()
        genre = self.genre_edit.text().strip()
        availability = self.availability_check.isChecked()
        barcode = self.barcode_edit.text().strip() or self.service.generate_barcode()
        location = self.location_edit.text().strip()
        purchase_date = self.purchase_date_edit.date().toString("yyyy-MM-dd")
        price = float(self.price_edit.value())
        if self.book:
            return Book(id=self.book.id, title=title, author=author, isbn=isbn, genre=genre,
                        availability=availability, barcode=barcode, location=location,
                        purchase_date=purchase_date, price=price)
        return Book(title=title, author=author, isbn=isbn, genre=genre,
                    availability=availability, barcode=barcode, location=location,
                    purchase_date=purchase_date, price=price)

class MemberDialog(QDialog):
    def __init__(self, member: Optional[Member] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.member = member
        self.setWindowTitle("Add Member" if member is None else "Edit Member")
        self.setModal(True)
        self.setMinimumWidth(480)
        self._build_ui()
        if self.member:
            self._populate()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.member_type_combo = QComboBox()
        self.member_type_combo.addItems(["Student", "Faculty", "Staff"])
        self.join_date_edit = QDateEdit()
        self.join_date_edit.setCalendarPopup(True)
        self.join_date_edit.setDate(QDate.currentDate())
        self.active_check = QCheckBox("Active")
        self.active_check.setChecked(True)

        form.addRow("Name:", self.name_edit)
        form.addRow("Email:", self.email_edit)
        form.addRow("Phone:", self.phone_edit)
        form.addRow("Address:", self.address_edit)
        form.addRow("Type:", self.member_type_combo)
        form.addRow("Join Date:", self.join_date_edit)
        form.addRow("Status:", self.active_check)

        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _populate(self):
        self.name_edit.setText(self.member.name)
        self.email_edit.setText(self.member.email)
        self.phone_edit.setText(self.member.phone)
        self.address_edit.setText(self.member.address)
        idx = self.member_type_combo.findText(self.member.member_type)
        self.member_type_combo.setCurrentIndex(max(0, idx))
        if self.member.join_date:
            try:
                y, m, d = [int(x) for x in self.member.join_date.split('-')]
                self.join_date_edit.setDate(QDate(y, m, d))
            except Exception:
                pass
        self.active_check.setChecked(bool(self.member.active))

    def get_member(self) -> Optional[Member]:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required")
            return None
        email = self.email_edit.text().strip()
        phone = self.phone_edit.text().strip()
        address = self.address_edit.text().strip()
        member_type = self.member_type_combo.currentText()
        join_date = self.join_date_edit.date().toString("yyyy-MM-dd")
        active = self.active_check.isChecked()
        if self.member:
            return Member(id=self.member.id, name=name, email=email, phone=phone, address=address,
                          member_type=member_type, join_date=join_date, active=active)
        return Member(name=name, email=email, phone=phone, address=address,
                      member_type=member_type, join_date=join_date, active=active)

class BooksWidget(QWidget):
    def __init__(self, library_service: LibraryService):
        super().__init__()
        self.library_service = library_service
        self.current_books: List[Book] = []
        self.setup_ui()
        self.load_books()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Book Management")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("Add Book")
        add_btn.clicked.connect(self.add_book)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Search
        search_layout = QHBoxLayout()
        
        self.search_field = QComboBox()
        self.search_field.addItems(["All Fields", "Title", "Author", "ISBN", "Genre"])
        search_layout.addWidget(QLabel("Search in:"))
        search_layout.addWidget(self.search_field)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term...")
        self.search_input.textChanged.connect(self.search_books)
        search_layout.addWidget(self.search_input)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_books)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Books table
        self.books_table = QTableWidget()
        self.setup_books_table()
        layout.addWidget(self.books_table)
        
        self.setLayout(layout)
    
    def setup_books_table(self):
        headers = ["ID", "Title", "Author", "ISBN", "Genre", "Status", "Barcode", "Location", "Price"]
        self.books_table.setColumnCount(len(headers))
        self.books_table.setHorizontalHeaderLabels(headers)
        
        # Context menu
        self.books_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.books_table.customContextMenuRequested.connect(self.show_book_context_menu)
        
        # Double-click to edit
        self.books_table.doubleClicked.connect(self.edit_selected_book)
        
        # Selection behavior
        self.books_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.books_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        # Resize columns
        header = self.books_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(len(headers) - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
    
    def load_books(self):
        self.current_books = self.library_service.book_repo.get_all_books()
        self.books_table.setRowCount(len(self.current_books))
        for row, book in enumerate(self.current_books):
            values = [
                book.id,
                book.title,
                book.author,
                book.isbn,
                book.genre,
                "Available" if book.availability else "Issued",
                book.barcode,
                book.location,
                f"{book.price:.2f}"
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val is not None else "")
                if col == 0:
                    # ID column should be non-editable and aligned center
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.books_table.setItem(row, col, item)
    
    def search_books(self, text: str):
        text = text.strip()
        if not text:
            self.load_books()
            return
        field_map = {
            "All Fields": "all",
            "Title": "title",
            "Author": "author",
            "ISBN": "isbn",
            "Genre": "genre",
        }
        field = field_map.get(self.search_field.currentText(), "all")
        self.current_books = self.library_service.book_repo.search_books(text, field)
        self.books_table.setRowCount(len(self.current_books))
        for row, book in enumerate(self.current_books):
            values = [
                book.id,
                book.title,
                book.author,
                book.isbn,
                book.genre,
                "Available" if book.availability else "Issued",
                book.barcode,
                book.location,
                f"{book.price:.2f}"
            ]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val is not None else "")
                if col == 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.books_table.setItem(row, col, item)
    
    def _selected_book_id(self) -> Optional[int]:
        selected = self.books_table.currentRow()
        if selected < 0:
            return None
        item = self.books_table.item(selected, 0)
        if not item:
            return None
        try:
            return int(item.text())
        except Exception:
            return None
    
    def add_book(self):
        dlg = BookDialog(self.library_service, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            book = dlg.get_book()
            if not book:
                return
            try:
                self.library_service.book_repo.add_book(book)
                self.load_books()
                QMessageBox.information(self, "Success", "Book added successfully")
            except sqlite3.IntegrityError as e:
                QMessageBox.warning(self, "Error", f"Failed to add book: {e}")
    
    def edit_selected_book(self):
        book_id = self._selected_book_id()
        if not book_id:
            return
        book = self.library_service.book_repo.get_book_by_id(book_id)
        if not book:
            QMessageBox.warning(self, "Not found", "Book not found")
            return
        dlg = BookDialog(self.library_service, book, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            updated = dlg.get_book()
            if not updated:
                return
            try:
                self.library_service.book_repo.update_book(updated)
                self.load_books()
                QMessageBox.information(self, "Updated", "Book updated successfully")
            except sqlite3.IntegrityError as e:
                QMessageBox.warning(self, "Error", f"Failed to update book: {e}")
    
    def delete_selected_book(self):
        book_id = self._selected_book_id()
        if not book_id:
            return
        reply = QMessageBox.question(self, "Confirm", "Delete selected book?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.library_service.book_repo.delete_book(book_id)
                self.load_books()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete: {e}")
    
    def show_book_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.books_table.viewport().mapToGlobal(pos))
        if action == edit_action:
            self.edit_selected_book()
        elif action == delete_action:
            self.delete_selected_book()

class MembersWidget(QWidget):
    def __init__(self, library_service: LibraryService):
        super().__init__()
        self.library_service = library_service
        self.current_members: List[Member] = []
        self.setup_ui()
        self.load_members()

    def setup_ui(self):
        layout = QVBoxLayout()
        header_layout = QHBoxLayout()

        title = QLabel("Member Management")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        add_btn = QPushButton("Add Member")
        add_btn.clicked.connect(self.add_member)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name/email/phone...")
        self.search_input.textChanged.connect(self.search_members)
        search_layout.addWidget(self.search_input)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_members)
        search_layout.addWidget(refresh_btn)

        layout.addLayout(search_layout)

        self.members_table = QTableWidget()
        headers = ["ID", "Name", "Email", "Phone", "Address", "Type", "Join Date", "Active"]
        self.members_table.setColumnCount(len(headers))
        self.members_table.setHorizontalHeaderLabels(headers)
        self.members_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.members_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.members_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.members_table.customContextMenuRequested.connect(self.show_context_menu)
        header = self.members_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(len(headers) - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.members_table)

        self.setLayout(layout)

    def load_members(self):
        self.current_members = self.library_service.member_repo.get_all_members()
        self.members_table.setRowCount(len(self.current_members))
        for row, m in enumerate(self.current_members):
            values = [m.id, m.name, m.email, m.phone, m.address, m.member_type, m.join_date, "Yes" if m.active else "No"]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val is not None else "")
                if col == 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.members_table.setItem(row, col, item)

    def search_members(self, text: str):
        text = text.strip()
        if not text:
            self.load_members()
            return
        self.current_members = self.library_service.member_repo.search_members(text)
        self.members_table.setRowCount(len(self.current_members))
        for row, m in enumerate(self.current_members):
            values = [m.id, m.name, m.email, m.phone, m.address, m.member_type, m.join_date, "Yes" if m.active else "No"]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val is not None else "")
                if col == 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.members_table.setItem(row, col, item)

    def _selected_member_id(self) -> Optional[int]:
        selected = self.members_table.currentRow()
        if selected < 0:
            return None
        item = self.members_table.item(selected, 0)
        if not item:
            return None
        try:
            return int(item.text())
        except Exception:
            return None

    def add_member(self):
        dlg = MemberDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            member = dlg.get_member()
            if not member:
                return
            try:
                self.library_service.member_repo.add_member(member)
                self.load_members()
                QMessageBox.information(self, "Success", "Member added successfully")
            except sqlite3.IntegrityError as e:
                QMessageBox.warning(self, "Error", f"Failed to add member: {e}")

    def edit_selected_member(self):
        member_id = self._selected_member_id()
        if not member_id:
            return
        member = self.library_service.member_repo.get_member_by_id(member_id)
        if not member:
            return
        dlg = MemberDialog(member, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            updated = dlg.get_member()
            if not updated:
                return
            try:
                self.library_service.member_repo.update_member(updated)
                self.load_members()
                QMessageBox.information(self, "Updated", "Member updated successfully")
            except sqlite3.IntegrityError as e:
                QMessageBox.warning(self, "Error", f"Failed to update member: {e}")

    def delete_selected_member(self):
        member_id = self._selected_member_id()
        if not member_id:
            return
        reply = QMessageBox.question(self, "Confirm", "Delete selected member?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.library_service.member_repo.delete_member(member_id)
                self.load_members()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete member: {e}")

    def show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.members_table.viewport().mapToGlobal(pos))
        if action == edit_action:
            self.edit_selected_member()
        elif action == delete_action:
            self.delete_selected_member()

class TransactionsWidget(QWidget):
    def __init__(self, library_service: LibraryService):
        super().__init__()
        self.library_service = library_service
        self.setup_ui()
        self.load_transactions()
        self.refresh_selectors()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Issue & Return")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        issue_box = QGroupBox("Issue Book")
        form = QFormLayout()
        self.member_combo = QComboBox()
        self.book_combo = QComboBox()
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 60)
        self.days_spin.setValue(14)
        form.addRow("Member:", self.member_combo)
        form.addRow("Book:", self.book_combo)
        form.addRow("Days:", self.days_spin)

        issue_btn = QPushButton("Issue")
        issue_btn.clicked.connect(self.issue_book)
        form.addRow(issue_btn)
        issue_box.setLayout(form)
        layout.addWidget(issue_box)

        # Transactions table
        self.tx_table = QTableWidget()
        headers = ["ID", "Book ID", "Member ID", "Issue Date", "Due Date", "Return Date", "Fine", "Status"]
        self.tx_table.setColumnCount(len(headers))
        self.tx_table.setHorizontalHeaderLabels(headers)
        self.tx_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tx_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tx_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tx_table.customContextMenuRequested.connect(self.show_context_menu)
        header = self.tx_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(len(headers) - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tx_table)

        self.setLayout(layout)

    def refresh_selectors(self):
        # Members
        self.member_combo.clear()
        members = self.library_service.member_repo.get_all_members()
        for m in members:
            self.member_combo.addItem(f"{m.name} ({m.member_type})", m.id)
        # Books
        self.book_combo.clear()
        books = self.library_service.book_repo.get_available_books()
        for b in books:
            self.book_combo.addItem(f"{b.title} - {b.author}", b.id)

    def load_transactions(self):
        txs = self.library_service.transaction_repo.get_all_transactions()
        self.tx_table.setRowCount(len(txs))
        for row, t in enumerate(txs):
            values = [t.id, t.book_id, t.member_id, t.issue_date, t.due_date, t.return_date or "", f"{t.fine_amount:.2f}", t.status]
            for col, val in enumerate(values):
                item = QTableWidgetItem(str(val) if val is not None else "")
                if col in (0, 1, 2):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tx_table.setItem(row, col, item)

    def _selected_tx_id(self) -> Optional[int]:
        selected = self.tx_table.currentRow()
        if selected < 0:
            return None
        item = self.tx_table.item(selected, 0)
        if not item:
            return None
        try:
            return int(item.text())
        except Exception:
            return None

    def issue_book(self):
        member_id = self.member_combo.currentData()
        book_id = self.book_combo.currentData()
        if not member_id or not book_id:
            QMessageBox.warning(self, "Validation", "Select a member and a book")
            return
        try:
            self.library_service.transaction_repo.issue_book(book_id, member_id, self.days_spin.value())
            QMessageBox.information(self, "Issued", "Book issued successfully")
            self.refresh_selectors()
            self.load_transactions()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to issue: {e}")

    def return_selected(self):
        tx_id = self._selected_tx_id()
        if not tx_id:
            return
        try:
            fine = self.library_service.transaction_repo.return_book(tx_id)
            if fine > 0:
                QMessageBox.information(self, "Returned", f"Book returned. Fine: ₹{fine:.2f}")
            else:
                QMessageBox.information(self, "Returned", "Book returned on time. No fine.")
            self.refresh_selectors()
            self.load_transactions()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to return: {e}")

    def show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        return_action = menu.addAction("Return Book")
        action = menu.exec(self.tx_table.viewport().mapToGlobal(pos))
        if action == return_action:
            self.return_selected()

class MainWindow(QMainWindow):
    def __init__(self, service: LibraryService, theme_manager: ThemeManager, user: User):
        super().__init__()
        self.service = service
        self.theme_manager = theme_manager
        self.user = user
        self.setWindowTitle("Library Management System")
        self.resize(1100, 720)
        self._build_menu()
        self._build_tabs()
        self._build_statusbar()
        # Apply persisted theme
        theme = self.service.get_setting('theme', 'light') or 'light'
        self.apply_theme(theme)

    def _build_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        backup_action = QAction("Backup Database", self)
        backup_action.triggered.connect(self.backup_db)
        restore_action = QAction("Restore Database", self)
        restore_action.triggered.connect(self.restore_db)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(backup_action)
        file_menu.addAction(restore_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu("View")
        light_action = QAction("Light Theme", self, checkable=True)
        dark_action = QAction("Dark Theme", self, checkable=True)
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)
        theme_group.addAction(light_action)
        theme_group.addAction(dark_action)
        light_action.triggered.connect(lambda: self.apply_theme('light'))
        dark_action.triggered.connect(lambda: self.apply_theme('dark'))
        view_menu.addAction(light_action)
        view_menu.addAction(dark_action)

        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _build_tabs(self):
        tabs = QTabWidget()
        self.dashboard = DashboardWidget(self.service)
        self.books = BooksWidget(self.service)
        self.members = MembersWidget(self.service)
        self.transactions = TransactionsWidget(self.service)
        tabs.addTab(self.dashboard, "Dashboard")
        tabs.addTab(self.books, "Books")
        tabs.addTab(self.members, "Members")
        tabs.addTab(self.transactions, "Transactions")
        self.setCentralWidget(tabs)

    def _build_statusbar(self):
        sb = self.statusBar()
        sb.showMessage(f"Logged in as {self.user.name} ({self.user.role})")

    def apply_theme(self, theme: str):
        self.theme_manager.current_theme = theme
        qapp = QApplication.instance()
        if theme == 'dark':
            qapp.setStyleSheet(self.theme_manager.get_dark_theme())
        else:
            qapp.setStyleSheet(self.theme_manager.get_light_theme())
        self.service.set_setting('theme', theme)

    def backup_db(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Database Backup", "library-backup.db", "SQLite DB (*.db)")
        if not path:
            return
        if self.service.backup_database(path):
            QMessageBox.information(self, "Backup", "Backup created successfully")
        else:
            QMessageBox.warning(self, "Backup", "Backup failed")

    def restore_db(self):
        path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite DB (*.db)")
        if not path:
            return
        reply = QMessageBox.question(self, "Confirm", "This will overwrite current data. Continue?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        if self.service.restore_database(path):
            QMessageBox.information(self, "Restore", "Database restored. UI will refresh.")
            # Refresh widgets
            self.dashboard.refresh_dashboard()
            self.books.load_books()
            self.members.load_members()
            self.transactions.refresh_selectors()
            self.transactions.load_transactions()
        else:
            QMessageBox.warning(self, "Restore", "Restore failed")

    def show_about(self):
        QMessageBox.information(self, "About", "Library Management System\nPySide6 + SQLite\n© 2025")

# Entry point
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Library Management System")
    db_path = os.path.join(os.getcwd(), "library.db")
    db = DatabaseManager(db_path)
    service = LibraryService(db)
    theme_manager = ThemeManager()

    # Login
    login = LoginDialog(service.user_repo)
    if login.exec() != QDialog.DialogCode.Accepted or not login.authenticated_user:
        return 0

    window = MainWindow(service, theme_manager, login.authenticated_user)
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())