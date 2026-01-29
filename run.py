import os
from dotenv import load_dotenv
from app import create_app
from app.main.utilities import get_category_color,get_category_icon

load_dotenv()

app=create_app()

@app.context_processor
def utility_processor():
    return {
        'get_category_icon': get_category_icon,
        'get_category_color': get_category_color
    }

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__== '__main__':
    is_production = os.getenv('FLASK_ENV') == 'production'
    is_dev = os.getenv('FLASK_ENV') == 'development'
    
    app.run(
        debug=is_dev,
        host='0.0.0.0' if is_production else '127.0.0.1',
        port=int(os.getenv('PORT', 5000)),
        use_reloader=is_dev
    )