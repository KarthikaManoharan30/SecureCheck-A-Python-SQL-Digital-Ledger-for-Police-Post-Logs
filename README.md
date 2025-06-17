# 🚨 SecureCheck: Digital Policing, Reimagined  
📊 *An intelligent police check post monitoring system using Python, SQL, and Streamlit*

---

## 🚀 Overview  
**SecureCheck** is a smart traffic stop monitoring and analysis tool designed for **law enforcement agencies**.  
It transforms manual police logs into **real-time insights**, enabling smarter, faster decisions at vehicle check posts.

---

## 🧠 What Makes It Powerful?

| Feature                      | Description                                                |
|-----------------------------|------------------------------------------------------------|
| 🔎 Real-Time Data View       | Live table view of vehicle stops with filters              |
| 🧮 Medium + Complex Queries  | From age-based arrest rates to drug violation trends       |
| 📈 Visual Dashboard          | KPIs, pie charts, and bar graphs using Plotly & Matplotlib|
| 🤖 Smart Predictions         | Predict stop outcome & violations based on driver input    |
| 🗃️ PostgreSQL Database       | Fast querying & structured record storage                  |

---

## 📂 Dataset Structure

| Field               | Example        | Description                         |
|--------------------|----------------|-------------------------------------|
| `driver_age`       | 27             | Driver age                  |
| `driver_gender`    | M / F          | Gender of the driver                |
| `violation`        | Speeding / DUI | Reason for the stop                 |
| `stop_outcome`     | Warning / Arrest | Final result of the stop          |
| `search_conducted` | True / False   | Whether a search was performed      |
| `drugs_related_stop` | True / False | Whether drug-related                |

---

## 📊 Key Visuals in Action

### KPI Cards:
- 🚗 **Total Stops**
- 📈 **Arrests**
- 🔍 **Searches**
- 💊 **Drug-Related Incidents**

### Graphs:
- 📊 **Pie Chart**: Gender distribution in drug cases  
- 📊 **Bar Graph**: Violations by age group  

---

## 💡 Prediction Module

**Provide:**
- Age  
- Gender  
- Search status  
- Stop duration  
- Drug involvement  

**📢 And get back:**
- **Likely Violation**  
- **Expected Outcome**

**Example:**  
> A 24-year-old male stopped in Canada at 3:00 PM with no search and no drug involvement  
> → **Likely Violation**: *Speeding*, **Outcome**: *Warning*

---

## 🛠 Tech Stack

| Component   | Tech                             |
|------------|----------------------------------|
| Backend     | Python (Pandas, SQLAlchemy)     |
| Frontend    | Streamlit                        |
| Database    | PostgreSQL                       |
| Visualization | Plotly, Matplotlib            |

---

## ✅ How to Run It Locally

```bash
# Step 1: Install dependencies
pip install streamlit pandas sqlalchemy plotly psycopg2 matplotlib

# Step 2: Start the app
streamlit run Miniproj.py
💡 Ensure PostgreSQL is running and contains the traffic_stops table with sample data.

📌 Sample Use Cases
🚓 Detect patterns in late-night stops

🧑‍⚖️ Understand arrest rates by demographic

🔍 Identify high-risk violations

📊 Run queries on the fly to support investigations


🗂️ Folder Structure
SecureCheck/
│
├── Miniproj.py             # Main Streamlit dashboard
├── README.md               # You're here
├── requirements.txt        # Python dependencies




