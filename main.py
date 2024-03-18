from flask import Flask, jsonify, request
from concurrent.futures import ThreadPoolExecutor
from corn import async_task 
from filter import calculate_similarity, getResults
from setup import database_setup
from database import drop_all_tables
from config import DB_GENERAL, DB_INDEXED_KEYWORD, DB_INDEXED_PAGE, INDEXER_CHECK_TIME
from apscheduler.schedulers.background import BackgroundScheduler
from indexer import doIndex
import tracemalloc
tracemalloc.start()


app = Flask(__name__)
executor = ThreadPoolExecutor()
is_indexing = False  # Flag to indicate whether indexing is in progress




async def runCorn():
    global is_indexing
    if not is_indexing:
        is_indexing = True
        await doIndex()  # Await the coroutine here
        is_indexing = False

def runCornWrapper():
    asyncio.run(runCorn())

def start_app():
    runCornWrapper()
    # Create scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(runCornWrapper, 'interval', seconds=INDEXER_CHECK_TIME)
    scheduler.start()

    # Start the Flask app
    app.run(debug=False)



@app.route('/set-database', methods=['GET'])
async def set_database():
    result = await database_setup()
    return jsonify({'message': result}), 200


@app.route('/delete-database', methods=['GET'])
def delete_database():
    drop_all_tables(DB_GENERAL)
    drop_all_tables(DB_INDEXED_KEYWORD)
    drop_all_tables(DB_INDEXED_PAGE)
    return "Successfully deleted!"

@app.route('/trigger-task', methods=['POST'])
def trigger_task():
    try:
        payload = request.json
        future = executor.submit(async_task, payload)
        return jsonify({'message': 'Async task started'}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/give-result', methods=['POST'])
def give_result():
    try:
        payload = request.json
        if 'query' in payload:
            query = payload["query"]
            obj = getResults(query.lower())
            return jsonify(obj), 200
        else:
            return jsonify({'error': 'Query is missing in the payload'}), 400
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'An error occurred'}), 500

if __name__ == '__main__':
    import asyncio
    asyncio.run(start_app())
