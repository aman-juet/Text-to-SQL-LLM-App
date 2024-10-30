import sqlite3

connection = sqlite3.connect("student.db")

# Create a cursor object to insert record,create table
cusror = connection.cursor()

#CREATE TABLE
table_info = """
create table STUDENT(NAME VARCHAR(25),CLASS VARCHAR(25),
SECTION VARCHAR(25),MARKS INT)
"""

cusror.execute(table_info)

## Insert RECORDS
cusror.execute('''Insert Into STUDENT values('Aman','GEN AI','A',90)''')
cusror.execute('''Insert Into STUDENT values('Jonh','GEN AI','B',100)''')
cusror.execute('''Insert Into STUDENT values('Jacob','DEVOPS','A',50)''')
cusror.execute('''Insert Into STUDENT values('Abhishek','DEVOPS','A',50)''')
cusror.execute('''Insert Into STUDENT values('Sahil','GEN AI','A',35)''')

## Display all the records

print("The Inserted Records are")
data = cusror.execute('''Select * from STUDENT''')

for row in data :
    print(row)
    
## COMMIT CHANGES IN DB
connection.commit()
connection.close()



