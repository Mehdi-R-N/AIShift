import pandas as pd
import numpy as np
from scipy.stats import zscore
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from statsmodels.robust import mad
import warnings
import pickle
import os


# Functions for data cleaning
# -------------------------------------------------------
CLEANING_STATES = {}

# Handle Date Formats
def check_date_conversion(df):
    recommendations = []
    for col in df.select_dtypes(include=['object']).columns:
        is_date = False
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                pd.to_datetime(df[col], infer_datetime_format=True)
                is_date = True
            except:
                pass

        if is_date:
            recommendations.append(col)

    return recommendations

def convert_date_column(df, col):
    df[col] = pd.to_datetime(df[col])

# Refactored functions
def initiate_cleaning(df, user_id):
    # Reset the state for a new cleaning session
    CLEANING_STATES[user_id] = {"step": "start"}
    return "Analyzing the data for cleaning recommendations..."

def handle_date_conversion(df, user_id, user_input=None):
    if user_id not in CLEANING_STATES:
        initiate_cleaning(df, user_id)
        
        # Check if df is not None before proceeding
    if df is None:
        # Log an error, return a message, or handle this case as appropriate for your application
        return "Error: DataFrame is None. Please load a valid DataFrame before proceeding.", True

    
    # Initial suggestion for date conversion
    if CLEANING_STATES[user_id]["step"] == "start":
        date_cols = check_date_conversion(df)
        if date_cols:
            CLEANING_STATES[user_id] = {"step": "date_conversion", "columns": date_cols, "current_idx": 0}
            col_name = date_cols[0]
            return f"Column '{col_name}' looks like it contains dates. Do you want to convert this to a date type? (yes, no, back)", False
        else:
            CLEANING_STATES[user_id]["step"] = "next_step"
            return "No columns seem to have date data. Moving on to missing values check.", True

    # Handle user's input on date conversion
    elif CLEANING_STATES[user_id]["step"] == "date_conversion":
        col_name = CLEANING_STATES[user_id]["columns"][CLEANING_STATES[user_id]["current_idx"]]
        
        # Convert user input to lowercase and remove leading/trailing whitespaces
        user_input = user_input.lower().strip()
        
        if user_input == "yes":
            convert_date_column(df, col_name)
            CLEANING_STATES[user_id]["current_idx"] += 1
        elif user_input == "back":
            if CLEANING_STATES[user_id]["current_idx"] > 0:
                CLEANING_STATES[user_id]["current_idx"] -= 1
                
                
                
        else:
            # If the user input is neither 'yes' nor 'back', re-prompt the user without changing the index
            return f"Column '{col_name}' looks like it contains dates. Do you want to convert this to a date type? (yes, no, back)", False
        
        # If there's another column to suggest for conversion
        if CLEANING_STATES[user_id]["current_idx"] < len(CLEANING_STATES[user_id]["columns"]):
           col_name = CLEANING_STATES[user_id]["columns"][CLEANING_STATES[user_id]["current_idx"]]
           return f"Column '{col_name}' looks like it contains dates. Do you want to convert this to a date type? (yes, no, back)", False
        else:
           CLEANING_STATES[user_id]["step"] = "next_step"
           return "Date column conversion complete. Moving on to missing values check.", True
        
# # ................................................................

# # Handle Missing Values

# def print_initial_missing_values_summary(df):
#     print("Initial missing values per column:")
#     missing_values = df.isnull().sum()
#     print(missing_values[missing_values > 0])

# def handle_specific_column_missing_values(df, col_name, decision_stack):
#     original_col = df[col_name].copy()

#     # Function to reset column to its original state
#     def reset_column():
#         df[col_name] = original_col
    
#     missing_count = df[col_name].isnull().sum()
    
#     # If no missing values, just return the dataframe without any prompts
#     if missing_count == 0:
#         return df, None
    
#     total_count = len(df[col_name])
#     missing_percentage = (missing_count / total_count) * 100

#     print(f"The column '{col_name}' has {missing_count} missing values, which is {missing_percentage:.2f}% of the data.")
#     decision = get_user_input("Do you want to remove these missing values? (yes, no, back): ", ["yes", "no", "back"])

#     if decision == "back":
#         decision_stack.pop_and_execute()
#         return df, "back"

#     if decision == "yes":
#         decision_stack.push(reset_column)
#         if missing_percentage < 10:
#             recommendation = get_user_input("Since this feature has less than 10 percent missing values, I recommend removing the rows with missing values in this feature instead of deleting the entire column. Do you want me to proceed with removing those rows? (yes, no, back): ", ["yes", "no", "back"])
            
#             if recommendation == 'back':
#                 return df, "back"
            
#             if recommendation == 'yes':
#                 df.dropna(subset=[col_name], inplace=True)
#             else:
#                 decision_stack.push(reset_column)
        
#             df.drop(col_name, axis=1, inplace=True)
#         else:
#             df.drop(col_name, axis=1, inplace=True)
#     else:
#         # Check if column is numeric or categorical/text
#         if np.issubdtype(df[col_name].dtype, np.number):
#             choice = get_user_input("Choose how to fill: mean, median, or specific value (or back to return): ", ["mean", "median", "specific value", "back"])
            
#             if choice == "back":
#                 return df, "back"

#             if choice == 'mean':
#                 df[col_name].fillna(df[col_name].mean(), inplace=True)
#             elif choice == 'median':
#                 df[col_name].fillna(df[col_name].median(), inplace=True)
#             elif choice == 'specific value':
#                 value = float(input(f"Enter the specific value for {col_name}: "))
#                 df[col_name].fillna(value, inplace=True)
#         else:
#             value = input(f"The column '{col_name}' is categorical or text. Enter the value you'd like to fill the missing values with (or type 'back' to return): ")
            
#             if value.lower() == 'back':
#                 return df, "back"

#             df[col_name].fillna(value, inplace=True)

#     return df, None  # Return None if there's no status to report



# def print_missing_values_summary(df):
#     missing_values = df.isnull().sum()
#     if missing_values.sum() == 0:
#         print("No missing values found in the dataset.")
#     else:
#         print("Missing values per column:")
#         print(missing_values)
        
# def check_for_missing_values(df):
#     decision_stack = DecisionStack()
#     missing_values = df.isnull().sum()
#     missing_values = missing_values[missing_values > 0]  # This line ensures we only process columns with missing values

#     for col_name in missing_values.index:
#         df, status = handle_specific_column_missing_values(df, col_name, decision_stack)
#         if status == "back":
#             decision_stack.clear()
#             return check_for_missing_values(df)
#     return df
# # ------------------------------------------

# #  Handle Outliers
# def modified_zscore(series):
#     median = series.median()
#     deviation_from_median = series - median
#     median_abs_deviation = mad(series)
#     return deviation_from_median / (1.4826 * median_abs_deviation)

# def check_outliers(df, method="combined", threshold=2):
#     recommendations = []
#     numeric_columns = df.select_dtypes(include=['number'])
#     for col in numeric_columns.columns:
#         if col.endswith("_id") or df[col].nunique() < 10:
#             continue

#         if method == "zscore":
#             outliers = np.abs(zscore(df[col].dropna())) > threshold
#         elif method == "iqr":
#             Q1 = df[col].quantile(0.25)
#             Q3 = df[col].quantile(0.75)
#             IQR = Q3 - Q1
#             outliers = ~df[col].between(Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
#         elif method == "combined":
#             z_scores = zscore(df[col].dropna())
#             m_z_scores = modified_zscore(df[col].dropna())
#             outliers = (np.abs(z_scores) > threshold) & (np.abs(m_z_scores) > threshold)

#         if outliers.any():
#             recommendations.append(col)

#     return recommendations


# def evaluate_outlier_options(df, col, options):
#     best_mse, best_option = float('inf'), None
#     temp_df = df.select_dtypes(include=['number']).dropna()
#     X_train, X_test, y_train, y_test = train_test_split(temp_df.drop(columns=[col]), temp_df[col], test_size=0.2, random_state=42)
#     for option, transform_func in options.items():
#         temp_col = transform_func(df[col])
#         if isinstance(temp_col, np.ndarray):
#             temp_col = pd.Series(temp_col, index=df.index)  # Convert to a pandas Series
#         available_indices = temp_col.dropna().index.intersection(X_train.index)
#         model = LinearRegression().fit(X_train.loc[available_indices], temp_col.loc[available_indices])
#         mse = mean_squared_error(y_test, model.predict(X_test))
#         if mse < best_mse:
#             best_mse, best_option = mse, option

#     return best_option

# def evaluate_and_handle_outliers(df):
#     outlier_columns = check_outliers(df) 

#     for col in outlier_columns:
#         print(f"Analyzing column '{col}' to find the best way to handle outliers...")

#         # Possible outlier handling options
#         mean = df[col].mean()
#         median = df[col].median()
#         std_dev = df[col].std()

#         options = {
#     'clip': lambda x: x.clip(lower=mean - 2 * std_dev, upper=mean + 2 * std_dev).reindex(df.index),
#     'replace': lambda x: pd.Series(np.where(np.abs(zscore(x)) > 2, median, x), index=df.index),
#     'remove': lambda x: x,  
#     'transform': lambda x: pd.Series(np.log1p(x), index=df.index),  
#     'ignore': lambda x: x
# }

#         best_option = evaluate_outlier_options(df, col, options)

#         print(f"Best suggestion for column '{col}': {best_option.capitalize()} outliers.")
#         print("Here are other options:")
#         for idx, option_name in enumerate(options.keys()):
#             print(f"{idx}. {option_name}")

#         user_choice = int(input("Enter the number of your choice: "))
#         chosen_option = list(options.keys())[user_choice]
#         df[col] = options[chosen_option](df[col])

#         
#         if chosen_option == "remove":
#             df = df.loc[~(np.abs(zscore(df[col])) > 2)]

#     print("Outliers handled.")
#     return df



# # -----------------------------------------------------------------

# # Handle Unnecessary Values

# def remove_unnecessary_values(df, variance_threshold=0.01):
#     drop_columns = []
#     for col in df.columns:
#         if df[col].nunique() == 1:
#             drop_columns.append(col)
#         elif df[col].dtype == 'number' and df[col].var() < variance_threshold:
#             drop_columns.append(col)

#     if drop_columns:
#         decision = user_decision(f"Would you like to drop the following unnecessary columns? {', '.join(drop_columns)} (yes/no): ")
#         if decision == 'yes':
#             df.drop(columns=drop_columns, inplace=True)
#             print("Unnecessary columns removed.")
#         else:
#             print("No changes made to unnecessary columns.")
#     else:
#         print("No unnecessary columns found.")


# # ---------------------------------------------------------------

# #  Handle Duplications
# def handle_duplicates(df):
#     # Handle duplicate rows
#     duplicates_rows = df.duplicated()
#     if duplicates_rows.any():
#         decision = user_decision(f"{duplicates_rows.sum()} duplicate rows found. Would you like to remove them? (yes/no): ")
#         if decision == 'yes':
#             df.drop_duplicates(inplace=True)
#             print("Duplicate rows removed.")
#         else:
#             print("No changes made to duplicate rows.")
#     else:
#         print("No duplicate rows found.")

#     # Handle duplicate columns
#     duplicates_columns = df.columns[df.T.duplicated()]
#     if duplicates_columns.any():
#         decision = user_decision(f"{duplicates_columns.size} duplicate columns found. Would you like to remove them? (yes/no): ")
#         if decision == 'yes':
#             # Remove the duplicate columns
#             df = df.loc[:, ~df.columns.duplicated(keep='first')]
#             print("Duplicate columns removed.")
#         else:
#             print("No changes made to duplicate columns.")
#     else:
#         print("No duplicate columns found.")

# # --------------------------------------------------------------
# #  Handle Typos
# def avoid_typos(df):
#     for col in df.select_dtypes(include=['object']).columns:
#         # Check for inconsistencies such as mixed capitalization or extra spaces
#         has_mixed_case = any(s != s.lower() and s != s.upper() for s in df[col].dropna())
#         has_extra_spaces = any(s != s.strip() for s in df[col].dropna())

#         # If inconsistencies are found, prompt the user
#         if has_mixed_case or has_extra_spaces:
#             decision_message = f"Column '{col}' appears to have inconsistencies such as mixed capitalization or extra spaces. Would you like to standardize the text in this column? (yes/no): "
#             decision = user_decision(decision_message)

#             if decision == 'yes':
#                 df[col] = df[col].str.strip().str.lower()
#                 print(f"Standardized text in column '{col}'.")
#             else:
#                 print(f"No changes made to column '{col}'.")
#         else:
#             print(f"Column '{col}' appears to be consistent. No changes made.")
            
# # --------------------------------------------------------------
# #  Handle Translate Language
# def translate_language(df, col, src_lang, target_lang):
#     # A skeleton for translating text in a specific column

# # ----------------------------------------------------------------


# # Function to report the identified issues to the user
# def report_issues(df):
#     print("\nAnalyzing dataset for potential cleaning issues...")
    
#     # Check date conversion
#     date_conversion_issues = check_date_conversion(df)
#     if date_conversion_issues:
#         print("\nFound potential date conversion issues in the following columns:")
#         for rec in date_conversion_issues:
#             print(rec)
#     else:
#         print("\nNo date conversion issues found.")
    
#     # Check missing values
#     missing_values = df.isnull().sum()
#     missing_values = missing_values[missing_values > 0]
#     if not missing_values.empty:
#         print("\nFound issues with missing values in the following columns:")
#         print(missing_values)
#     else:
#         print("\nNo missing values found.")

#     # Check outliers
#     outlier_columns = check_outliers(df)
#     if outlier_columns:
#         print("\nFound issues with outliers in the following columns:")
#         for col in outlier_columns:
#             print(f"Column '{col}' has potential outliers.")
#     else:
#         print("\nNo outlier issues found.")
        
    

# # --------------------------------------------------------------------


# UPLOAD_DIR = 'uploads'  # Global directory for all user uploads
# CLEANED_DATA_DIR = 'cleaned_data'  # Directory for saving cleaned data

# def save_cleaned_data(df, user_id):
#     """
#     Save the cleaned dataframe to a CSV.
#     """
#     if not os.path.exists(CLEANED_DATA_DIR):
#         os.makedirs(CLEANED_DATA_DIR)

#     output_path = os.path.join(CLEANED_DATA_DIR, f"{user_id}_cleaned.csv")
#     df.to_csv(output_path, index=False)
#     return output_path

# def cleaned_data_exists(user_id):
#     """
#     Check if cleaned data exists for the given user_id.
#     """
#     cleaned_data_path = os.path.join('cleaned_data', f"{user_id}_cleaned.csv")
#     return os.path.exists(cleaned_data_path), cleaned_data_path


# def interactive_data_cleaning(df, user_id):
#     messages = ["Analyzing the data for cleaning recommendations..."]
#     original_df = df.copy()
    
#     # Check if cleaned data exists
#     data_exists, cleaned_data_path = cleaned_data_exists(user_id)
#     if data_exists:
#         # Load cleaned data if exists
#         df = pd.read_csv(cleaned_data_path)
#         print("Loaded cleaned data from previous session.")
#         return df
    
#     # Handle date conversion
#     print("\nHandling date conversion:")
#     df = handle_date_conversion(df)
    
#     # Handling missing values
#     print_initial_missing_values_summary(df)
    
#     # Check for missing values
#     decision_stack = DecisionStack()  
#     df = check_for_missing_values(df)
    
#     # Handle outliers
#     print("\nHandling outliers:")
#     df = evaluate_and_handle_outliers(df)

   

#     # Report the identified issues
#     report_issues(df)
    
#     # Remove unnecessary values
#     remove_unnecessary_values(df)
    
    
#     # Handle duplicates
#     handle_duplicates(df)

#     # Standardize text
#     avoid_typos(df)

    

#     # Summary
#     changed_columns = original_df.columns[original_df.ne(df).any()]
#     if changed_columns.any():
#         print("\nSummary of changes:")
#         for col in changed_columns:
#             print(f"- {col}")

#     # Data cleaning complete
#     print("\nData cleaning complete.")
    
#     # Saving the cleaned DataFrame to a CSV file
#     cleaned_data_path = save_cleaned_data(df, user_id)
#     print(f"Cleaned data saved to {cleaned_data_path}.")

#     return df, messages  # return the cleaned DataFrame
    
   
