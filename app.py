# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort, send_from_directory, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

# Import the CryptoAdvisor class and CryptoAPI class
from crypto_advisor import CryptoAdvisor
from crypto_api import CryptoAPI
from models import db, User # Assuming models.py correctly defines db and User

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crypto_buddy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app) # Initialize SQLAlchemy with the Flask app
login_manager = LoginManager()
login_manager.init_app(app) # Initialize LoginManager with the Flask app
login_manager.login_view = 'login'

# For Flask-Session, if you intend to use it for server-side sessions
# If you don't explicitly use `session` from `flask_session`, you might not need this.
# app.config['SESSION_TYPE'] = 'filesystem' # Or 'sqlalchemy', 'redis', etc.
# from flask_session import Session
# Session(app) # Initialize Flask-Session with the Flask app


# Create database tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created successfully")

# Initialize crypto components
# Pass the crypto_api instance to CryptoAdvisor, as it depends on it.
crypto_api = CryptoAPI()
crypto_advisor = CryptoAdvisor(crypto_api_instance=crypto_api)

# Serve static files
@app.route('/static/images/crypto/<path:filename>')
def serve_crypto_image(filename):
    return send_from_directory('static/images/crypto', filename)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500

@app.errorhandler(401)
def unauthorized_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required'}), 401
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('auth.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400

        if '@' not in data['email'] or '.' not in data['email']:
            return jsonify({'error': 'Invalid email format'}), 400

        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return jsonify(user.to_dict())

    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'An error occurred during registration'}), 500

@app.route('/api/login', methods=['POST'])
def login_api():
    try:
        data = request.get_json()
        if not data:
            logger.warning("Login attempt with no data provided")
            return jsonify({'error': 'No data provided'}), 400

        if 'username' not in data or 'password' not in data:
            logger.warning("Login attempt with missing fields")
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=data['username']).first()
        
        if not user:
            logger.warning(f"Login attempt with non-existent username: {data['username']}")
            return jsonify({'error': 'Invalid username or password'}), 401

        if not user.check_password(data['password']):
            logger.warning(f"Invalid password attempt for user: {data['username']}")
            return jsonify({'error': 'Invalid username or password'}), 401

        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        logger.info(f"User {user.username} logged in successfully")
        return jsonify(user.to_dict())

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'An error occurred during login'}), 500

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/user')
def get_user():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(current_user.to_dict())

@app.route('/api/query', methods=['POST'])
@login_required
def query():
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
            
        query = data['query']
        # Call the process_query method on the crypto_advisor instance
        response = crypto_advisor.process_query(query)
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({'error': 'An error occurred while processing your query'}), 500

@app.route('/api/market-data')
@login_required
def market_data():
    try:
        # Call the get_market_data method on the crypto_api instance
        data = crypto_api.get_market_data()
        if not data:
            return jsonify({'error': 'Failed to fetch market data'}), 500
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in market_data endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/trending')
@login_required
def get_trending():
    try:
        # Call the get_trending_coins method on the crypto_api instance
        data = crypto_api.get_trending_coins()
        if not data: # crypto_api.get_trending_coins already returns an empty list if there's an error
            return jsonify({'trending_coins': []}) # Return an empty list to frontend
        
        # Limit to top 5, as in your original app.py logic
        trending_coins_formatted = []
        for coin in data[:5]:
            trending_coins_formatted.append({
                'id': coin.get('id'),
                'name': coin.get('name'),
                'symbol': coin.get('symbol'),
                'market_cap_rank': coin.get('market_cap_rank'),
                'price_btc': coin.get('price_btc'), # crypto_api.py's get_trending_coins doesn't directly return price_btc
                'score': coin.get('score'), # crypto_api.py's get_trending_coins doesn't directly return score
                'price_change_percentage_24h': coin.get('price_change_percentage_24h', 0) # This comes from the market data merge in CryptoAdvisor
            })

        return jsonify(trending_coins_formatted)
            
    except Exception as e:
        logger.error(f"Error in get_trending: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/coin/<coin_id>')
@login_required
def coin_info(coin_id):
    try:
        # Call the get_coin_info method on the crypto_api instance
        data = crypto_api.get_coin_info(coin_id)
        if not data:
            return jsonify({'error': 'Failed to fetch coin information'}), 500
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in coin_info endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/coin/<coin_id>/history')
@login_required
def coin_history(coin_id):
    try:
        days = request.args.get('days', default=30, type=int)
        # Call the get_coin_history method on the crypto_api instance
        data = crypto_api.get_coin_history(coin_id, days)
        if not data:
            return jsonify({'error': 'Failed to fetch coin history'}), 500
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error in coin_history endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)