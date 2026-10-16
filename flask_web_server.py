from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import threading
import queue
import uuid
import time
import soundfile as sf
from tts_flask_service import synthesize_speech

app = Flask(__name__)
CORS(app)

job_queue = queue.Queue()
job_status = dict()
job_results = dict()

# TODO impliment this mock

OUTPUT_DIR = 'data/web_outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def worker():
    while True:
        job_id, data = job_queue.get()
        try:
            job_status[job_id] = dict(status='processing')
            sample_rate, audio_data = synthesize_speech(data['text'])
            output_path = os.path.join(OUTPUT_DIR, f'{job_id}.wav')
            sf.write(output_path, audio_data, sample_rate)
            job_results[job_id] = output_path
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
    file_path = job_results.get(job_id)
    return send_file(
        file_path,
        mimetype='audio/wav',
        as_attachment=True,
    )


if __name__ == '__main__':
    app.run(debug=True)
