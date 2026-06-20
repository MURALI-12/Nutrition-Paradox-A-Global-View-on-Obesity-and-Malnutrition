import mysql.connector as con

connection = con.connect(
    host="127.0.0.1",
    user="root",
    password="001200",
    auth_plugin='mysql_native_password',
    database='obesityMalnurition'
)
cursor =connection.cursor()
cursor.execute("CREATE TABLE obesity (Year INT,Gender VARCHAR(255),Mean_Estimate FLOAT,LowerBound FLOAT,UpperBound FLOAT,age_group VARCHAR(255),Country VARCHAR(255),Region VARCHAR(255),CI_Width FLOAT,Obesity_level VARCHAR(255))")
cursor.execute("CREATE TABLE malnutrition (Year INT,Gender VARCHAR(255),Mean_Estimate FLOAT,LowerBound FLOAT,UpperBound FLOAT,age_group VARCHAR(255),Country VARCHAR(255),Region VARCHAR(255),CI_Width FLOAT,malnutrition_level VARCHAR(255))")
connection.commit()
cursor.close()
connection.close()

