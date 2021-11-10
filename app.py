
import os, sys
top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
if not top_path in sys.path:
    sys.path.insert(1, top_path)

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from configs.development import DevelopmentConfig as Config
from auth import User

# Create a flask object
app = Flask(__name__)

# Set configuration from file. For now we use development config
# for production, create a real production config
app.config.from_object(Config)

# Blueprints are module, for example there's a module for API
def configure_blueprints(app):
    
    if "BLUEPRINTS" in app.config:
        for key in app.config["BLUEPRINTS"]:
            bp_mod = __import__(app.config["BLUEPRINTS"][key]["MODULE"], globals(), locals(), [key], 0)
            app.register_blueprint(eval("bp_mod." + key), url_prefix=app.config["BLUEPRINTS"][key]["URL_PREFIX"])

# Create the tempfolder if not already exist
def configure_temp_folders(app):
	if "TEMPORARY_FOLDER" in app.config:
		if os.path.isdir(app.config['TEMPORARY_FOLDER']) is False:
			os.makedirs(app.config['TEMPORARY_FOLDER'])



# route for logging user in
@app.route("/login", methods =["POST"])
def login():
	# creates dictionary of form data
	auth = request.form

	if not auth or not auth.get("email") or not auth.get("password"):
		# returns 401 if any email or / and password is missing
		return make_response(
			"Could not verify",
			401,
			{"WWW-Authenticate" : 'Basic realm ="Login required !!"'}
		)

	# Normally this is where we would get the user from database,
	# but for this exercise, a dummy User is created with hardcoded
	# id to match the passed in JWT token
	#     user = User.query\
	# 	    .filter_by(email = auth.get("email"))\
	# 	    .first()

	user = User()
	user.public_id = "123456789" # hardcoded just for this exercise

	if not user:
		# returns 401 if user does not exist
		return make_response(
			"Could not verify",
			401,
			{"WWW-Authenticate" : 'Basic realm ="User does not exist !!"'}
		)

	if True:# check_password_hash(user.password, auth.get("password")):
		# generates the JWT Token
		token = jwt.encode({
			"public_id": user.public_id,
			"exp" : datetime.utcnow() + timedelta(minutes = 30)
		}, app.config["SECRET_KEY"])

		return make_response(jsonify({"token" : token.decode("UTF-8")}), 201)

	# returns 403 if password is wrong
	return make_response(
		"Could not verify",
		403,
		{"WWW-Authenticate" : 'Basic realm ="Wrong Password !!"'}
	)

# Bootstrap the app 
configure_blueprints(app)
configure_temp_folders(app)

if __name__ == "__main__":
	# Just for expediency, run Flask in development mode.
    # For production, of course it"s better to use something like UWSGI
	app.run(debug = True, host=app.config["HOST"], port=app.config["PORT"])
