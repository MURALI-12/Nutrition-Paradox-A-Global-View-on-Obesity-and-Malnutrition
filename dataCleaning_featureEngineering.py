import requests as r
import pandas as pd
import pycountry
import mysql.connector as con


def extractData():
    urls = [
        'https://ghoapi.azureedge.net/api/NCD_BMI_30C',
        'https://ghoapi.azureedge.net/api/NCD_BMI_PLUS2C',
        'https://ghoapi.azureedge.net/api/NCD_BMI_18C',
        'https://ghoapi.azureedge.net/api/NCD_BMI_MINUS2C'
    ]
    
    dataframes = []
    for link in urls:
        print(f"Fetching: {link}")
        try:
            response = r.get(link)
            response.raise_for_status()
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            if 'value' in data:
                df = pd.DataFrame(data['value'])
                dataframes.append(df)
            else:
                print(f"No 'value' key found in response from {link}")
        except r.exceptions.RequestException as e:
            print(f"An error occurred with {link}: {e}")
    dataframes_dic ={"NCD_BMI_30C":dataframes[0],"NCD_BMI_18C":dataframes[2],"NCD_BMI_PLUS2C":dataframes[1],"NCD_BMI_MINUS2C":dataframes[3]}
    return dataframes,dataframes_dic

def add_age_group_column(dataframes):
    age_groups = ['Adult', 'Child/Adolescent', 'Adult', 'Child/Adolescent']
    for i, df in enumerate(dataframes):
        df['age_group'] = age_groups[i]

def merge_df(dataframes_dic):
    df_obesity =pd.concat([dataframes_dic['NCD_BMI_30C'],dataframes_dic['NCD_BMI_PLUS2C']],ignore_index=True)
    df_malnutrition =pd.concat([dataframes_dic['NCD_BMI_18C'],dataframes_dic["NCD_BMI_MINUS2C"]],ignore_index=True)
    return df_malnutrition,df_obesity

def filter_dataframe_byYear(df_malnutrition,df_obesity):
    df_malnutrition['TimeDimensionValue'] = pd.to_numeric(df_malnutrition['TimeDimensionValue'], errors='coerce')
    df_malnutrition.dropna(subset=['TimeDimensionValue'], inplace=True)
    mask = (df_malnutrition['TimeDimensionValue'] >= 2012) & (df_malnutrition['TimeDimensionValue'] <= 2022)
    df_malnutrition_filteredDataframe = df_malnutrition[mask]

    df_obesity['TimeDimensionValue'] = pd.to_numeric(df_obesity['TimeDimensionValue'], errors='coerce')
    df_obesity.dropna(subset=['TimeDimensionValue'], inplace=True)
    mask_1 = (df_obesity['TimeDimensionValue'] >= 2012) & (df_obesity['TimeDimensionValue'] <= 2022)
    df_obesity_filteredDataframe = df_obesity[mask_1]
    return df_malnutrition_filteredDataframe,df_obesity_filteredDataframe

def filter_columns(df_malnutrition_filteredDataframe,df_obesity_filteredDataframe):
    df_malnutrition_filteredDataframe_final= df_malnutrition_filteredDataframe[[
    'ParentLocation',
    'Dim1',
    'TimeDim',
    'Low',
    'High',
    'NumericValue',
    'SpatialDim',
    'age_group']
]
    df_obesity_filteredDataframe_final = df_obesity_filteredDataframe[[
    'ParentLocation',
    'Dim1',
    'TimeDim',
    'Low',
    'High',
    'NumericValue',
    'SpatialDim',
    'age_group']
]
    return df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final

def alter_columnName_changeGenderValues(df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final):
    df_column = {'ParentLocation':'Region', 'Dim1':'Gender', 'TimeDim':'Year', 'Low':'LowerBound', 'High':'UpperBound', 'NumericValue':'Mean_Estimate',
       'SpatialDim':'Country'}
    df_malnutrition_filteredDataframe_final.rename(columns = df_column,inplace = True)
    df_obesity_filteredDataframe_final.rename(columns = df_column,inplace = True)
    gender_values = {"SEX_BTSX":"Both",
    "SEX_FMLE":"Female",
    "SEX_MLE":"Male"}
    df_malnutrition_filteredDataframe_final['Gender'] =df_malnutrition_filteredDataframe_final['Gender'].map(gender_values)
    df_obesity_filteredDataframe_final['Gender'] =df_obesity_filteredDataframe_final['Gender'].map(gender_values)


    return df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final

def alter_country_name(df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final):
    special_cases = {
                    'GLOBAL': 'Global',
                    'WB_LMI': 'Low & Middle Income',
                    'WB_HI': 'High Income',
                    'WB_LI': 'Low Income',
                    'EMR': 'Eastern Mediterranean Region',
                    'EUR': 'Europe',
                    'AFR': 'Africa',
                    'SEAR': 'South-East Asia Region',
                    'WPR': 'Western Pacific Region',
                    'AMR': 'Americas Region',
                    'WB_UMI': 'Upper Middle Income'}
    
    def special_case(code):
        if code in special_cases:
            return special_cases[code]
        pycountry_alpha_3 = pycountry.countries.get(alpha_3 =code)
        return pycountry_alpha_3.name
    df_malnutrition_filteredDataframe_final['Country'] =df_malnutrition_filteredDataframe_final['Country'].apply(special_case)
    df_obesity_filteredDataframe_final['Country'] =df_obesity_filteredDataframe_final['Country'].apply(special_case)

def create_columnNames(df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final):
    df_malnutrition_filteredDataframe_final['CI_Width']= df_malnutrition_filteredDataframe_final ['UpperBound'] - df_malnutrition_filteredDataframe_final['LowerBound']
    df_obesity_filteredDataframe_final['CI_Width']= df_obesity_filteredDataframe_final ['UpperBound'] - df_obesity_filteredDataframe_final['LowerBound']
    def obesity_level(Mean_Estimate):
        if Mean_Estimate >= 30: 
            return 'High'
    
        elif Mean_Estimate < 25:
            return 'Low' 
        else:
            return 'Moderate'

    df_obesity_filteredDataframe_final['Obesity_level']= df_obesity_filteredDataframe_final ['Mean_Estimate'].apply(obesity_level)
   
    def malnutrition_level(Mean_Estimate):
        if Mean_Estimate >= 20:
            return 'High'
        elif Mean_Estimate < 10:
            return 'Low'
        else:
            return 'Moderate'
        
    df_malnutrition_filteredDataframe_final['malnutrition_level']=df_malnutrition_filteredDataframe_final ['Mean_Estimate'].apply(malnutrition_level)

def toCsv(df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final):
    df_malnutrition_filteredDataframe_final.to_csv('df_malnutrition.csv',index=False, encoding='utf-8')
    df_obesity_filteredDataframe_final.to_csv('df_obesity.csv',index=False, encoding='utf-8')

    
    





def main():
    dataframes,dataframes_dic = extractData()
    add_age_group_column(dataframes)
    df_malnutrition,df_obesity = merge_df(dataframes_dic)
    df_malnutrition_filteredDataframe,df_obesity_filteredDataframe = filter_dataframe_byYear(df_malnutrition,df_obesity)
    #pd.set_option('display.max_columns', None)
    df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final = filter_columns(df_malnutrition_filteredDataframe,df_obesity_filteredDataframe)
    alter_columnName_changeGenderValues(df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final)
    alter_country_name(df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final)
    create_columnNames(df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final)
    toCsv(df_malnutrition_filteredDataframe_final,df_obesity_filteredDataframe_final)


main()