from flask import Flask, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def test_api():
    return jsonify({
        "message": "API is running /"
    })

@app.route('/api/transcript/<video_id>', methods=['GET'])
def get_transcript(video_id):
    try:
        english_codes = ['en']
        
        # Here's the correct cookies parameter
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id , cookies="cookies.txt")
        
        english_transcripts = {}
        
        for code in english_codes:
            try:
                transcript = transcript_list.find_transcript([code])
                english_transcripts[code] = transcript.fetch(cookies="cookies.txt")
            except Exception as e:
                print(f"No transcript found for {code}")
                continue

        if english_transcripts:
            return jsonify({
                "success": True,
                "transcripts": english_transcripts
            })
        else:
            return jsonify({
                "success": False,
                "error": "No English transcripts found"
            }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
