
from flask import Flask, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from flask_cors import CORS
import os

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
        english_codes = ['en', 'en-GB', 'en-US', 'en-IN', 'en-AU', 'en-CA', 'en-NZ', 'en-ZA', 'en-IE', 'en-SG', 'en-FR']
        
        # Get the absolute path to cookies.txt in the root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cookies_path = os.path.join(root_dir, "cookies.txt")
        
        # Check if cookies file exists
        if not os.path.exists(cookies_path):
            print(f"Warning: Cookies file not found at {cookies_path}")
            cookies_path = "cookies.txt"  # Fallback to relative path
        
        print(f"Using cookies file: {cookies_path}")
        
        try:
            # List transcripts with cookies
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookies_path)
            
            english_transcripts = {}
            all_text = ""
            
            for code in english_codes:
                try:
                    # Find and fetch transcript with the same cookies file
                    transcript = transcript_list.find_transcript([code])
                    
                    # Pass cookies to fetch as well
                    transcript_data = transcript.fetch(cookies=cookies_path)
                    english_transcripts[code] = transcript_data
                    
                    # Concatenate text for the first found transcript
                    if not all_text and transcript_data:
                        all_text = " ".join([item["text"] for item in transcript_data])
                
                except Exception as e:
                    print(f"No transcript found for {code}: {str(e)}")
                    continue

            if english_transcripts:
                return jsonify({
                    "success": True,
                    "transcripts": english_transcripts,
                    "transcript": all_text  # Include the concatenated text
                })
            else:
                # Try manual approach if no transcripts found
                try:
                    print("Trying direct transcript fetch without language filtering...")
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id, cookies=cookies_path)
                    all_text = " ".join([item["text"] for item in transcript_data])
                    
                    return jsonify({
                        "success": True,
                        "transcript": all_text,
                        "manual": True
                    })
                except Exception as manual_error:
                    print(f"Manual fetch failed: {str(manual_error)}")
                    return jsonify({
                        "success": False,
                        "error": "No transcripts found"
                    }), 404
        
        except Exception as list_error:
            print(f"Error listing transcripts: {str(list_error)}")
            # Try direct transcript fetch as fallback
            try:
                print("Trying direct transcript fetch...")
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, cookies=cookies_path)
                all_text = " ".join([item["text"] for item in transcript_data])
                
                return jsonify({
                    "success": True,
                    "transcript": all_text,
                    "fallback": True
                })
            except Exception as fallback_error:
                print(f"Fallback fetch failed: {str(fallback_error)}")
                return jsonify({
                    "success": False,
                    "error": f"Failed to get transcript: {str(fallback_error)}"
                }), 404

    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
