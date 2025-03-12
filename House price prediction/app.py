import pickle
import numpy as np
import logging
from flask import Flask, request, render_template, jsonify

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load the trained model
try:
    with open("best_reg_model.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model: {e}")
    model = None  # Prevent app from breaking if the model fails to load

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route("/predict", methods=["POST"])
def predict():
    """Handle prediction requests."""
    try:
        if request.content_type == 'application/json':  # Handle JSON requests
            data = request.get_json()
            
            # Extract input values
            bedrooms = data.get("bedrooms")
            bathrooms = data.get("bathrooms")
            floors = data.get("floors")
            yr_built = data.get("yr_built")
            
            # Validate inputs
            if not all([bedrooms, bathrooms, floors, yr_built]):
                logging.warning("Missing input values in JSON request.")
                return jsonify({"error": "All fields (bedrooms, bathrooms, floors, yr_built) are required."}), 400
            
            try:
                # Convert to appropriate types
                bedrooms = float(bedrooms)
                bathrooms = float(bathrooms)
                floors = float(floors)
                yr_built = int(yr_built)
            except ValueError:
                logging.error("Invalid input: Non-numeric values in JSON request.")
                return jsonify({"error": "Please provide numeric values for bedrooms, bathrooms, floors, and yr_built."}), 400
            
            # Validate year built
            if yr_built > 2025:
                logging.warning("Invalid year in JSON request.")
                return jsonify({"error": "Year built cannot be greater than 2025."}), 400
            
            if model is None:
                logging.error("Model is not loaded.")
                return jsonify({"error": "Model is not available. Please try again later."}), 500
            
            # Make a prediction
            features = np.array([bedrooms, bathrooms, floors, yr_built]).reshape(1, -1)
            prediction = model.predict(features)[0]
            return jsonify({"price": int(prediction)})
        
        else:  # Handle HTML form submissions
            # Extract form inputs
            val1 = request.form.get("bedrooms", "").strip()
            val2 = request.form.get("bathrooms", "").strip()
            val3 = request.form.get("floors", "").strip()
            val4 = request.form.get("yr_built", "").strip()
            
            # Validate inputs
            if not all([val1, val2, val3, val4]):
                logging.warning("Missing input values in form submission.")
                return render_template("index.html", error="All fields are required.")
            
            try:
                # Convert to appropriate types
                bedrooms = float(val1)
                bathrooms = float(val2)
                floors = float(val3)
                yr_built = int(val4)
            except ValueError:
                logging.error("Invalid input: Non-numeric values in form submission.")
                return render_template("index.html", error="Please enter valid numeric values.")
            
            # Validate year built
            if yr_built > 2025:
                logging.warning("Invalid year in form submission.")
                return render_template("index.html", error="Year built cannot be greater than 2025.")
            
            if model is None:
                logging.error("Model is not available.")
                return render_template("index.html", error="Model is not available. Please try again later.")
            
            # Make a prediction
            features = np.array([bedrooms, bathrooms, floors, yr_built]).reshape(1, -1)
            prediction = model.predict(features)[0]
            return render_template("index.html", data=int(prediction))
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if request.content_type == 'application/json':
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500
        else:
            return render_template("index.html", error="An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    app.run(debug=True)