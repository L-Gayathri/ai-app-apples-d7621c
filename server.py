```python
import os
from flask import Flask, jsonify, request, send_from_directory

# --- In-memory store for demonstration ---
apples_db = {
    1: {"id": 1, "variety": "Fuji", "weight_kg": 0.2, "color": "red"},
    2: {"id": 2, "variety": "Granny Smith", "weight_kg": 0.25, "color": "green"},
    3: {"id": 3, "variety": "Gala", "weight_kg": 0.18, "color": "red-yellow"},
}
next_apple_id = 4

class APIError(Exception):
    """Custom exception for API errors."""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Converts the error to a dictionary for JSON response."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def create_app():
    """Flask application factory."""
    app = Flask(__name__)

    # --- Error Handlers ---
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handler for custom APIError exceptions."""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        """Handler for 404 Not Found errors."""
        response = jsonify({"message": "Resource not found."})
        response.status_code = 404
        return response

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handler for 500 Internal Server Error."""
        response = jsonify({"message": "An unexpected error occurred."})
        response.status_code = 500
        return response

    # --- Dynamic CORS Handling ---
    @app.before_request
    def handle_options_requests():
        """Handles preflight OPTIONS requests for API routes."""
        if request.method == 'OPTIONS' and request.path.startswith('/api/'):
            origin = request.headers.get('Origin')
            if origin:
                # Create a default response for preflight
                resp = app.make_default_options_response()
                # Set CORS headers for the preflight response
                resp.headers['Access-Control-Allow-Origin'] = origin
                resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization' # Common headers for fetch
                resp.headers['Access-Control-Allow-Credentials'] = 'true'
                resp.headers['Access-Control-Max-Age'] = '86400' # Cache preflight for 24 hours
                return resp
            # If no origin or not an API path, let Flask continue normally

    @app.after_request
    def apply_cors_headers(response):
        """Applies dynamic CORS headers to API responses."""
        # Only apply CORS to /api/* routes
        if request.path.startswith('/api/'):
            origin = request.headers.get('Origin')
            if origin:
                # Set the Access-Control-Allow-Origin header to the request's origin
                response.headers['Access-Control-Allow-Origin'] = origin
                # Re-set common methods and headers for the actual request response
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # --- Mandatory Root Route ---
    @app.route("/")
    def serve_frontend():
        """Serves the index.html file for the frontend."""
        # This assumes index.html is in the same directory as the app.py file
        return send_from_directory(".", "index.html")

    # --- API Endpoints ---

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "service": "apples-backend"})

    @app.route("/api/apples", methods=["GET"])
    def get_apples():
        """Returns a list of all apples."""
        return jsonify(list(apples_db.values()))

    @app.route("/api/apples", methods=["POST"])
    def create_apple():
        """Creates a new apple entry."""
        global next_apple_id
        if not request.is_json:
            raise APIError("Request must be JSON", status_code=400)

        data = request.get_json()
        variety = data.get("variety")
        weight_kg = data.get("weight_kg")
        color = data.get("color")

        if not all([variety, weight_kg, color]):
            raise APIError("Missing data for new apple. Required: variety, weight_kg, color", status_code=400)
        
        try:
            # Validate weight_kg as a positive float
            weight_kg = float(weight_kg)
            if weight_kg <= 0:
                 raise ValueError("Weight must be positive.")
        except (ValueError, TypeError):
             raise APIError("weight_kg must be a positive number.", status_code=400)

        new_apple = {
            "id": next_apple_id,
            "variety": variety,
            "weight_kg": weight_kg,
            "color": color,
        }
        apples_db[next_apple_id] = new_apple
        next_apple_id += 1
        return jsonify(new_apple), 201 # Return 201 Created status

    @app.route("/api/apples/<int:apple_id>", methods=["GET"])
    def get_apple(apple_id):
        """Returns details for a specific apple by ID."""
        apple = apples_db.get(apple_id)
        if not apple:
            raise APIError(f"Apple with ID {apple_id} not found.", status_code=404)
        return jsonify(apple)

    @app.route("/api/apples/<int:apple_id>", methods=["PUT"])
    def update_apple(apple_id):
        """Updates an existing apple's details."""
        apple = apples_db.get(apple_id)
        if not apple:
            raise APIError(f"Apple with ID {apple_id} not found.", status_code=404)

        if not request.is_json:
            raise APIError("Request must be JSON", status_code=400)

        data = request.get_json()
        
        # Update fields if provided
        if 'variety' in data:
            apple['variety'] = data['variety']
        if 'color' in data:
            apple['color'] = data['color']
        if 'weight_kg' in data:
            try:
                weight_kg_val = float(data['weight_kg'])
                if weight_kg_val <= 0:
                    raise ValueError("Weight must be positive.")
                apple['weight_kg'] = weight_kg_val
            except (ValueError, TypeError):
                raise APIError("weight_kg must be a positive number.", status_code=400)

        return jsonify(apple)

    @app.route("/api/apples/<int:apple_id>", methods=["DELETE"])
    def delete_apple(apple_id):
        """Deletes an apple by ID."""
        if apple_id not in apples_db:
            raise APIError(f"Apple with ID {apple_id} not found.", status_code=404)
        
        deleted_apple = apples_db.pop(apple_id)
        return jsonify({"message": f"Apple ID {apple_id} deleted.", "deleted_apple": deleted_apple})

    @app.route("/api/apples/varieties", methods=["GET"])
    def get_apple_varieties():
        """Returns a list of all unique apple varieties."""
        varieties = sorted(list(set(apple["variety"] for apple in apples_db.values())))
        return jsonify({"varieties": varieties})

    return app

# --- For gunicorn entry point and local development ---
if __name__ == '__main__':
    app = create_app()
    # Read PORT from environment variable, default to 5000
    PORT = int(os.environ.get("PORT", 5000))
    # DO NOT use debug=True in production
    app.run(host='0.0.0.0', port=PORT, debug=False)
```