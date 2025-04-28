from flask import Flask, request, jsonify
import threading
import queue
import uuid
import time

app = Flask(__name__)

job_queue = queue.Queue()
job_status = dict()
job_results = dict()

# TODO impliment this mock


def text_to_speech_service(gen_text):
    time.sleep(5)
    return './data/ramsay/outputs/1.wav'


def worker():
    while True:
        job_id, data = job_queue.get()
        try:
            job_status[job_id] = dict(status='processing')
            result = text_to_speech_service(data['text'])
            job_results[job_id] = result
            job_status[job_id] = dict(status='completed')
        except Exception as e:
            job_status[job_id] = dict(status='failed', error=e)
        finally:
            job_queue.task_done()


# Start worker as a background process
threading.Thread(
    target=worker,
    daemon=True
).start()


@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    status = job_status.get(job_id)
    if not status:
        return jsonify(dict(
            error='Job ID not found'
        ), 400)
    return jsonify(status)


@app.route('/submit', methods=['POST'])
def submit():
    req_data = request.get_json()
    gen_text = req_data.get('text')

    if not gen_text:
        return jsonify(dict(
            error='Missing "text" field'
        ), 400)

    job_id = str(uuid.uuid4())
    job_status[job_id] = dict(status='queued')
    job_queue.put((
        job_id,
        dict(text=gen_text)
    ))

    return jsonify(dict(
        job_id=job_id
    ), 202)


@app.route('/result/<job_id>', methods=['GET'])
def result(job_id):
    if job_id not in job_status.keys():
        return jsonify(dict(
            error='No such job id'
        ), 404)
    if job_status.get(job_id)['status'] != 'completed':
        return jsonify(dict(
            error='Result not ready',
            job_status=job_status.get(job_id)
        ), 400)
    result = job_results.get(job_id)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
