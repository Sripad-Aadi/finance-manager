# Finance Tracker

A comprehensive personal finance management web application built with Flask. Track income and expenses, visualize spending patterns, and manage your financial data efficiently.

## Features

- **User Authentication**: Secure registration and login with password reset functionality
- **Transaction Management**: Add, edit, and delete income/expense transactions
- **Category-based Tracking**: Organize transactions with predefined categories
- **Dashboard Analytics**: View spending patterns, category breakdowns, and financial summaries
- **Data Export**: Export transactions to Excel with detailed summaries
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Security**: CSRF protection, password hashing, and secure session management

## Tech Stack

- **Backend**: Flask 2.3
- **Database**: SQLAlchemy with Flask-SQLAlchemy
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login with Flask-BCrypt
- **Email**: Flask-Mail (for password resets)
- **Data Export**: Pandas and openpyxl
- **Image Processing**: Pillow

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sripad-Aadi/finance-manager.git
   cd FinanceTracker
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv myenv
   myenv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env
   
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

   The application will be available at `http://127.0.0.1:5000`

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///finance_tracker.db
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

### Required Variables Explanation

- **FLASK_ENV**: Set to `development` or `production`
- **SECRET_KEY**: Random string (minimum 32 characters) for session security
- **DATABASE_URL**: Database connection string
- **EMAIL_USER/PASS**: Gmail credentials for password reset emails
- **MAIL_SERVER/PORT**: SMTP server configuration

## Usage

### Creating an Account
1. Click "Register" on the home page
2. Enter username, email, and password
3. Click "Register" to create your account

### Adding Transactions
1. Log in to your account
2. Click "Add Transaction" button
3. Select transaction type (Income/Expense)
4. Choose category
5. Enter amount and description
6. Select date
7. Click "Submit"

### Viewing Analytics
- Dashboard shows spending by category
- View top 3 expense categories
- See recent transactions
- Filter by period (This Month, Last Month, Last 3 Months, This Year, All Time)

### Exporting Data
1. Go to "Transactions" page
2. Apply any filters you want
3. Click "Export" button
4. Excel file will be downloaded with:
   - Transaction details
   - Summary statistics
   - Category breakdown

## File Structure

```
FinanceTracker/
├── app/
│   ├── __init__.py              # App factory and initialization
│   ├── models.py                # Database models
│   ├── forms.py                 # WTForms forms
│   ├── main/
│   │   ├── routes.py            # Main blueprint routes
│   │   └── utilities.py         # Dashboard utilities
│   ├── transactions/
│   │   ├── routes.py            # Transaction routes
│   │   └── utilities.py         # Export and filter utilities
│   ├── users/
│   │   ├── routes.py            # User authentication routes
│   │   └── utilities.py         # User utilities (email, profile pic)
│   ├── static/
│   │   ├── styles.css           # Custom styles
│   │   └── profile_pics/        # User profile pictures
│   └── templates/               # HTML templates
├── config.py                    # Configuration management
├── run.py                       # Application entry point
├── wsgi.py                      # Production WSGI entry point
├── init_db.py                   # Database initialization
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables template
└── README.md                    # This file
```

## Development

### Creating Transactions Programmatically

```python
from app import create_app, db
from app.models import Transaction, TransactionType, User

app = create_app()

with app.app_context():
    user = User.query.first()
    transaction = Transaction(
        type=TransactionType.EXPENSE,
        category='food',
        amount=50.00,
        description='Lunch',
        date=datetime.now().date(),
        user_id=user.id
    )
    db.session.add(transaction)
    db.session.commit()
```

### Running Tests

```bash
# Coming soon - test suite needs to be implemented
python -m pytest
```

## Production Deployment

### Using Gunicorn

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
   ```

### Deploying to Heroku

1. **Create Procfile**
   ```
   web: gunicorn wsgi:app
   ```

2. **Deploy**
   ```bash
   heroku create your-app-name
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   git push heroku main
   ```

### Security Checklist

- [ ] Set `FLASK_ENV=production` in environment
- [ ] Use a strong, random `SECRET_KEY` (32+ characters)
- [ ] Configure HTTPS/SSL
- [ ] Set up database backups
- [ ] Enable email verification for new accounts
- [ ] Configure rate limiting on login endpoints
- [ ] Review security headers configuration
- [ ] Set up monitoring and logging
- [ ] Test all authentication flows
- [ ] Verify CSRF protection is enabled

## Database Models

### User
- `id`: Primary key
- `username`: Unique username (max 20 chars)
- `email`: Unique email address
- `password`: Hashed password
- `image_file`: Profile picture filename
- `created_at`: Account creation timestamp
- `transactions`: Relationship to transactions

### Transaction
- `id`: Primary key
- `user_id`: Foreign key to User
- `type`: Enum (INCOME/EXPENSE)
- `amount`: Decimal amount
- `category`: Category name
- `description`: Transaction description
- `date`: Transaction date
- `created_at`: Record creation timestamp

## Categories

### Expense Categories
- Food
- Entertainment
- Grocery
- Travel
- Transfers
- Investment
- Shopping
- Medical
- Bills
- Miscellaneous

### Income Categories
- Salary
- Freelance
- Business
- Investment Profit
- Gift
- Bonus
- Other Income

## Troubleshooting

### Email Not Sending
- Verify Gmail account credentials
- Enable "Less secure app access" for Gmail
- Use app-specific passwords if 2FA is enabled

### Database Errors
```bash
# Reset database
python init_db.py
```

### Port Already in Use
```bash
# Run on different port
python run.py --port 5001
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.


**Last Updated**: January 2026

