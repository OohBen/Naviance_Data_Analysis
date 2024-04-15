# School Data Analysis Project

## Project Overview

This project analyzes school data to understand patterns in student acceptances across top universities. By leveraging data from Naviance, it focuses on extracting insights from student records, such as GPA, SAT scores, and type of application to determine their impact on university acceptance rates.

## Data Collection

### Identifying Data Sources
- Data was collected through network request analysis on the Naviance website.
- This approach helped identify the actual API endpoints used by Naviance, allowing direct data fetching without traditional web scraping.

### Token Acquisition
- Selenium WebDriver was used to automate the login process on Naviance to retrieve authorization tokens. This step is necessary due to the complexity of the Naviance login mechanism, which includes reCAPTCHA.

### Data Retrieval Optimization
- With the token, API endpoints were accessed directly to fetch data related to college applications, SAT scores, GPA, and acceptance statuses.
- Concurrent processing with 50 worker threads was implemented to handle large volumes of data efficiently, enhancing data retrieval speed.

## Data Analysis

### Descriptive Statistics
- Duplicates in the dataset were removed, focusing on unique combinations of GPA and SAT scores.
- Basic statistics such as average and median for GPA and SAT were calculated, along with histograms to visualize data distribution.

### Statistical Analysis
- Logistic regression was used to analyze the impact of GPA and SAT on acceptance chances.
- Chi-squared tests were conducted to explore the correlation between application types (EA, ED, RD) and acceptance rates.
- A heatmap was generated to show acceptance rates by GPA and SAT score bins.

### Insights
- The project revealed specific insights into the GPA and SAT scores required for acceptance into top universities.
- Statistical tests indicated a significant impact of application type on acceptance rates, highlighting advantages of applying early.
- No significant correlation was found between GPA or SAT scores alone and acceptance rates, suggesting other factors may also be influential.

## Challenges Encountered
- Discrepancies in data accuracy were observed due to some students not being automatically updated in the system.
- There were differences between aggregated data displayed by Naviance and individual data on the scattergram, affecting the precision of the analysis.

## Conclusion
- This analysis provided a detailed look into the factors influencing student acceptances at prestigious universities.
- The findings can assist students in understanding the importance of application strategies and academic performance in college admissions.
