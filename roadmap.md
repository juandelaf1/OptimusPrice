# OPTIMUS PRICE — Product Roadmap & Integration Guide

## Overview

OptimusPrice (OPT-PR-001) is a **machine learning-powered revenue management system** designed to help small and medium-sized hotels optimize room pricing, reduce OTA dependency (15-30%), and improve profitability through data-driven dynamic pricing.

## Product Vision

Transform independent hotels into data-driven pricing engines that can compete with large hotel chains through automated price optimization powered by machine learning.

## Current Status: Production Ready

### ✅ Core Product Complete
- **ML Models**: 4 advanced Python modules (6,535-7,857 lines)
- **Deployment**: Docker containerization + CI/CD pipeline
- **User Interface**: Streamlit dashboard with role-based access
- **Data Pipeline**: Complete hotel reservation dataset (10M+ rows)
- **Documentation**: Comprehensive setup guides

### ✅ Integration Point: RASPAL_SCRAPER
- Web scraping framework for hotel data collection
- Real-time competitor pricing monitoring
- Automated OTA price comparison

## Immediate Next Steps

### Phase 1: Data Collection Enhancement (Weeks 1-2)

#### 1.1 Integrate RASPAL_SCRAPER
```bash
# Install the scraping framework
pip install raspal[all]

# Setup for hotel pricing data collection
raspal setup  # Install browsers and verify Ollama

# Create scraping pipelines for hotel data sources
```

#### 1.2 Configure Scraping Engines

**For hotel pricing data, use these engine combinations:**

| Source Type | Recommended Engine | Reason |
|-------------|------------------|--------|
| Hotel websites | `stealth` | Bypasses Cloudflare/turnstile, anti-bot measures |
| OTA platforms | `stealth` | Complex JS rendering, dynamic pricing |
| Hotel booking pages | `playwright` | Interactive forms, real-time pricing |
| Price comparison sites | `auto` | Static content with fallback |

#### 1.3 Create Hotel Data Scraping Pipelines

**Example YAML pipeline for hotel pricing data:**
```yaml
# hotel_pricing_scraping.yaml
url: "https://www.booking.com/hotel/price/{hotel_id}"
engine: stealth
cache_ttl: 1800  # 30 minutes - pricing changes frequently
extract:
  text: true
  metadata: true
  use_selectolax: true
  selectors:
    hotel_name: "h1.hotel-name"
    price: "span.price-main"
    availability: "div.availability-status"
    rating: "span.rating-value"
    location: "div.hotel-address"
    features: "ul.hotel-features li"
llm:
  model: "llama3.2"
  template: "hotel_listing"
  prompt: "Extract hotel details: name, price, rating, location, amenities, availability status"
  output_schema:
    name: ""
    price: 0
    currency: "EUR"
    rating: 0
    location: ""
    amenities: []
    availability: "available/unavailable"
    last_updated: "YYYY-MM-DD HH:MM:SS"
```

### Phase 2: Product Enhancement (Weeks 3-4)

#### 2.1 Add Real-time Price Monitoring
```python
# Real-time competitor monitoring using RASPAL
from raspal import Fetcher, LLMExtractor

# Monitor key competitors
competitor_urls = [
    "https://www.booking.com/hotel/price/hotel-a",
    "https://www.expedia.com/hotel/hotel-b",
    "https://www.hotels.com/hotel/hotel-c",
    "https://www.trivago.es/hotel/hotel-d"
]

for url in competitor_urls:
    fetcher = Fetcher(engine="stealth")
    result = fetcher.fetch(url, cache_ttl=300)  # 5 minutes cache
    
    llm = LLMExtractor()
    data = llm.extract(
        result.html, 
        LLMConfig(
            template="hotel_pricing",
            output_schema={
                "hotel_name": "",
                "price": 0,
                "currency": "EUR",
                "availability": "available/unavailable"
            }
        )
    )
    
    # Compare with internal pricing
    optimize_pricing(data, "OPT-MDL-OPT")
```

#### 2.2 Implement OTA Price Comparison Engine
```python
# Compare internal vs OTA prices
class OTAPriceComparator:
    def __init__(self, opt_model):
        self.opt_model = opt_model
        self.ota_sources = ["booking.com", "expedia.com", "hotels.com"]
    
    def analyze_price_gap(self, hotel_data):
        internal_price = self.opt_model.predict_price(hotel_data)
        
        for ota in self.ota_sources:
            ota_price = self.get_ota_price(hotel_data.hotel_id, ota)
            price_gap = ota_price - internal_price
            opportunity = self.calculate_opportunity(internal_price, ota_price)
            
            if opportunity > 0:
                # Generate recommendation
                recommendation = self.generate_price_adjustment(
                    internal_price, ota_price, opportunity
                )
                return recommendation
        
        return {"action": "maintain", "reason": "pricing_aligned_with_market"}
```

### Phase 3: Advanced Features (Weeks 5-8)

#### 3.1 Dynamic Pricing Algorithm
```yaml
# dynamic_pricing_config.yaml
# Time-based pricing rules
time_based_rules:
  peak_season: "November-March"
  peak_hours: "18:00-22:00"
  weekend_premium: 20%
  holiday_multiplier: 1.3

# Demand-based adjustments
booking_pattern_analysis: true
seasonality_weighting: true
competitor_response: true

# Revenue optimization constraints
min_profit_margin: 15%
max_discount: 25%
price_change_frequency: "hourly"
```

#### 3.2 Integration with Existing Optimus Systems
```python
# Extend existing ML pipeline to include web data
from raspal import Fetcher, AutoThrottle
from optimus_price.src.optimus_price.training import TrainingModule

class EnhancedOptimusPrice(TrainingModule):
    def __init__(self):
        super().__init__()
        self.competitor_monitor = OTAPriceComparator(self)
        self.raspal_fetcher = Fetcher(engine="stealth")
        self.throttle = AutoThrottle(min_delay=1, max_delay=60)
    
    def train_with_web_data(self, historical_data, competitor_urls):
        # Fetch competitor pricing data
        for url in competitor_urls:
            self.throttle.wait("scrapling")
            result = self.raspal_fetcher.fetch(url)
            
            # Extract and normalize data
            processed_data = self.normalize_competitor_data(result)
            historical_data.append(processed_data)
        
        # Retrain model with enhanced dataset
        return self.train(historical_data)
    
    def predict_with_market_context(self, hotel_features):
        # Get current market conditions
        market_data = self.get_current_market_data()
        
        # Combine with internal ML prediction
        base_prediction = super().predict(hotel_features)
        market_adjustment = self.calculate_market_adjustment(market_data)
        
        return base_prediction + market_adjustment
```

### Phase 4: Production Deployment (Weeks 9-10)

#### 4.1 Enhanced Docker Configuration
```dockerfile
# Dockerfile.enhanced
FROM python:3.11-slim

# Install raspal for web scraping
RUN pip install raspal[all]

# Copy enhanced optimus-price code
COPY OptimusPrice/ /app/

# Install dependencies
WORKDIR /app
RUN pip install -r requirements.txt

# Create dedicated user for security
RUN useradd -m -u 1000 optimus
RUN chown -R optimus:optimus /app
USER optimus

# Expose ports
EXPOSE 8501  # Streamlit
EXPOSE 8080  # RASPAL web interface

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501 || exit 1

CMD ["streamlit", "run", "app_streamlit/app_cliente.py", "--server.port", "8501"]
```

#### 4.2 Comprehensive CI/CD Pipeline
```yaml
# .github/workflows/optimus-enhanced.yml
name: Optimus Price Enhanced Deployment

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10"]
    
    services:
      redis:
        image: redis:alpine
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install raspal[all]
    
    - name: Run unit tests
      run: |
        pytest tests/ -v
    
    - name: Run integration tests
      run: |
        # Test scraping capabilities
        python -c "from raspal import Fetcher; f = Fetcher(); print('RASPAL available')"
    
  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t optimus-price-enhanced .
    
    - name: Run security scan
      run: |
        # Add security scanning here
        # e.g., npm audit, safety scan
        
    - name: Deploy to staging
      run: |
        # Deploy to staging environment
        # e.g., kubernetes, docker-compose
        
    - name: Production deployment
      if: github.ref == 'refs/heads/main'
      run: |
        # Full production deployment
        # e.g., update production servers
```

## Data Sources for Hotel Pricing

### Primary Sources (Direct Data)

1. **Hotel Websites**
   - Direct booking pages
   - Hotel chain websites
   - Resort/hotel official pages

2. **OTA Platforms**
   - Booking.com
   - Expedia
   - Hotels.com
   - Trivago
   - Agoda

3. **Price Comparison Engines**
   - Google Hotels
   - Kayak
   - Momondo
   - Cheapflights

### Secondary Sources (Indirect Data)

1. **Industry Reports**
   - STR Global Hotel Index
   - Hotel News and Trends
   - Market research reports

2. **Public APIs**
   - Google Maps Places API
   - Foursquare Venue Insights
   - Weather APIs (seasonal pricing)

3. **Social Media**
   - Hotel reviews and pricing discussions
   - Travel forum pricing discussions

### Data Collection Strategy

#### Phase 1: Foundational (Weeks 1-2)
- Target 50-100 hotel properties
- Focus on seasonal destinations (beach, mountain, city)
- Establish baseline pricing patterns

#### Phase 2: Expansion (Weeks 3-4)
- Scale to 500-1000 properties
- Include diverse market segments
- Integrate with hotel loyalty programs

#### Phase 3: Advanced (Weeks 5-8)
- Comprehensive market coverage
- Real-time pricing monitoring
- Predictive analytics integration

## Testing Strategy

### Unit Tests
- **Scraper functionality**: Test extraction logic
- **LLM integration**: Verify data parsing
- **Cache performance**: Test caching behavior
- **Rate limiting**: Verify throttling works

### Integration Tests
- **End-to-end**: Full scraping pipeline
- **ML integration**: Combine web data with ML models
- **Price optimization**: Test recommendation algorithms
- **Dashboard integration**: Verify Streamlit updates

### Performance Tests
- **Scalability**: Handle large numbers of requests
- **Speed**: Response time under load
- **Reliability**: Uptime and error recovery

## Security Considerations

### Web Scraping Security
```python
# Secure scraping practices
secure_config = {
    'timeout': 30,
    'retries': 3,
    'backoff_factor': 2,
    'user_agent': 'OptimusPrice-PriceMonitor/1.0 (contact@example.com)',
    'respect_robots_txt': True,
    'cache_dir': '/tmp/optimus_cache',
    'proxy_rotation': True,
}
```

### Data Storage Security
- Encrypt stored competitor pricing data
- Use secure database connections
- Implement access controls for admin dashboard
- Regular security audits

## Future Enhancements

### Phase 5: Advanced Features (Weeks 11-12)

1. **AI-Powered Price Optimization**
   - Machine learning for optimal pricing
   - Predictive analytics for demand forecasting
   - Reinforcement learning for continuous improvement

2. **Multi-Modal Data Integration**
   - Social media sentiment analysis
   - Weather data integration
   - Local event data (concerts, festivals)

3. **API Integration**
   - Direct hotel API connections
   - OTA API partnerships
   - Third-party analytics services

## Project Timeline

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| 1-2 | Core integration | RASPAL scraping framework |
| 3-4 | Price monitoring | Real-time competitor tracking |
| 5-6 | Enhanced ML pipeline | Web data + ML models |
| 7-8 | Advanced features | Multi-source integration |
| 9-10 | Production deployment | Enhanced Docker images |
| 11-12 | Testing & optimization | Full system testing |

## Risk Assessment

### High Risk
- Legal compliance issues
Clampdown by target websites
- Technical integration complexity
- Performance under high load

### Medium Risk
- Cost of additional infrastructure
- Team skill gaps
- Data quality issues

### Low Risk
- Schedule delays
- Minor feature scope creep
- Documentation completeness

## Success Metrics

### Technical KPIs
- **Scraping coverage**: % of target hotels successfully scraped
- **Data accuracy**: Precision of extracted pricing data
- **System uptime**: Availability of monitoring service
- **Response time**: Time to extract and process data

### Business KPIs
- **Price optimization impact**: Revenue improvement percentage
- **OTA dependency reduction**: % decrease in OTA usage
- **Market competitiveness**: Ranking in price comparisons
- **Customer satisfaction**: User engagement with dashboard

### Operational KPIs
- **Monitoring coverage**: Number of hotels tracked
- **Alert effectiveness**: False positive/negative rates
- **Resource utilization**: CPU/memory usage
- **Cost per insight**: Economics of data collection

## Conclusion

The integration of RASPAL_SCRAPER with OptimusPrice creates a powerful competitive advantage in the hotel pricing optimization market. By combining:

1. **Robust ML models** for pricing optimization
2. **Advanced web scraping** for real-time market data
3. **Comprehensive deployment infrastructure**
4. **Professional analytics and visualization**

The Enhanced Optimus Price system will deliver superior pricing recommendations that continuously adapt to market conditions, competitor pricing, and customer demand patterns, resulting in significant revenue improvements for partner hotels.

---

*Prepared for: Juan de la Fuente*  
*Date: June 2026*  
*Project: OptimusPrice Enhanced with RASPAL Integration*

---

**Next Steps:**
1. **Phase 1 Implementation**: Set up RASPAL scraping framework (Weeks 1-2)
2. **Phase 2 Integration**: Build price monitoring system (Weeks 3-4)
3. **Phase 3 Enhancement**: Upgrade ML pipeline with web data (Weeks 5-8)
4. **Phase 4 Deployment**: Launch enhanced production system (Weeks 9-10)
5. **Phase 5 Optimization**: Advanced features and integrations (Weeks 11-12)

This roadmap provides a comprehensive, phased approach to transforming OptimusPrice into a market-leading revenue management solution powered by real-time competitive intelligence.