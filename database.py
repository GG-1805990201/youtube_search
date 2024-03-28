import mysql.connector
from mysql.connector import Error
from datetime import datetime


# Function to insert a new video into the MySQL database
def insert_video(title, description, publishString, thumbnailURL):
    try:
        # Convert string to datetime
        # Assuming the format 'YYYY-MM-DD HH:MM:SS'
        # Remove 'Z' and parse
        publishDateTime = datetime.fromisoformat(publishString.replace('Z', '+00:00'))

        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host='localhost',  # or your host, e.g., '127.0.0.1'
            database='YouTubeData',  # your database name
            user='root',  # your mysql username
            password='trgt@2023')  # your mysql password

        if connection.is_connected():
            cursor = connection.cursor()
            # SQL query to insert a new video
            query = """INSERT INTO Videos (Title, Description, PublishDateTime, ThumbnailURL)
                       VALUES (%s, %s, %s, %s)"""
            # Tuple of values to insert
            values = (title, description, publishDateTime, thumbnailURL)

            cursor.execute(query, values)
            connection.commit()
            print("Video inserted successfully")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

# Example usage
