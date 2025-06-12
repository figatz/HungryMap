# HungryMap
Contains files and scripto to build a dashboard with some graphs and data about restaurants around the world

# 1- Business Problem Context

Your main task at this moment is to assist CEO Kleiton Guerra in identifying key points of the company by answering his questions using data!

The company HungryMap is a restaurant marketplace. In other words, its core business is to facilitate the connection and negotiations between customers and restaurants.

Restaurants register on the HungryMap platform, which provides information such as address, type of cuisine served, whether they accept reservations, if they offer delivery, and also a rating of the restaurant’s services and products, among other details.

**The Challenge**

CEO Kleiton Guerra has also been recently hired and needs to better understand the business in order to make the best strategic decisions and further boost HungryMap's growth. To do this, he requires an analysis of the company’s data and the creation of dashboards based on that analysis to answer the following questions:

### General Questions

1. How many unique restaurants are registered?
2. How many unique countries are registered?
3. How many unique cities are registered?
4. What is the total number of reviews submitted?
5. What is the total number of registered cuisine types?

### **Countries**

1. Which country has the highest number of registered cities?
2. Which country has the highest number of registered restaurants?
3. Which country has the highest number of restaurants with a price level of 4?
4. Which country has the highest number of distinct cuisine types?
5. Which country has the highest number of reviews submitted?
6. Which country has the highest number of restaurants that offer delivery?
7. Which country has the highest number of restaurants that accept reservations?
8. Which country has the highest average number of reviews per restaurant?
9. Which country has the highest average rating?
10. Which country has the lowest average rating?
11. What is the average cost of a meal for two in each country?

### **City-Level Questions**

1. Which city has the highest number of registered restaurants?
2. Which city has the most restaurants with an average rating above 4?
3. Which city has the most restaurants with an average rating below 2.5?
4. Which city has the highest average cost for a meal for two?
5. Which city has the highest number of distinct cuisine types?
6. Which city has the highest number of restaurants that accept reservations?
7. Which city has the highest number of restaurants that offer delivery?
8. Which city has the highest number of restaurants that accept online orders?

### **Restaurant-Level Questions**

1. Which restaurant has the highest number of reviews?
2. Which restaurant has the highest average rating?
3. Which restaurant has the highest cost for a meal for two?
4. Which Brazilian cuisine restaurant has the lowest average rating?
5. Which Brazilian cuisine restaurant, located in Brazil, has the highest average rating?
6. Do restaurants that accept online orders also have, on average, the highest number of reviews?
7. Do restaurants that accept reservations also have, on average, the highest meal cost for two?
8. In the United States, do Japanese cuisine restaurants have a higher average meal cost for two than American BBQ restaurants?

### **Cuisine-Type Questions**

1. Among Italian cuisine restaurants, which one has the highest average rating?
2. Among Italian cuisine restaurants, which one has the lowest average rating?
3. Among American cuisine restaurants, which one has the highest average rating?
4. Among American cuisine restaurants, which one has the lowest average rating?
5. Among Arabic cuisine restaurants, which one has the highest average rating?
6. Among Arabic cuisine restaurants, which one has the lowest average rating?
7. Among Japanese cuisine restaurants, which one has the highest average rating?
8. Among Japanese cuisine restaurants, which one has the lowest average rating?
9. Among homemade-style cuisine (“caseira”) restaurants, which one has the highest average rating?
10. Among homemade-style cuisine (“caseira”) restaurants, which one has the lowest average rating?
11. Which cuisine type has the highest average meal cost for two?
12. Which cuisine type has the highest average rating?
13. Which cuisine type has the highest number of restaurants that accept online orders and offer delivery?

# 2 - Assumptions Made for the Analysis

- **Data Accuracy**:
    
    All data provided (e.g., ratings, prices, cuisine types, delivery/reservation options) are assumed to be clean, accurate, and up to date.
    
- **Unique Entries**:
    
    Each row in the dataset represents a unique restaurant. Duplicate entries have been removed or filtered appropriately.
    
- **Cuisine Types**
    
    A restaurant can serve more than one type of cuisine. For analysis by cuisine, we take only the main cuisine from each restaurant.
    
- **Price Representation**
    
    The price for a meal for two is assumed to be expressed in the local currency but has been converted to a consistent format (e.g., USD) if necessary for cross-country comparisons. Also restaurants with prices equal to 0 were excluded.
    
- **Ties**
    
    In case of ties (e.g., multiple restaurants with the same highest rating), the first result by ID is returned unless otherwise required.
    

# 3 - Solution Strategy

### **1. Data Understanding and Cleaning**

- Import and initial inspection of the platform data.
- Treatment of missing, duplicate, or inconsistent data.
- Standardization of country, city, and cuisine names.
- Format conversions (e.g., meal prices into a consistent currency, ratings into numerical format).

### **2. Creation of Key Metrics and Indicators**

- Generate key business metrics from the data, such as:
    - Total number of restaurants, cities, countries, and reviews.
    - Average ratings, average price for two, and average number of reviews per restaurant.
    - Counts of features like delivery, reservations, and online ordering.

### 3.Development of Interactive Dashboards

- Build dynamic dashboards using Streamlit and uploaded to cloud.
- Dashboards will include:
    - Filters by country, city, and cuisine.
    - Key performance indicators (KPIs) and comparative visualizations.
    - Drill-down tables for detailed restaurant-level insights.

# 4 - **Insight Generation and Strategic Recommendations**

- Based on the analysis, highlight:
    - **Strengths** of the platform (e.g., top-performing countries or cities).
    - **Growth opportunities** (e.g., underrepresented regions or cuisines).
    - **Quality alerts** (e.g., cuisines with low ratings).
- Provide **practical suggestions** for improving performance and engagement.
- Restaurants that provide online delivery tends to have more votes in general

# 5 - Final Deliverable of the Project

Online dashboard, hosted in the cloud and accessible from any internet-connected device.

The dashboard can be accessed by the following link:

[Home · Streamlit](https://hungrymap.streamlit.app/)

# 6 - Conclusion

This project aims to equip CEO Kleiton Guerra and the HungryMap team with a clear, data-driven understanding of the company’s current performance and growth opportunities. By analyzing key metrics across restaurants, cities, countries, and cuisine types, and by delivering interactive dashboards and detailed reports, we provide actionable insights to guide strategic decisions.

The solution ensures that HungryMap can continuously monitor its marketplace dynamics, optimize its offerings, and strengthen its position in the competitive food delivery market. With this foundation, the company is well-positioned to enhance customer satisfaction, attract more restaurants, and accelerate growth sustainably.

# 7 - Next Steps

- **Iterate and Refine**
    
    Adjust analyses and dashboards based on feedback to better meet business needs.
    
- **Implement Continuous Monitoring**
    
    Establish processes for regular data updates and dashboard maintenance to support ongoing decision-making.
    
- **Reduce the number of metrics adjusting the most important ones to the CEO and the growth of the business, and if necessary creating new ones**
