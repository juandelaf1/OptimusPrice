# Optimus Price Production Setup

## Project Overview
Optimus Price is a machine learning-based pricing recommendation system for hotels.

## Quick Start
`ash
git clone https://github.com/juandelaf1/OptimusPrice.git
cd Optimus_Price_Final

# Install dependencies
pip install -r requirements.txt

# Run Streamlit application
streamlit run app_streamlit/app_cliente.py
`

## Production Deployment
`ash
# Build Docker image
docker build -t optimus-price .

# Run container
docker run -p 8501:8501 optimus-price
`

## Testing
Run unit tests:
`ash
pytest tests/
`

## Files Structure
- src/optimus_price/ - Core ML models and data processing
- pp_streamlit/ - Streamlit user interface
- data/ - Training and test datasets
- docs/ - Project documentation

## Contributing
Contributions are welcome! Please open issues or submit pull requests.

