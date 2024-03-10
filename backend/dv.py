# import os
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# def load_cleaned_data(user_id):
#     """
#     Load cleaned data for a given user_id if it exists.
#     """
#     cleaned_data_path = os.path.join('cleaned_data', f"{user_id}_cleaned.csv")
#     if os.path.exists(cleaned_data_path):
#         df = pd.read_csv(cleaned_data_path)
#         return df
#     else:
#         print("Cleaned data not found for this user.")
#         return None

# user_id = "some_user_id"  # This could be input from the user or any other mechanism
# df = load_cleaned_data(user_id)



# def is_identifier_col(df, col):
#     """
#     Check if the column is likely an identifier.
#     """
#     unique_values = df[col].nunique()
#     total_values = len(df)
    
#     if unique_values / total_values > 0.8:  # If more than 80% values are unique
#         return True
#     return False

# def is_low_variability_col(df, col):
#     """
#     Check if the column has low variability.
#     """
#     if df[col].dtype in ['float64', 'int64']:
#         if df[col].var() < 0.1:
#             return True
#     elif df[col].nunique() > 30:  # If a non-numeric column has more than 30 unique values
#         return True
#     return False

# def is_likely_uninsightful_name(col_name):
#     """
#     Check if the column name suggests it's likely less insightful.
#     """
#     less_insightful_keywords = ['id', 'code', 'length', 'name', 'prefix', 'postal']
#     if any(keyword in col_name for keyword in less_insightful_keywords):
#         return True
#     return False

# def identify_features_for_visualization(df):
#     """
#     Identifies continuous numeric features in the dataframe for potential visualization.
#     """
#     all_cols = df.columns.tolist()
#     meaningful_cols = []
    
#     for col in all_cols:
#         if (not is_identifier_col(df, col)) and (not is_low_variability_col(df, col)) and (not is_likely_uninsightful_name(col)):
#             meaningful_cols.append(col)
    
#     return meaningful_cols


# def generate_visualization(df, column_name, plot_type="histogram"):
#     """
#     Generates visualizations based on the plot_type and column_name.
#     """
#     plt.figure(figsize=(10, 6))
    
#     if plot_type == "histogram":
#         sns.histplot(df[column_name])
#         plt.ylabel('Frequency')
#     elif plot_type == "boxplot":
#         sns.boxplot(y=df[column_name])
#     elif plot_type == "kde":
#         sns.kdeplot(df[column_name])
#     elif plot_type == "bar":
#         df[column_name].value_counts().plot(kind='bar')
#         plt.ylabel('Frequency')
#     elif plot_type == "pie" and df[column_name].nunique() < 10:
#         df[column_name].value_counts().plot(kind='pie')
#     else:
#         print(f"Plot type {plot_type} not recognized or not suitable for the column {column_name}.")
#         return

#     plt.title(f'{plot_type.capitalize()} of {column_name}')
#     plt.xlabel(column_name)
#     plt.tight_layout()
#     plt.show()

#     provide_insight(df, column_name, plot_type)

# def provide_insight(df, column_name, plot_type):
#     """
#     Provides a brief insight after displaying a visualization.
#     """
#     if plot_type in ["histogram", "boxplot", "kde"]:
#         mean_val = df[column_name].mean()
#         median_val = df[column_name].median()
#         max_val = df[column_name].max()
#         min_val = df[column_name].min()
#         print(f"For {column_name}:")
#         print(f"- Average (Mean) value: {mean_val:.2f}")
#         print(f"- Middle (Median) value: {median_val:.2f}")
#         print(f"- Highest value: {max_val}")
#         print(f"- Lowest value: {min_val}")
#         print(f"This {plot_type} gives us an understanding of the distribution of the values. We can see where most values are clustered and if there are any outliers.")
#     elif plot_type in ["bar", "pie"]:
#         most_common = df[column_name].mode()[0]
#         least_common = df[column_name].value_counts().idxmin()
#         print(f"For the feature {column_name}:")
#         print(f"- The most common category is {most_common}.")
#         print(f"- The least common category is {least_common}.")
#         print(f"This {plot_type} shows the distribution of different categories.")

# def compare_two_features(df, feature1, feature2, plot_type="scatter"):
#     """
#     Generates a comparison plot between two features.
#     """
#     plt.figure(figsize=(12, 6))
    
#     if plot_type == "scatter":
#         print("Generating scatter plot...")  # Debugging statement
#         sns.scatterplot(data=df, x=feature1, y=feature2)
        
#     elif plot_type == "line":
#         sns.lineplot(data=df, x=feature1, y=feature2)
#     elif plot_type == "bar":
#         sns.barplot(data=df, x=feature1, y=feature2, estimator=sum)  # estimator can be mean, median, sum, etc.
#     else:
#         print(f"Plot type {plot_type} not recognized.")
#         return
    
#     plt.title(f'Comparison between {feature1} and {feature2}')
#     plt.tight_layout()
#     plt.show()

# def offer_bivariate_plots(df, feature):
#     """
#     Offers the user the option to visualize the feature in relation to another feature.
#     """
#     other_features = df.columns.drop(feature).tolist()
#     print(f"Would you like to compare {feature} with another feature?")
#     user_response = input(f"Available features for comparison are: {', '.join(other_features)}. Enter the feature name or 'no' to skip: ").strip().lower()
    
#     if user_response in other_features:
#         if df[feature].dtype in ['float64', 'int64'] and df[user_response].dtype in ['float64', 'int64']:
#             print("Scatter Plot: Displays relationship between two numeric features.")
#             resp = input(f"Do you want a scatter plot between {feature} and {user_response}? (yes/no) ").strip().lower()
#             if resp == 'yes':
#                 compare_two_features(df, feature, user_response, "scatter")

#         if 'date' in user_response:  # assuming date columns contain the keyword 'date'
#             print("Line Plot: Shows the trend of a numeric feature over time.")
#             resp = input(f"Do you want a line plot of {feature} against {user_response}? (yes/no) ").strip().lower()
#             if resp == 'yes':
#                 compare_two_features(df, feature, user_response, "line")
        
#         if df[user_response].nunique() < 10:  # limiting to categorical features with fewer unique values
#             print("Bar Plot: Displays the sum of a numeric feature for each category.")
#             resp = input(f"Do you want a bar plot of {feature} against {user_response}? (yes/no) ").strip().lower()
#             if resp == 'yes':
#                 compare_two_features(df, feature, user_response, "bar")

# def offer_plot_options(df, feature):
#     """
#     Offers the user various plotting options for the given feature.
#     """
#     print(f"Which type of plot would you like for {feature}?")
    
#     if df[feature].dtype in ['float64', 'int64']:
#         print("Histogram: Displays the distribution of data.")
#         resp = input(f"Do you want a histogram for {feature}? (yes/no) ").strip().lower()
#         if resp == 'yes':
#             generate_visualization(df, feature, "histogram")
        
#         print("Boxplot: Shows the spread & outliers of data.")
#         resp = input(f"Do you want a boxplot for {feature}? (yes/no) ").strip().lower()
#         if resp == 'yes':
#             generate_visualization(df, feature, "boxplot")
        
#         print("KDE Plot: Provides a smoothed curve of data distribution.")
#         resp = input(f"Do you want a kde for {feature}? (yes/no) ").strip().lower()
#         if resp == 'yes':
#             generate_visualization(df, feature, "kde")
    
#     elif df[feature].nunique() < 10:  # assuming categorical feature
#         print("Bar Plot: Displays frequency of each category.")
#         resp = input(f"Do you want a bar plot for {feature}? (yes/no) ").strip().lower()
#         if resp == 'yes':
#             generate_visualization(df, feature, "bar")
        
#         print("Pie Plot: Displays percentage distribution of each category.")
#         resp = input(f"Do you want a pie chart for {feature}? (yes/no) ").strip().lower()
#         if resp == 'yes':
#             generate_visualization(df, feature, "pie")


# def interactive_data_visualization(df):
#     """
#     Interactively proposes columns for visualization and generates visualizations based on user input.
#     """
#     features = identify_features_for_visualization(df)
#     if not features:
#         print("No columns found suitable for visualization.")
#         return

#     print(f"I can see these features like: {', '.join(features[:-1])} and {features[-1]} have good insights for analysis.")
    
#     for feature in features:
#         user_response = input(f"Do you want me to start analyzing the feature: {feature}? (yes/no) ").strip().lower()
#         if user_response == 'yes':
#             offer_plot_options(df, feature)
#             offer_bivariate_plots(df, feature)

            

# if __name__ == "__main__":
#     # This is a dummy dataframe for testing. You can replace this with your actual data.
#     dummy_data = {
#         'feature1': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
#         'feature2': [5, 15, 25, 35, 45, 55, 65, 75, 85, 95]
#     }
#     df = pd.DataFrame(dummy_data)
#     interactive_data_visualization(df)

