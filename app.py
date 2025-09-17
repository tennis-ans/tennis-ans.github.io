import mimetypes
import os
import tempfile

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from supabase import Client, create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/data")
def data():
    return send_from_directory("data", "index.html")


@app.route("/files", methods=["GET"])
def list_files():
    try:
        res = supabase.storage.from_("charted_data").list("uploads")
        files_list = []

        for item in res:
            filename = item["name"]
            parts = filename.split("_")
            year = parts[0] if parts else "N/A"
            # Get public URL (just the string)
            public_url = supabase.storage.from_("charted_data").get_public_url(
                f"uploads/{filename}"
            )

            # Try to fetch the .txt content to extract Event & Video Url
            event_name = filename
            video_url = None
            try:
                txt_data = supabase.storage.from_("charted_data").download(
                    f"uploads/{filename}"
                )
                content = (
                    txt_data.decode("utf-8")
                    if isinstance(txt_data, bytes)
                    else txt_data
                )
                import re

                event_match = re.search(r"\[Event:\s*(.*?)\]", content, re.IGNORECASE)
                video_match = re.search(
                    r"\[Video Url:\s*(.*?)\]", content, re.IGNORECASE
                )
                if event_match:
                    event_name = event_match.group(1)
                if video_match:
                    video_url = video_match.group(1)
            except Exception as e:
                print(f"Failed to parse {filename}: {e}")

            files_list.append(
                {
                    "name": filename,
                    "event": event_name,
                    "url": public_url,
                    "video_url": video_url,
                    "year": year,
                }
            )

        return jsonify(files_list)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files["file"]
        filename = file.filename

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        # Guess MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            mime_type = "application/octet-stream"

        # Upload using file path
        res = supabase.storage.from_("charted_data").upload(
            f"uploads/{filename}", tmp_path, {"content-type": mime_type}
        )

        print("Upload response:", res)

        # Delete temporary file
        os.remove(tmp_path)

        # Generate public URL
        public_url = supabase.storage.from_("charted_data").get_public_url(
            f"uploads/{filename}"
        )

        return jsonify(
            {
                "message": "Successfully uploaded! Thank you for contributing to TANS community!",
                "file_url": public_url,
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
