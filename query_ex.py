import streamlit as st
import mysql.connector as c
import pandas as pd


def get_connection():
    return c.connect(
        host="127.0.0.1",
        user="root",
        password="001200",
        auth_plugin='mysql_native_password',
        database='obesityMalnurition'
    )


queries = {
    # Obesity Queries
    "Top 5 Regions by Obesity (2022)": """
        SELECT Region, 
               ROUND(AVG(Mean_Estimate), 2) AS Avg_Obesity, 
               MAX(Obesity_level) AS Max_Obesity_Level
        FROM obesity
        WHERE Year = 2022
        GROUP BY Region
        ORDER BY Avg_Obesity DESC
        LIMIT 5
    """,

    "Top 5 Countries by Obesity": """
        SELECT country, round(AVG(mean_estimate),2) AS highest_obesity_avg 
        FROM obesity 
        GROUP BY country 
        ORDER BY highest_obesity_avg DESC 
        LIMIT 5
    """,

    "Obesity Trend in India": """
        SELECT country, year, AVG(mean_estimate) AS Obesity_trend_bymean_estimate 
        FROM obesity 
        WHERE country = 'India' 
        GROUP BY year 
        ORDER BY year ASC
    """,

    "Average Obesity by Gender": """
        SELECT gender, ROUND(AVG(mean_estimate), 2) AS Average_obesity 
        FROM obesity 
        GROUP BY gender
    """,

    "Country Count by Obesity Level and Age Group": """
        SELECT obesity_level, age_group, COUNT(DISTINCT country) AS country_count 
        FROM obesity 
        GROUP BY obesity_level, age_group
    """,

    "Top 5 Least & Most Reliable Countries (CI_Width)": """
        
            
            
        SELECT * FROM (
    SELECT country, ROUND(AVG(CI_Width), 2) AS avg_ci_width, 'High' AS category
    FROM obesity
    GROUP BY country
    ORDER BY avg_ci_width DESC
    LIMIT 5
    ) AS top_countries

    UNION ALL

    SELECT * FROM (
    SELECT country, ROUND(AVG(CI_Width), 2) AS avg_ci_width, 'Low' AS category
    FROM obesity
    GROUP BY country
    ORDER BY avg_ci_width ASC
    LIMIT 5
    ) AS bottom_countries;

            
    """,

    "Average Obesity by Age Group": """
        SELECT age_group, AVG(mean_estimate) AS avg_obesity 
        FROM obesity 
        GROUP BY age_group
    """,

    "Top 10 Consistent Low Obesity Countries": """
        SELECT Country,
               ROUND(AVG(Mean_Estimate), 2) AS avg_obesity,
               ROUND(AVG(CI_Width), 2) AS avg_ci_width,
               ROUND(AVG(Mean_Estimate) + AVG(CI_Width), 2) AS consistency_Value_Obesity
        FROM obesity
        GROUP BY Country
        ORDER BY consistency_Value_Obesity ASC
        LIMIT 10;
    """,

    "Countries where female obesity exceeds male by large margin (same year)": """
     WITH female_avg AS (
        SELECT Country, Year, AVG(Mean_Estimate) AS Female_Obesity
        FROM obesity
        WHERE Gender = 'Female' AND Year = 2022
        GROUP BY Country, Year
    ),
    male_avg AS (
        SELECT Country, Year, AVG(Mean_Estimate) AS Male_Obesity
        FROM obesity
        WHERE Gender = 'Male' AND Year = 2022
        GROUP BY Country, Year
    )

    SELECT 
        f.Country,
        f.Year,
        ROUND(f.Female_Obesity, 2) AS Female_Obesity,
        ROUND(m.Male_Obesity, 2) AS Male_Obesity,
        ROUND(f.Female_Obesity - m.Male_Obesity, 2) AS Difference
    FROM 
        female_avg f
    JOIN 
        male_avg m ON f.Country = m.Country AND f.Year = m.Year
    WHERE 
        (f.Female_Obesity - m.Male_Obesity) > 5
    ORDER BY 
        Difference DESC limit 10;

            
    """,

    "Global Obesity Percentage by Year": """
        SELECT year, ROUND(AVG(mean_estimate), 2) AS Obesity_Percentage 
        FROM obesity 
        GROUP BY year
    """,

    # Malnutrition Queries
    "Average Malnutrition by Age Group": """
        SELECT age_group, ROUND(AVG(mean_estimate), 2) AS avg_malnutrition 
        FROM malnutrition 
        GROUP BY age_group 
        ORDER BY avg_malnutrition DESC
    """,

    "Top 5 Countries by Malnutrition": """
        SELECT country, ROUND(AVG(mean_estimate), 2) AS highest_malnutrition 
        FROM malnutrition 
        GROUP BY country 
        ORDER BY highest_malnutrition DESC 
        LIMIT 5
    """,

    "Malnutrition Trend in Africa": """
        SELECT Year, Region, ROUND(AVG(mean_estimate), 2) AS malnutrition_trend 
        FROM malnutrition 
        WHERE Region = 'Africa' 
        GROUP BY year 
        ORDER BY year ASC
    """,

    "Gender-Based Average Malnutrition": """
        SELECT gender, ROUND(AVG(mean_estimate), 2) AS average_malnutrition 
        FROM malnutrition 
        GROUP BY gender 
        ORDER BY average_malnutrition DESC
    """,

    "Malnutrition Level vs CI_Width by Age Group": """
        SELECT malnutrition_level, age_group, ROUND(AVG(ci_width), 2) AS avg_CI_Width 
        FROM malnutrition 
        GROUP BY malnutrition_level, age_group 
        ORDER BY malnutrition_level
    """,

    "Yearly Malnutrition Change (India, Nigeria, Brazil)": """
        SELECT Country, Year, ROUND(AVG(Mean_Estimate), 2) AS avg_malnutrition_rate 
        FROM malnutrition 
        WHERE Country IN ('India', 'Nigeria', 'Brazil') 
        GROUP BY Country, Year 
        ORDER BY Country, Year;
    """,

    "Regions with Lowest Malnutrition": """
        SELECT Region, ROUND(AVG(mean_estimate), 2) AS lowest_malnutrition 
        FROM malnutrition 
        GROUP BY Region 
        ORDER BY lowest_malnutrition ASC
    """,

    "Countries with Increasing Malnutrition": """
        SELECT Country,
               MIN(Mean_Estimate) AS earliest_rate,
               MAX(Mean_Estimate) AS latest_rate,
               ROUND(MAX(Mean_Estimate) - MIN(Mean_Estimate), 2) AS rate_increase
        FROM malnutrition
        GROUP BY Country
        HAVING rate_increase > 0;
    """,

    "Year-wise Min/Max Malnutrition by Level": """
        SELECT year, malnutrition_level, 
               MIN(mean_estimate) AS min_value, 
               MAX(mean_estimate) AS max_values 
        FROM malnutrition 
        GROUP BY year, malnutrition_level 
        ORDER BY year ASC
    """,

    "High CI_Width Flags (>5)": """
        SELECT ci_width 
        FROM malnutrition 
        WHERE ci_width > 5 
        ORDER BY ci_width DESC;
    """,

    # Combined Queries
    "Obesity vs Malnutrition Comparison (5 Countries)": """
        SELECT o.Country,
               ROUND(AVG(o.Mean_Estimate), 2) AS avg_obesity,
               ROUND(AVG(m.Mean_Estimate), 2) AS avg_malnutrition
        FROM obesity o
        INNER JOIN malnutrition m ON o.Country = m.Country
        WHERE o.Country IN ('India', 'Nigeria', 'Brazil', 'Italy', 'Bangladesh')
        GROUP BY o.Country
        ORDER BY avg_malnutrition DESC;
    """,

    "Gender-Based Disparity in Obesity & Malnutrition": """
        SELECT o.Gender,
               ROUND(AVG(o.Mean_Estimate), 2) AS avg_obesity,
               ROUND(AVG(m.Mean_Estimate), 2) AS avg_malnutrition
        FROM obesity o
        INNER JOIN malnutrition m 
            ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender
        WHERE o.Gender IN ('Male', 'Female')
        GROUP BY o.Gender
        ORDER BY o.Gender;
    """,

    "Region-Wise Comparison (Africa vs Americas)": """
        SELECT o.Region,
               ROUND(AVG(o.Mean_Estimate), 2) AS avg_obesity,
               ROUND(AVG(m.Mean_Estimate), 2) AS avg_malnutrition
        FROM obesity o
        INNER JOIN malnutrition m 
            ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender
        WHERE o.Region IN ('Africa', 'Americas')
        GROUP BY o.Region
        ORDER BY o.Region;
    """,

    "Countries with Obesity Up & Malnutrition Down": """
        SELECT o.Country,
               ROUND(AVG(o.Mean_Estimate), 2) AS avg_obesity,
               ROUND(AVG(m.Mean_Estimate), 2) AS avg_malnutrition
        FROM obesity o
        INNER JOIN malnutrition m ON o.Country = m.Country
        GROUP BY o.Country
        HAVING avg_obesity > avg_malnutrition
        ORDER BY avg_obesity DESC, avg_malnutrition DESC;
    """,

    "Age-Wise Trend Analysis": """
        SELECT o.age_group, o.year,
               ROUND(AVG(o.Mean_Estimate), 2) AS avg_obesity,
               ROUND(AVG(m.Mean_Estimate), 2) AS avg_malnutrition
        FROM obesity o
        INNER JOIN malnutrition m ON o.year = m.year AND o.country = m.country
        GROUP BY o.age_group, o.year"""
        }


st.title("🧮 Obesity & Malnutrition Insights")
selected_query = st.selectbox("Choose a query to run:", list(queries.keys()))


if selected_query:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(queries[selected_query])
    results = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(results, columns=columns)
    st.dataframe(df)

    cursor.close()
    conn.close()
