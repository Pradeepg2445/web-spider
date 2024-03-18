import mysql.connector.pooling
from config import DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD
# Define your database connection details
DB_CONFIG = {
    'host': DB_HOST,
    'port': DB_PORT,
    'user': DB_USERNAME,
    'password': DB_PASSWORD,
    'pool_name': 'mypool',
    'pool_size': 30,
    'pool_reset_session': True
}
 

# Create a connection pool
db_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)


def execute_query(query, db_name, commit=False):
    connection = None
    try:
        # print(query)
        connection = db_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"USE {db_name}")  # Switch to the specified database
        cursor.execute(query)
        if commit:
            connection.commit()  # Commit the transaction if specified
        if query.strip().lower().startswith('select'):
            result = cursor.fetchall()
            return result
        else:
            return True  # Indicate successful execution for non-select queries
    except mysql.connector.Error as e:
        print(f"Error executing query: {e} query:{query}")
        return None
    finally:
        if connection:
            connection.close()

async def execute_query_async(query, db_name, commit=False):
    connection = None
    try:
        # print(query)
        connection = db_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"USE {db_name}")  # Switch to the specified database
        cursor.execute(query)
        if commit:
            await connection.commit()  # Commit the transaction if specified
        if query.strip().lower().startswith('select'):
            result = cursor.fetchall()
            return result
        else:
            return "Database Created!"  # Indicate successful execution for non-select queries
    except mysql.connector.Error as e:
        print(f"Error executing query: {e} query:{query}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print('Connection closed')

def drop_all_tables(database_name):
    try:
        connection = db_pool.get_connection()

        if connection.is_connected():
            print(f'Connected to MySQL database "{database_name}"')
            cursor = connection.cursor()

            # Select the specified database
            cursor.execute(f"USE {database_name}")

            # Get all table names
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            drop_query = " "
            # Drop each table
            for table in tables:
                table_name = table[0]
                drop_query+= f" DROP TABLE {table_name}; "

            
            cursor.execute(drop_query)

            print("All tables dropped successfully.")

    except mysql.connector.Error as e:
        print(f"Error dropping tables: {e}")

    finally:
        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print('Connection closed')


# Example usage:
# query = "SELECT * FROM your_table"
# result = execute_query(query, DB_GENERAL_NAME)
# print(result)
 