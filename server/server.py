from flask import Flask, request, jsonify, send_from_directory
import os

# Support running as a module (python -m server.server) or as a script
try:
    from . import util  # type: ignore
except ImportError:
    import util  # type: ignore

# Get the parent directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# API routes (must be defined before catch-all route)
@app.route('/api/get_location_names', methods=['GET'])
def get_location_names():
    response = jsonify({
        'locations': util.get_location_names()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response

@app.route('/api/predict_home_price', methods=['GET', 'POST'])
def predict_home_price():
    try:
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            total_sqft = float(data.get('total_sqft'))
            location = data.get('location')
            bhk = int(data.get('bhk'))
            bath = int(data.get('bath'))
        else:
            total_sqft = float(request.form.get('total_sqft'))
            location = request.form.get('location')
            bhk = int(request.form.get('bhk'))
            bath = int(request.form.get('bath'))

        print(f"Received request: sqft={total_sqft}, location={location}, bhk={bhk}, bath={bath}")
        
        if not location:
            raise ValueError("Location is required")
        
        estimated_price = util.get_estimated_price(location, total_sqft, bhk, bath)
        
        print(f"Estimated price: {estimated_price}")
        
        response = jsonify({
            'estimated_price': estimated_price
        })
        response.headers.add('Access-Control-Allow-Origin', '*')

        return response
    except KeyError as e:
        error_msg = f"Missing required parameter: {str(e)}"
        print(f"Error in predict_home_price: {error_msg}")
        response = jsonify({
            'error': error_msg,
            'estimated_price': None
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.status_code = 400
        return response
    except Exception as e:
        error_msg = str(e)
        print(f"Error in predict_home_price: {error_msg}")
        import traceback
        traceback.print_exc()
        response = jsonify({
            'error': error_msg,
            'estimated_price': None
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.status_code = 500
        return response

# Serve HTML files
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'real.html')  # Serve real.html as homepage

@app.route('/index.html')
def index_alt():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/app.html')
def app_page():
    return send_from_directory(BASE_DIR, 'app.html')

@app.route('/real.html')
def real_page():
    return send_from_directory(BASE_DIR, 'real.html')

@app.route('/listings.html')
def listings_page():
    return send_from_directory(BASE_DIR, 'listings.html')

@app.route('/contact.html')
def contact_page():
    return send_from_directory(BASE_DIR, 'contact.html')

# Serve static files (CSS, JS, images) - must be last
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(BASE_DIR, filename)

if __name__ == "__main__":
    print("Starting Python Flask Server For Home Price Prediction...")
    util.load_saved_artifacts()
    app.run()