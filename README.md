
# 🚀 Optimus Price  
## 🏨 Intelligent Hotel Pricing Recommendation System

![Optimus Price – Intelligent Hotel Pricing System](docs/img/optimus_price_logo.jpg)

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.2.2-F7931E?logo=scikit-learn)
![License](https://img.shields.io/badge/license-MIT-green)

**Optimus Price** is a **machine learning-based pricing recommendation system** designed to help **small and medium-sized hotels optimize room prices, improve revenue management, and reduce dependency on Online Travel Agencies (OTAs)** that charge high commissions.

> 💡 Data Science project focused on solving a **real business problem**, including data analysis, modeling, evaluation, and an **interactive Streamlit application**.

---

# 📌 Business Problem

Many small and medium-sized hotels struggle with **pricing optimization** due to:

❌ Prices defined manually or based on intuition  
❌ High dependency on OTAs with commissions between **15% and 30%**  
❌ Limited access to dynamic pricing tools  

This often results in **lost revenue opportunities and reduced competitiveness** compared to large hotel chains.

---

# 🎯 Project Objective

The goal of this project is to develop a **data-driven pricing recommendation system** capable of:

- Analyzing historical reservation data  
- Detecting **demand patterns and seasonality**  
- Generating **automated price recommendations**  
- Supporting business decisions through an **interactive interface**

---

# 🧠 Solution Overview

Optimus Price combines **machine learning, feature engineering and data visualization** to help hotel managers:

- ✅ Adjust prices dynamically based on demand  
- ✅ Reduce OTA commission dependency  
- ✅ Improve revenue management  
- ✅ Make **data-driven pricing decisions**

> 💼 **Portfolio Highlight**: End-to-end ML project demonstrating:
> - Complete data pipeline (collection → cleaning → feature engineering → modeling)
> - Model experimentation with benchmarking against multiple algorithms
> - Production-ready Streamlit deployment with role-based interfaces
> - Business impact visualization and clear ROI communication

---

# 🧰 Tech Stack

- 🐍 **Python 3.8+** 
- 📊 **Pandas 2.0.3**, **NumPy 1.24.3**
- 🤖 **Scikit-learn 1.2.2** (RandomForestRegressor)
- 🔍 **Optuna** (hyperparameter optimization)
- 🖥️ **Streamlit 1.25.0** (interactive UI)
- 📦 **KaggleHub** (data acquisition)

---

# 🏗️ Project Structure

📦 OptimusPrice
├── data/
│ ├── raw/ # Original datasets
│ ├── processed/ # Cleaned and transformed data
│ ├── train/ # Training dataset
│ └── test/ # Test dataset
├── notebooks/
│ ├── 01_DataSources.ipynb
│ ├── 02_DataCleaning_EDA.ipynb
│ └── 03_ModelTraining_Evaluation.ipynb
├── src/
│ ├── data_processing.py
│ ├── training.py
│ └── evaluation.py
├── models/ # Trained models
├── app_streamlit/ # Streamlit application
├── docs/ # Project documentation
└── README.md


---

# 🔬 Project Workflow

## 1️⃣ Data Collection

Hotel reservation dataset obtained from **Kaggle** using the Kaggle API.

---

## 2️⃣ Data Cleaning & Exploratory Data Analysis (EDA)

Main steps included:

- Handling missing values  
- Encoding categorical variables  
- Identifying relationships between **reservation characteristics and pricing**

---

## 3️⃣ Feature Engineering

New variables were created to improve model performance:

- **total_guests**
- **total_nights**

These features help capture **booking complexity and demand patterns**.

---

## 4️⃣ Model Training

Main model used:

🌲 **Random Forest Regressor**

This model was selected because it:

- captures **non-linear relationships**
- handles **feature interactions**
- is robust to outliers

---

## 5️⃣ Hyperparameter Optimization

Model performance was improved using:

🔍 **Optuna**

Hyperparameter tuning was performed using **cross-validation** to identify the best model configuration.

---

## 6️⃣ Model Evaluation

Performance was evaluated using:

📉 **RMSE** – Root Mean Squared Error  
📉 **MAE** – Mean Absolute Error  
📈 **R²** – Coefficient of Determination  

These metrics allow evaluating **prediction accuracy and model reliability**.

---

## 7️⃣ Model Persistence

The trained model and preprocessing pipeline were saved to allow **future predictions without retraining**.

---

# 🖥️ Streamlit Application

The interactive application allows users to:

- Input reservation characteristics  
- Generate **real-time price recommendations**  
- Interact with the trained model through a **simple visual interface**

Run the application locally:

streamlit run app_streamlit/app_cliente.py


---

# 📈 Revenue Impact Example

| Scenario | Gross Revenue (€) | Commission | Net Revenue (€) |
|--------|--------|--------|--------|
| 💚 Direct booking with Optimus Price | 100 | 0% | 100 |
| OTA (15%) | 100 | 15% | 85 |
| OTA (25%) | 100 | 25% | 75 |
| OTA (30%) | 100 | 30% | 70 |

➡️ **Conclusion:** Direct pricing strategies supported by data can significantly improve hotel profitability.

---

# 🚀 Running the Project

git clone https://github.com/juandelaf1/OptimusPrice.git

pip install -r requirements.txt
streamlit run app_streamlit/app_cliente.py


---

# 🔮 Future Improvements

Potential next steps:

📅 Time-series validation for demand forecasting  
🌦️ Integration of external data (events, weather, tourism trends)  
🏨 Hotel-specific model training  
⚡ Testing boosting models such as **XGBoost or LightGBM**  
☁️ Cloud deployment (Streamlit Cloud / Hugging Face Spaces)  
📊 Monitoring model performance in production

---

# 🤝 Contributions

Contributions and suggestions are welcome 🙌

Feel free to open a **pull request** or propose improvements.

📬 Contact  
Email: juandelafuentelarrocca@gmail.com
