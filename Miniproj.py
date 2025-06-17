import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import plotly.express as px
from sqlalchemy import create_engine


# Function to create a SQLAlchemy engine
def create_connection():
    try:
        # Format: postgresql+psycopg2://user:password@host:port/dbname
        engine = create_engine("postgresql+psycopg2://postgres:Regular30@localhost:5432/Testing_db")
        return engine
    except Exception as e:
        print(f"Error creating engine: {e}")
        return None

# Fetch data using pandas and SQLAlchemy
def fetch_data(query):
    engine = create_connection()
    if engine:
        try:
            df = pd.read_sql(query, con=engine)
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()    

# Cleaning data function
def clean_data(df):
    # Drop columns where all values are NaN
    df = df.dropna(axis=1, how='all')

    # Fill missing string fields with 'Unknown'
    string_cols = ['driver_gender', 'driver_race', 'country_name', 'violation', 'stop_outcome', 'search_type', 'stop_duration']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')

    # Fill missing boolean fields with False
    bool_cols = ['search_conducted', 'drugs_related_stop', 'is_arrested']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)

    # Handle missing ages: convert to numeric, fill with median, cast to int
    if 'driver_age' in df.columns:
        df['driver_age'] = pd.to_numeric(df['driver_age'], errors='coerce')
        df['driver_age'] = df['driver_age'].fillna(df['driver_age'].median()).astype(int)

    # Convert 'stop_date' to datetime
    if 'stop_date' in df.columns:
        df['stop_date'] = pd.to_datetime(df['stop_date'], errors='coerce')

    # Convert 'stop_time' to time only (if in HH:MM:SS or HH:MM format)
    if 'stop_time' in df.columns:
        df['stop_time'] = pd.to_datetime(df['stop_time'], errors='coerce').dt.time

    return df

# Load data from the database and clean it
raw_df = pd.read_sql("SELECT * FROM traffic_stops", create_connection())
data = clean_data(raw_df)
# stop duration options
durations = data['stop_duration'].dropna().unique().tolist()
durations = sorted(durations) if durations else ["0-15 Min", "16-30 Min", "30+ Min"]

# Streamlit app configuration    

st.set_page_config(page_title="SecureCheck Police Data Analysis", layout="wide")


st.title(":blue[🚨 SecureCheck: A Python-SQL Digital Ledger for Police Post Logs 👮‍♀️]")  # visible title
st.header("Overview")
query = "Select * from traffic_stops"
data = fetch_data(query)
st.dataframe(data, use_container_width=True) # Display the data in a table

st.header("📈:blue[Essential Statistics]")  # subtitle

# Calculate essential statistics
total_stops = len(data)
total_arrests = data['stop_outcome'].value_counts().get('Arrest', 0)  # Count of 'Arrest' in stop_outcome
total_warnings = data['stop_outcome'].value_counts().get('Warning', 0) # Count of 'Warning' in stop_outcome
total_searches = data['search_conducted'].sum() # Count of True in search_conducted
drug_searches = (data['drugs_related_stop'] == True).sum() # Count of True in drugs_related_stop
unique_violations = data['violation'].nunique() # Count of unique violations


col1, col2, col3, col4, col5,col6 = st.columns(6)
col1.metric("🚗 Total Stops", f"{total_stops:,}")
col2.metric("📈 Total Arrests", f"{total_arrests}")
col3.metric("⚠️ Total Warnings", f"{total_warnings}")
col4.metric("🔍 Stops with Search", f"{total_searches:,}")
col5.metric("💊 Drug-Related Searches", f"{drug_searches:,}")
col6.metric("🛑 Unique Violations", f"{unique_violations:,}")

#Data Visulaization

# Prepare data for chart
metrics_data = {
    "Metric": [
        "Total Stops",
        "Total Arrests",
        "Total Warnings",
        "Stops with Search",
        "Drug-Related Searches",
        "Unique Violations"
    ],
    "Value": [
        total_stops,
        total_arrests,
        total_warnings,
        total_searches,
        drug_searches,
        unique_violations
    ]
}

# Create DataFrame
metrics_df = pd.DataFrame(metrics_data)

tab1, tab2 = st.tabs(["🧮 Categorical Insights", "🧬 Gender Insights"])

# Draw bar chart
with tab1:
    st.subheader("📊 Metrics Visualization")

    fig = px.bar(metrics_df, x="Metric", y="Value", color="Metric", text="Value", 
             title="Traffic Stop Metrics", 
             color_discrete_sequence=px.colors.qualitative.Set2)

    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False, height=450)

    st.plotly_chart(fig, use_container_width=True)


# Pie chart for gender distribution in drug-related stops
with tab2:
    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")

    # Filter only drug-related stops
    drug_related = data[data['drugs_related_stop'] == True]

    # Check if gender column exists and has data
    if 'driver_gender' in drug_related.columns and not drug_related['driver_gender'].isnull().all():
        gender_counts = drug_related['driver_gender'].value_counts()

        # Create pie chart
        fig = px.pie(
            names=gender_counts.index,
            values=gender_counts.values,
            title="💊 Gender Distribution in Drug-Related Stops",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Column `driver_gender` not found or has only null values.")



st.header("💡Medium Insights") # Medium queries

selected_query = st.selectbox("Select an advanced query to run:",[
"1: What are the top 10 vehicle_Number involved in drug-related stops?",
"2: Which vehicles were most frequently searched?",
"3: Which driver age group had the highest arrest rate?",
"4: What is the gender distribution of drivers stopped in each country?",
"5: Which race and gender combination has the highest search rate?",
"6: What time of day sees the most traffic stops?",
"7: What is the average stop duration for different violations?",
"8: Are stops during the night more likely to lead to arrests?",
"9: Which violations are most associated with searches or arrests?",
"10: Which violations are most common among younger drivers (<25)?",
"11: Is there a violation that rarely results in search or arrest?",
"12: Which countries report the highest rate of drug-related stops?",
"13: What is the arrest rate by country and violation?",
"14: Which country has the most stops with search conducted?",
])


query_map = {
"1: What are the top 10 vehicle_Number involved in drug-related stops?" : """Select vehicle_number, drugs_related_stop 
from traffic_stops 
where drugs_related_stop = TRUE limit 10""",
"2: Which vehicles were most frequently searched?" : """select vehicle_number, count(*) as search_count
from traffic_stops 
where search_conducted = TRUE group by vehicle_number order by search_count desc limit 1""",
"3: Which driver age group had the highest arrest rate?" : """select 
	case
	when driver_age <= 18 then 'under18'
	when driver_age <= 25 then '18-25'
	when driver_age <= 35 then '26-35'
	when driver_age <= 50 then '36-50'
	when driver_age <= 65 then '51-65'
	else '65+'
end as age_group,
    driver_age,
    avg(case when is_arrested = 'True' then 1 else 0 END) as arrest_rate
from 
    traffic_stops
group by 
    driver_age
order by 
    arrest_rate DESC
limit 1;""",
"4: What is the gender distribution of drivers stopped in each country?" : """select
    country_name,
    driver_gender,
    count(*) as num_stops
from
    traffic_stops
group by
    country_name,
    driver_gender
order by
    country_name,
    driver_gender;""",
"5: Which race and gender combination has the highest search rate?" : """select
    driver_race,
    driver_gender,
    count(*) filter (where search_conducted = TRUE) as num_searches,
    count(*) as total_stops,
    round(count(*) filter (where search_conducted = TRUE) * 100.0 / count(*), 2) as search_rate
from
    traffic_stops
group by
    driver_race,
    driver_gender
order by
    search_rate desc
limit 1;""",
"6: What time of day sees the most traffic stops?" : """select 
extract (hour from stop_time) as hour_of_day,
count(*) as no_of_stops
from traffic_stops
where stop_time IS NOT NULL
group by hour_of_day
order by no_of_stops desc
limit 1;""",
"7: What is the average stop duration for different violations?" : """select violation,
round(avg(case
	when stop_duration = '0-15 Min' then 15
	when stop_duration = '16-30 Min' then 30
	when stop_duration = '30+ Min' then 45
end),3) as avg_duration
from traffic_stops
where stop_duration is not null
group by violation
order by avg_duration desc;""",
"8: Are stops during the night more likely to lead to arrests?" : """select 
  case when extract(HOUR from stop_time::time) between 6 and 17 then 'Day'
    else 'Night'
  end as time_of_day,
  count(*) as total_stops,
  sum(case when is_arrested = 'True' then 1 else 0 end) as total_arrests,
  round(sum(case when is_arrested = 'True' then 1 else 0 END) * 100.0 / count(*),2
  ) as arrest_rate_percentage
from traffic_stops
group by time_of_day;""",
"9: Which violations are most associated with searches or arrests?" : """select 
  violation,
  count(*) as total_stops,
  sum(case when search_conducted = 'True' then 1 else 0 end) as total_searches,
  sum(case when is_arrested = 'True' then 1 else 0 end) as total_arrests,
  round(sum(case when search_conducted = 'True' then 1 else 0 end) * 100.0 / count(*), 2) as search_rate_percentage,
  round(sum(case when is_arrested = 'True' then 1 else 0 end) * 100.0 / count(*), 2) as arrest_rate_percentage
from traffic_stops
group by violation
order by total_searches desc, total_arrests desc;""",
"10: Which violations are most common among younger drivers (<25)?" : """select violation,
count(*) as young_driver_stops
from traffic_stops
where driver_age < 25
group by violation
order by young_driver_stops desc;""",
"11: Is there a violation that rarely results in search or arrest?" : """select violation,
	count(*) as total_stops,
	sum(case when search_conducted = TRUE then 1 else 0 end) as total_searches,
	sum(case when is_arrested = TRUE then 1 else 0 end) as total_arrests,
	round(sum(case when search_conducted = TRUE then 1 else 0 end) *100.0 / count(*),2) as search_percent,
	round(sum(case when is_arrested = TRUE then 1 else 0 end) *100.0 / count(*),2) as arrest_percent
from traffic_stops
Group by violation
order by total_searches asc, total_arrests asc
limit 5;""",
"12: Which countries report the highest rate of drug-related stops?" : """select country_name,
count(*) as total_stops,
sum(case when drugs_related_stop = TRUE then 1 else 0 end) as total_drug_related_stops,
round(sum(case when drugs_related_stop = TRUE then 1 else 0 end) * 100.0 / count(*), 2) as total_drug_related_stops_percent
from traffic_stops
group by country_name
order by total_drug_related_stops_percent desc;""",
"13: What is the arrest rate by country and violation?" : """select country_name, violation,
count(*) as total_stops,
sum(case when is_arrested = TRUE then 1 else 0 end) as total_arrests,
round(sum(case when is_arrested = TRUE then 1 else 0 end) *100.0 / count(*),2) as arrest_percent
from traffic_stops
group by country_name, violation
order by arrest_percent desc;""",
"14: Which country has the most stops with search conducted?" : """select country_name,
count(*) as total_stops_per_country
from traffic_stops
where search_conducted = TRUE
group by country_name
order by total_stops_per_country desc
limit 1;"""
}

#Show the query code with syntax highlighting
st.subheader("SQL Query Used")
st.code(query_map[selected_query], language='sql')  

if st.button("Run Query"): #run the selected query
    result = fetch_data(query_map[selected_query]) #fetch data based on the selected query
    if not result.empty: #render the result if not empty
        st.write(result)
    else:
        st.warning("No data found for the selected query.") #warning if no data found

st.header("🔍Complex Insights") # Complex Queries

# Dropdown for complex queries
selected_query = st.selectbox(" Select a complex query to run:", [
    "1: Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions",
    "2: Driver Violation Trends Based on Age and Race (Join with Subquery)",
    "3: Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day",
    "4: Violations with High Search and Arrest Rates (Window Function)",
    "5: Driver Demographics by Country (Age, Gender, and Race)",
    "6: Top 5 Violations with Highest Arrest Rates"
])

query_map = {
"1: Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions" : """SELECT 
    country_name,
    year,
    total_stops,
    total_arrests,
    ROUND(total_arrests * 100.0 / NULLIF(total_stops, 0), 2) AS arrest_rate,
    SUM(total_stops) OVER (PARTITION BY country_name ORDER BY year) AS cumulative_stops,
    SUM(total_arrests) OVER (PARTITION BY country_name ORDER BY year) AS cumulative_arrests
FROM (
    SELECT 
        country_name,
        EXTRACT(YEAR FROM stop_date) AS year,
        COUNT(*) AS total_stops,
        COUNT(*) FILTER (WHERE is_arrested = TRUE) AS total_arrests
    FROM 
        traffic_stops
    GROUP BY 
        country_name, year
) AS yearly_stats
ORDER BY 
    country_name, year;""",

"2: Driver Violation Trends Based on Age and Race (Join with Subquery)" : """    
 -- Subquery: Count of violations by driver age and race
WITH age_race_violations AS (
    SELECT 
        driver_age,
        driver_race,
        violation,
        COUNT(*) AS stop_count
    FROM 
        traffic_stops
    WHERE 
        driver_age IS NOT NULL AND driver_race IS NOT NULL AND violation IS NOT NULL
    GROUP BY 
        driver_age, driver_race, violation
),

-- Subquery: Total stops by driver age and race
age_race_totals AS (
    SELECT 
        driver_age,
        driver_race,
        COUNT(*) AS total_stops
    FROM 
        traffic_stops
    WHERE 
        driver_age IS NOT NULL AND driver_race IS NOT NULL
    GROUP BY 
        driver_age, driver_race
)

-- Final Join to calculate % of each violation type per age-race group
SELECT 
    v.driver_age,
    v.driver_race,
    v.violation,
    v.stop_count,
    t.total_stops,
    ROUND(v.stop_count * 100.0 / t.total_stops, 2) AS violation_percent
FROM 
    age_race_violations v
JOIN 
    age_race_totals t
ON 
    v.driver_age = t.driver_age AND v.driver_race = t.driver_race
ORDER BY 
    violation_percent DESC
LIMIT 100;
""",

"3: Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day" : """SELECT 
    EXTRACT(YEAR FROM stop_date) AS stop_year,
    TO_CHAR(stop_date, 'Month') AS stop_month_name,
    EXTRACT(MONTH FROM stop_date) AS stop_month,
    EXTRACT(HOUR FROM stop_time::time) AS stop_hour,
    COUNT(*) AS total_stops
FROM 
    traffic_stops
WHERE 
    stop_date IS NOT NULL AND stop_time IS NOT NULL
GROUP BY 
    stop_year, stop_month_name, stop_month, stop_hour
ORDER BY 
    stop_year, stop_month, stop_hour;
""",

"4: Violations with High Search and Arrest Rates (Window Function)" : """SELECT *
FROM (
    SELECT 
        violation,
        COUNT(*) AS total_stops,
        SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches,
        SUM(CASE WHEN is_arrested = 'True' THEN 1 ELSE 0 END) AS total_arrests,
        ROUND(SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS search_rate,
        ROUND(SUM(CASE WHEN is_arrested = 'True' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate,
        RANK() OVER (ORDER BY 
            SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 1.0 / COUNT(*) DESC
        ) AS search_rank,
        RANK() OVER (ORDER BY 
            SUM(CASE WHEN is_arrested = 'True' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) DESC
        ) AS arrest_rank
    FROM 
        traffic_stops
    WHERE 
        violation IS NOT NULL
    GROUP BY 
        violation
) AS ranked_data
ORDER BY 
    search_rank + arrest_rank
LIMIT 10;
""",

"5: Driver Demographics by Country (Age, Gender, and Race)" : """SELECT 
    country_name, 
    driver_age, 
    driver_gender, 
    driver_race
FROM 
    traffic_stops
GROUP BY 
    country_name, 
    driver_age, 
    driver_gender, 
    driver_race
ORDER BY 
    country_name, 
    driver_age;""",

"6: Top 5 Violations with Highest Arrest Rates" : """SELECT 
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = 'True' THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(SUM(CASE WHEN is_arrested = 'True' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate
FROM 
    traffic_stops
WHERE 
    violation IS NOT NULL
GROUP BY 
    violation
ORDER BY 
    arrest_rate DESC
LIMIT 5;"""
}

#Show the query code with syntax highlighting
st.subheader("SQL Query Used")
st.code(query_map[selected_query], language='sql')  

if st.button("Execute Query"): #run the selected query
    result = fetch_data(query_map[selected_query]) #fetch data based on the selected query
    if not result.empty: #render the result if not empty
        st.write(result)
    else:
        st.warning("No data found for the selected query.") #warning if no data found

st.markdown("---")
st.markdown("🔧 Crafted with care for 👮 Law Enforcement — by SecureCheck")

st.header("🗂️ Filter Records by Text Input")

st.markdown("Enter the details to get the natural language prediction of the stop outcome based on the input text.")

st.header("🤖 Add Stop Data & Get Outcome Prediction")

# Input fields
with st.form("log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time", step=60)  # 60 seconds step
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["M", "F"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=30)
    driver_race = st.text_input("Driver Race")
    was_search_conducted = st.selectbox("Was a Search Conducted?", ["0","1"])
    search_type = st.text_input("Search Type")
    was_it_drugs_related = st.selectbox("Was it Drugs Related?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", ["0-15 Min", "16-30 Min", "30+ Min"])
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button("Predict Stop Outcome and Violation")

if submitted:
  
    # Filtered data prediction
    filtered_data = data[
        (data['driver_gender'] == driver_gender) &
        (data['driver_age'] == driver_age) &
        (data['search_conducted'] == int(was_search_conducted)) &
        (data['stop_duration'] == stop_duration) &
        (data['drugs_related_stop'] == int(was_it_drugs_related)) 
    ]
    st.write("Matching rows found:", len(filtered_data))
    st.dataframe(filtered_data.head())  # Preview matched data
    
    # Predict outcome based on the input text
    if not filtered_data.empty:
        predicted_outcome = filtered_data['stop_outcome'].mode()[0]
        predicted_violation = filtered_data['violation'].mode()[0]
    else:   
        predicted_outcome = "Warning"
        predicted_violation = "Speeding"


    # ✅ Convert gender code to full text
    gender_full = "Male" if driver_gender == "M" else "Female"

    # Natural language summary
    search_text = "A search was conducted" if int(was_search_conducted) else "No search was conducted"
    drug_text = "It was drugs related" if int(was_it_drugs_related) else "It was not drugs related"

    st.markdown(f"""
    📝 **Prediction Summary ***
        
    **Predicted Stop Outcome:** {predicted_outcome} \n
    **Predicted Violation:** {predicted_violation}

    **Details:**
    📢A {driver_age}-year old {gender_full} driver in {country_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}
    {search_text}, and {drug_text.lower()}.
    Stop duration: **{stop_duration}**.
    Vehicle Number: **{vehicle_number}**.
    """)


st.markdown("---")

st.image("D:/proj/191088732.jpg", caption="🔒 Empowering Smart Policing with Data", width= 900 )

        
    







