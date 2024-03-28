import json

from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

from redis_config import redis_client

app = Flask(__name__)
cors = CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:5000"])


def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='YouTubeData',
            user='root',
            password='trgt@2023'
        )
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return connection


@app.route('/videos', methods=['GET'])
def fetch_videos():
    # Default values for pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Calculate offset
    offset = (page - 1) * per_page

    # Connect to the database
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection could not be established"}), 500

    cursor = connection.cursor(dictionary=True)

    try:
        # Query to fetch paginated videos sorted by PublishDateTime in descending order
        cursor.execute("""
            SELECT Title, Description, PublishDateTime, ThumbnailURL
            FROM Videos
            ORDER BY PublishDateTime DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))

        # Fetch the result
        videos = cursor.fetchall()

        return jsonify({"videos": videos, "page": page, "per_page": per_page}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/search', methods=['GET'])
def search_videos():
    # Get search query from URL parameter
    search_query = request.args.get('query', '')
    cached_response = redis_client.get(search_query)
    if cached_response:
        return jsonify({"videos": cached_response}), 200

    # Connect to the database
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Database connection could not be established"}), 500

    cursor = connection.cursor(dictionary=True)

    try:
        # SQL query to search videos by title or description, using LIKE for pattern matching
        cursor.execute("""
            SELECT Title, Description, PublishDateTime, ThumbnailURL
            FROM Videos
            WHERE Title LIKE %s OR Description LIKE %s
            ORDER BY PublishDateTime DESC
        """, ('%' + search_query + '%', '%' + search_query + '%'))

        # Fetch the result
        videos = cursor.fetchall()
        redis_client.set(search_query, json.dumps(videos), ex=60)
        return jsonify({"videos": videos}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
