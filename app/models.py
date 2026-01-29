import enum
from datetime import datetime
from app import db,login_manager
from flask_login import UserMixin
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
import logging
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class TransactionType(str,enum.Enum):
    EXPENSE='expense'
    INCOME='income'
    

class IncomeCategory(str, enum.Enum):
    SALARY ='salary'
    FREELANCE = 'freelance'
    BUSINESS = 'business'
    INVESTMENT_PROFIT = 'investment_profit'
    GIFT = 'gift'
    BONUS = 'bonus'
    OTHERS = 'other_income'
    
class ExpenseCategory(str,enum.Enum):
    FOOD='food'
    ENTERTAINMENT='entertainment'
    GROCERY='grocery'
    TRAVEL='travel'
    TRANSFERS='transfers'
    INVESTMENT='investment'
    SHOPPING='shopping'
    MEDICAL='medical'
    BILLS='bills'
    MISCELLANEOUS='miscellaneous'
    OTHERS='other_expense'

class User(db.Model,UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(60),nullable=False)
    image_file=db.Column(db.String(20),default="default.jpg",nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    transactions=db.relationship("Transaction",backref="user",lazy=True,cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"User({self.username},{self.email})"
    
    def get_reset_token(self):
        s=Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id':self.id},salt='password-reset-salt')
    @staticmethod
    def verify_reset_token(token,expires_in=600):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token,salt='password-reset-salt',max_age=expires_in)['user_id']
        except (ValueError, TypeError) as e:
            logger.error(f"Token verification failed: {e}")
            return None
        return User.query.get(user_id)
    

class Transaction(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    type=db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(10, 2),nullable=False)
    category=db.Column(db.String(50),nullable=False)
    description=db.Column(db.Text)
    date = db.Column(db.Date)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Transaction({self.type},{self.amount},{self.category})"
    
    