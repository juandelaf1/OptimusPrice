# OPTIMUS PRICE — Enhanced Edition with RASPAL Integration

## Quick Start

### Environment Setup
```bash
# 1. Clone the repository
git clone https://github.com/juandelaf1/OptimusPrice.git
cd Optimus_Price_Final

# 2. Setup Python virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install RASPAL scraping framework
pip install raspal[all]

# 4. Install Optimus Price dependencies
pip install -r requirements.txt

# 5. Setup required browsers
raspal setup

# 6. Initialize data collection
raspal init
```

### Basic Usage

#### Start Streamlit Application
```bash
# Launch the user interface
streamlit run app_streamlit/app_cliente.py

# Access the admin dashboard
streamlit run app_streamlit/app_adm_1.py
```

#### Data Collection
```bash
# Monitor competitor pricing
raspal run configs/hotel_pricing_scraping.yaml

# Real-time price tracking
raspal serve  # Web interface at http://localhost:8462
```

#### ML Model Training
```bash
# Train with enhanced dataset
python -m src.optimus_price.training

# Evaluate model performance
python -m src.optimus_price.evaluation
```

## Product Overview

### Optimus Price (OPT-PR-001) — Enhanced Version

Optimus Price is an **AI-powered hotel revenue management system** that combines machine learning algorithms with real-time web scraping to optimize room pricing and maximize revenue for hotels.

#### Key Differentiators:
- **ML-Powered Pricing**: Random Forest with hyperparameter optimization
- **Real-Time Market Intelligence**: Live competitor price monitoring
- **Enhanced Data Pipeline**: RASPAL integration for comprehensive market data
- **Multi-Platform Deployment**: Docker, CI/CD, and cloud-ready
- **Professional Analytics**: Advanced reporting and visualization

### Product Features

#### 1. Advanced ML Pipeline
- **Random Forest Regressor**: Non-linear relationship modeling
- **Hyperparameter Optimization**: Optuna with cross-validation
- **Feature Engineering**: total_guests, total_nights, seasonality
- **Performance Metrics**: RMSE, MAE, R² evaluation

#### 2. RASPAL Integration
- **Web Scraping**: Hotel pricing data collection
- **Multi-Engine Support**: scrapling, playwright, stealth, auto
- **AI Extraction**: LLM-based data parsing
- **Real-Time Monitoring**: Live competitor tracking

#### 3. Enhanced User Experience
- **Role-Based Interface**: Admin dashboard + customer portal
- **Real-Time Pricing**: Dynamic price recommendations
- **Market Analysis**: Competitor comparison tools
- **Revenue Visualization**: Clear ROI communication

#### 4. Production Infrastructure
- **Docker Containerization**: Consistent deployment
- **CI/CD Pipeline**: Automated testing and deployment
- **Cloud Ready**: Scalable for enterprise use
- **Security First**: Comprehensive security measures

## Technical Specifications

### Core Components

#### 1. ML Models (`src/optimus_price/`)
| File | Purpose | Lines | Performance |
|------|---------|--------|-------------|
| `data_generator.py` | Data generation | 6,535 | Advanced preprocessing |
| `training.py` | Model training | 7,857 | Random Forest with hyperparameter tuning |
| `evaluation.py` | Model evaluation | 3,850 | Comprehensive metrics |
| `data_processing.py` | Data processing | 2,607 | Feature engineering |

#### 2. User Interfaces (`app_streamlit/`)
| Application | Purpose | Users | Features |
|-------------|---------|--------|----------|
| `app_cliente.py` | Customer portal | Hotel guests | Price check, booking assistance |
| `app_adm_1.py` | Admin dashboard | Hotel managers | Price settings, competitor analysis |
| `pruebas_apps/` | Test applications | QA team | Testing, validation |

#### 3. Data Collection (`raspal/`)
| Component | Function | Configuration | Priority |
|-----------|----------|---------------|----------|
| Hotel scraping | Hotel website data | YAML-based | High |
| OTA monitoring | OTA platform prices | Automated | High |
| Price comparison | Market analysis | Real-time | Medium |
| Weather integration | Seasonal pricing | External API | Low |

### Dependencies

#### Python Packages
```bash
# Core Optimus requirements
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.2.2
Optuna>=3.0.0
Streamlit==1.25.0
KaggleHub>=0.5.0

# RASPAL integration
raspal>=0.4.0

# Development tools
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
```

#### System Requirements
- **Memory**: 16GB RAM (minimum)
- **Storage**: 500GB free space
- **CPU**: Multi-core processor
- **Network**: High-speed internet connection

## Installation Guide

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/juandelaf1/OptimusPrice.git
cd Optimus_Price_Final

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
pip install raspal[all]

# Setup browsers and tools
raspal setup

# Initialize data collection
raspal init

# Test installation
python -c "from raspal import Fetcher; from optimus_price.src.optimus_price.training import TrainingModule; print('✅ All imports successful')"
```

### Docker Deployment
```bash
# Build Docker image
docker build -t optimus-price-enhanced .

# Run container
docker run -p 8501:8501 -p 8462:8462 optimus-price-enhanced

# Or use docker-compose
docker-compose up -d
```

### Cloud Deployment
```bash
# AWS ECS/EKS
# Google Cloud GKE
# Azure AKS
# Kubernetes with Helm
```

## Usage Examples

### 1. Price Optimization
```python
from optimus_price.src.optimus_price.training import TrainingModule

# Initialize model
trainer = TrainingModule()

# Prepare hotel features
hotel_features = {
    'total_guests': 2,
    'total_nights': 3,
    'season': 'peak_season',
    'location': 'beach_resort',
    'competitor_prices': [150, 160, 155]
}

# Get price recommendation
price = trainer.predict_price(hotel_features)
print(f"Recommended price: ${price}")
```

### 2. Competitor Monitoring
```python
from raspal import Fetcher, LLMExtractor

# Monitor competitor prices
competitors = [
    "https://www.booking.com/hotel/price/hotel-a",
    "https://www.expedia.com/hotel/hotel-b",
    "https://www.hotels.com/hotel/hotel-c"
]

for url in competitors:
    fetcher = Fetcher(engine="stealth")
    result = fetcher.fetch(url)
    
    llm = LLMExtractor()
    data = llm.extract(
        result.html,
        LLMConfig(
            template="hotel_pricing",
            output_schema={
                "price": 0,
                "rating": 0,
                "availability": "available"
            }
        )
    )
    
    print(f"Competitor price: ${data['price']}")
```

### 3. ML Pipeline Integration
```python
# Complete ML pipeline with web data
from raspal import Fetcher, AutoThrottle
from optimus_price.src.optimus_price.training import TrainingModule

# Initialize enhanced system
enhanced_system = EnhancedOptimusPrice()

# Collect web data and train
competitor_urls = ["https://booking.com/hotel/price/1", "https://expedia.com/hotel/price/2"]
historical_data = enhanced_system.collect_web_data(competitor_urls)

# Train with enhanced dataset
model = enhanced_system.train_with_web_data(historical_data)

# Make predictions with market context
predictions = enhanced_system.predict_with_market_context(hotel_features)
```

## Configuration

### Environment Variables
```bash
# RASPAL configuration
RASPAL_CACHE_DIR=/tmp/raspal_cache
RASPAL_TIMEOUT=30
RASPAL_MAX_RETRIES=3

# Optimus configuration
OPTIMUS_MODEL_PATH=/app/models/hotel_pricing_optuna.pkl
OPTIMUS_DATA_PATH=/app/data/processed
OPTIMUS_ENVIRONMENT=production
```

### Config Files

#### `configs/hotel_pricing_scraping.yaml`
```yaml
# Hotel pricing scraping configuration
url: "https://www.booking.com/hotel/price/{hotel_id}"
engine: stealth
cache_ttl: 1800
extract:
  text: true
  metadata: true
  use_selectolax: true
  selectors:
    hotel_name: "h1.hotel-name"
    price: "span.price-main"
    availability: "div.availability-status"
    rating: "span.rating-value"
llm:
  model: "llama3.2"
  template: "hotel_pricing"
  prompt: "Extract hotel pricing information including name, price, rating, and availability"
throttle:
  min_delay: 1
  max_delay: 60
```

#### `configs/dynamic_pricing.yaml`
```yaml
# Dynamic pricing rules
time_based_rules:
  peak_season: "November-March"
  peak_hours: "18:00-22:00"
  weekend_premium: 20%
  holiday_multiplier: 1.3

# Optimization constraints
min_profit_margin: 15%
max_discount: 25%
price_change_frequency: "hourly"

# Market integration
competitor_response: true
seasonality_analysis: true
booking_pattern_prediction: true
```

## Testing

### Unit Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_scraping.py
pytest tests/test_ml_integration.py
pytest tests/test_pricing_optimization.py
```

### Integration Tests
```bash
# Test scraping capabilities
python -m unittest test_raspal_integration

# Test ML pipeline
python -m unittest test_ml_pipeline

# Test web integration
python -m unittest test_web_integration
```

### Performance Tests
```bash
# Load testing
# Test with large datasets
# Monitor response times
# Check system resource usage
```

## Maintenance

### Daily Tasks
```bash
# Check system health
raspal status

# Clear cache if needed
raspal clear-cache

# Monitor logs
tail -f /var/log/optimus/price_monitor.log
```

### Weekly Tasks
```bash
# Backup data
rsync -av /app/data/ /backup/optimus_data/

# Update dependencies
pip list --outdated | xargs pip install

# Security audit
# Run security scanning tools
```

### Monthly Tasks
```bash
# Model retraining
python scripts/retrain_model.py

# System optimization
# Analyze performance metrics
# Adjust throttling parameters
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Cannot connect to hotel website"
**Solution:**
1. Check if the URL is valid
2. Verify website accessibility
3. Try different scraping engine
4. Increase timeout and retry count

#### Issue 2: "Price extraction failed"
**Solution:**
1. Check selector syntax
2. Verify HTML structure
3. Adjust LLM configuration
4. Manually extract data if needed

#### Issue 3: "Model prediction error"
**Solution:**
1. Check model file integrity
2. Verify feature consistency
3. Retrain model with new data
4. Check for data preprocessing issues

### Error Codes
- **ERR-SCRAPE-001**: Connection timeout
- **ERR-SCRAPE-002**: Invalid URL
- **ERR-SCRAPE-003**: Selector not found
- **ERR-MODEL-001**: Model loading error
- **ERR-MODEL-002**: Prediction failure
- **ERR-DATA-001**: Data processing error

## Support

### Documentation
- [Quick Start Guide](README.md)
- [API Reference](docs/api-reference.md)
- [Configuration Guide](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)

### Community
- **GitHub Issues**: https://github.com/juandelaf1/OptimusPrice/issues
- **Discussions**: Technical support and feature requests
- **Contributing**: Pull requests and contributions

### Contact
- **Email**: juandelafuentelarrocca@gmail.com
- **Support**: For technical issues and questions
- **Sales**: For enterprise licensing and support

## Future Roadmap

### Phase 6: Advanced Features (Weeks 13-16)
1. **Voice Interface**: Voice-based pricing queries
2. **AR/VR Integration**: Augmented reality room visualization
3. **Blockchain Integration**: Smart contracts for pricing
4. **Advanced Analytics**: Predictive analytics with quantum computing

### Phase 7: Enterprise Features (Weeks 17-20)
1. **Multi-Hotel Management**: Chain hotel support
2. **API Gateway**: RESTful API for third-party integration
3. **Advanced Reporting**: Custom report generation
4. **White Label**: Client-specific branding

### Phase 8: Innovation (Weeks 21-24)
1. **AI Research**: Integration with latest ML research
2. **Quantum Computing**: Quantum machine learning
3. **Global Expansion**: International market support
4. **Industry 4.0**: Smart factory integration

## Conclusion

The Enhanced Optimus Price with RASPAL integration represents a significant leap forward in hotel revenue management. By combining cutting-edge machine learning with real-time market intelligence, hotels can now:

- **Maximize revenue** through data-driven pricing
- **Reduce OTA dependency** with competitive pricing
- **Improve guest experience** with dynamic offerings
- **Stay competitive** with market-aware pricing strategies

This system is ready for enterprise deployment and will continue to evolve with advances in AI, web scraping, and market analytics technology.

---

*Document Version: 1.0*
*Last Updated: June 2026*
*Prepared by: Juan de la Fuente*
*Contact: juandelafuentelarrocca@gmail.com*

---

**🚀 Ready to Transform Your Hotel Pricing?**

Start your Optimus Price journey today with the enhanced RASPAL integration!

```bash
# Quick start for production deployment
git clone https://github.com/juandelaf1/OptimusPrice.git
cd Optimus_Price_Final
docker-compose up -d
```