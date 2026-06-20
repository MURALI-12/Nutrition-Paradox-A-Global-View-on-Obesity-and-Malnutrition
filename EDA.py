import requests as r
import pandas as pd
import mysql.connector as con
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def understanding_dataset():
    # Correct file loading
    df_obesity = pd.read_csv('df_obesity.csv', encoding='utf-8')
    df_malnutrition = pd.read_csv('df_malnutrition.csv', encoding='utf-8')

    # Basic structure
    print(f"SHAPE(df_obesity): \n{df_obesity.shape}")
    print(f"SHAPE(df_malnutrition.shape):\n {df_malnutrition.shape}")

    print(f"INFO(df_obesity): \n{df_obesity.info()}")
    print(f"INFO(df_malnutrition):\n {df_malnutrition.info()}")

    print(f"COLUMNS(df_obesity): \n{df_obesity.columns}")
    print(f"COLUMNS(df_malnutrition): \n{df_malnutrition.columns}")

    
    print(f"NULL VALUES OF(df_obesity): \n{df_obesity.isnull().sum()}")
    print(f"NULL VALUES OF(df_malnutrition):\n {df_malnutrition.isnull().sum()}")

    print(f"Duplicate Entries Of df_malnutrition : \n{df_malnutrition.duplicated().sum()}")
    print(f"Duplicate Entries Of df_obesity:\n {df_obesity.duplicated().sum()}")   

    
    
    #Finding Unique values and classification from each column before handlig null and duplicates
    print(f'UNIQUE VALUES FROM Gender (df_obesity):\n {df_obesity['Gender'].unique()}')
    print(f'UNIQUE VALUES FROM Country (df_obesity):\n {df_obesity['Country'].unique()}')
    print(f'UNIQUE VALUES FROM Region  (df_obesity):\n {df_obesity['Region'].unique()}')

    print(f'CLASSIFICATION OF Obesity_level: \n{df_obesity['Obesity_level'].value_counts()}')
    print(f'CLASSIFICATION OF Malnutrition_level \n {df_malnutrition['malnutrition_level'].value_counts()}')
    

    return df_malnutrition, df_obesity
def handling_missingData_duplicate_data(df_malnutrition, df_obesity):
    df_obesity_nonNull = df_obesity.dropna(subset=['Region'])
    df_malnutrition_nonNull = df_malnutrition.dropna(subset=['Region'])

    print(f"Duplicate Entries Of df_obesity After Droping na (df_obesity):\n {df_obesity_nonNull.isnull().sum()}")
    print(f"Duplicate Entries Of df_malnutrition After Droping na (df_malnutrition):\n {df_malnutrition_nonNull.isnull().sum()}")
    
    #Finding Unique values and classification from each column after handlig null and duplicates

    print(f'UNIQUE VALUES FROM Gender (df_obesity):\n {df_obesity_nonNull['Gender'].unique()}')
    print(f'UNIQUE VALUES FROM Country (df_obesity):\n {df_obesity_nonNull['Country'].unique()}')
    print(f'UNIQUE VALUES FROM Region  (df_obesity):\n {df_obesity_nonNull['Region'].unique()}')

    print(f'CLASSIFICATION OF Obesity_level: \n{df_obesity_nonNull['Obesity_level'].value_counts()}')
    print(f'CLASSIFICATION OF Malnutrition_level \n {df_malnutrition_nonNull['malnutrition_level'].value_counts()}')
    return df_malnutrition_nonNull, df_obesity_nonNull

def describing_statics_summary(df_malnutrition_nonNull, df_obesity_nonNull):
    describtion_df_obesity_nonNull = df_obesity_nonNull.describe()
    describtion_df_malnutrition_nonNull = df_malnutrition_nonNull.describe()

    print(f"DESCRIBITION(df_obesity): \n{describtion_df_obesity_nonNull}")
    print(f"DESCRIBITION(df_malnutrition): \n{describtion_df_malnutrition_nonNull}")

    describtion_df_obesity_nonNull_object = df_obesity_nonNull.describe(include='object')
    describtion_df_malnutrition_nonNull_object = df_malnutrition_nonNull.describe(include='object')

    print(f"DESCRIBITION OF OBJECTS(df_obesity): \n{describtion_df_obesity_nonNull_object}")
    print(f"DESCRIBITION OF OBJECTS(df_malnutrition): \n{describtion_df_malnutrition_nonNull_object}")

    return describtion_df_obesity_nonNull,describtion_df_malnutrition_nonNull,describtion_df_obesity_nonNull_object,describtion_df_malnutrition_nonNull_object



'''

def insert_dataframes_mysql(df_malnutrition_nonNull, df_obesity_nonNull):
    connection = con.connect(
    host="127.0.0.1",
    user="root",
    password="001200",
    auth_plugin='mysql_native_password',
    database='obesityMalnurition'
)
    cursor =connection.cursor()
    for _,row in df_malnutrition_nonNull.iterrows():
        cursor.execute(""" INSERT INTO malnutrition (Year,Gender,Mean_Estimate,LowerBound,UpperBound,age_group,Country,Region,CI_Width,malnutrition_level)
        VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s)""",(row['Year'],row['Gender'],row['Mean_Estimate'],row['LowerBound'],row['UpperBound'],row['age_group'],row['Country'],row['Region'],row['CI_Width'],row['malnutrition_level']) )       
    
    for _,row in df_obesity_nonNull.iterrows():
        cursor.execute(""" INSERT INTO obesity (Year,Gender,Mean_Estimate,LowerBound,UpperBound,age_group,Country,Region,CI_Width,Obesity_level)
        VALUES (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s)""", (row['Year'],row['Gender'],row['Mean_Estimate'],row['LowerBound'],row['UpperBound'],row['age_group'],row['Country'],row['Region'],row['CI_Width'],row['Obesity_level']) )         

    connection.commit()
    cursor.close()
    connection.close()
'''

def main():
    df_malnutrition, df_obesity = understanding_dataset()
    df_malnutrition_nonNull, df_obesity_nonNull=handling_missingData_duplicate_data(df_malnutrition, df_obesity)
    describtion_df_obesity_nonNull,describtion_df_malnutrition_nonNull,describtion_df_obesity_nonNull_object,describtion_df_malnutrition_nonNull_object = describing_statics_summary(df_malnutrition_nonNull, df_obesity_nonNull)
    

    #insert_dataframes_mysql(df_malnutrition_nonNull, df_obesity_nonNull)
    df_malnutrition_nonNull.to_csv('df_malnutrition_nonNull.csv',index=False, encoding='utf-8')
    df_obesity_nonNull.to_csv('df_obesity_nonNull.csv',index=False, encoding='utf-8')
main()