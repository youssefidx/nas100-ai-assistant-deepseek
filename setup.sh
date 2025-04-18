#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py

#!/bin/bash

set -e  # Exit immediately if any command fails

echo "Installing dependencies..."
pip install -r requirements.txt || {
    echo "Error installing dependencies"
    exit 1
}

echo "Starting Streamlit app..."
streamlit run app.py
