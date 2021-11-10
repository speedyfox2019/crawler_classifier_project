import os, sys
top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if not top_path in sys.path:
    sys.path.insert(1, top_path)

from flask import Flask, render_template, url_for, \
    jsonify, request, send_from_directory, Blueprint, current_app

from crawler.downloader import grab_using_selenium
from crawler.ml import clasify_image
from auth import token_required

from io import BytesIO


api = Blueprint("api", __name__)

# NOTE: the @token_required annotation is there to protect the API
# at least with JWT token. For this exercise is commented out
# to allow easy testing. To enable the JWT token checking,
# uncomment this annotation.

@api.route("/search/<string:search_keyword>")
# @token_required # Uncomment to enable JWT token auth
def search_and_classify(search_keyword):
    
    # First grab the images from twitter
    images = grab_using_selenium(search_keyword, current_app.config)    

    # Clasify each image
    for img_data in images:
        clasify_image(img_data) 

    # NOTE: Need to clean up the temporary files. For this exercise
    # I left the temporary files there in case anyone wants to see it.   

    return jsonify(result=images)
    
@api.route("/upload", methods=["POST"])
# @token_required # Uncomment to enable JWT token auth
def upload_and_classify():
    images = []
    folder = current_app.config["TEMPORARY_FOLDER"]
    file_obj = request.files
    for f in file_obj:
        file = request.files.get(f)
        file_name = file.filename

        # First, save the uploaded file to a temporary folder
        uploaded_file_path = os.path.join(folder, file_name)
        print(f">> Uploaded file: {uploaded_file_path}", flush=True)
        file.save(uploaded_file_path)        

        # NOTE: Tried bypassing temporary file by storing the
        # image in bytesio, but keras' load_img() doesn't accept it
        # so I comment this out for now. In a lot of cases, bytesio
        # is better so we don't need to worry about cleaning up temp files.
        #     
        #     byte_io = BytesIO()
        #     file.save(byte_io)
        #     byte_io.seek(0)

        # Initialize an empty dict because it will be populated
        # with the classification result
        img_data = {
            "src": file_name,
            "local_file": uploaded_file_path
        }

        # Clasify this image, result will be in img_data
        clasify_image(img_data)           
        images.append(img_data)

        # NOTE: Need to clean up the temporary files. For this exercise
        # I left the temporary files there in case anyone wants to verify
        # the result.

    return jsonify(result=images)
    
