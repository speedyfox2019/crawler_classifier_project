# crawler_classifier_project

## Summary

Here are the summary of the 3 parts of this test/project:
1. Crawler
   - As suggested, I used Selenium, with Chrome Driver (you'll need a test Twitter account user nane, email, and password for this)
   - I also have a separate copy that implements the same with the Twitter API (APIs are usually more robust, and also uses tokens instead of user name and password)
   - To ensure the selenium driver version compatibility with the installed browser, I decided to create a Docker container, with a Dockerfile that installs a specific Chrome browser and Driver version. I've used the selenium driver long enough to know it's finicky about the version compatibility :)
2. ML:
   - I chose to use a simple VGG19 from Keras library as a pre-trained model and use it directtly to classify the images. 
   - Result/accuracy is so-so, for production, we'll need a better solution and maybe train our own model.
3. API:
   - I used Flask to implement the API
   - The APIs are wide-open (no login required), but I included a simple JWT token-based authentication (commented out by default). Username and password are hardcoded just for illustration, normally it will be stored in database and used with some ORM.
   - See Usage section below.   

## Installation/Running

1. Clone this project to a folder, then go into the folder.
2. Edit the "configs/development.py" file and fill out the appropriate *test* Twitter credential. Highly recommended to use a test account, not your real/personal Twitter.
   ```
   Fill out the TW_USER_NAME, TW_EMAIL, and TW_PASSWORD in the development.py
   ```
2. Make sure you have docker and docker-compose installed
3. To start the program (you may need to do sudo):
   ```
   docker-compose -f docker-compose.yml up
   ```
4. Note the IP Address and port that is printed out on the console for calling the APIs.
5. The docker-compose may take approx 10 minutes to finish setting up for the first time.
6. To stop the program:
   ```
   docker-compose -f docker-compose.yml down
   ```

## Usage:

- To invoke the search crawler, on your browser, go to: http://<ip_address>:5001/api/search/<searchkeyword>, for example:
  ```
  http://<ip_address>:5001/api/search/covid
  ```
- To invoke the file uploader API, use something like curl utility, for example:
  ```
  curl -F 'data=@<path_to_your_local_image_file>' http://<ip_address>:5001/api/upload
  ```
- To use the APIs with JWT token, edit the "api/views.py" file, uncomment the "@token_required" annotation
  ```
  curl -X POST -F "email=abc" -F "password=123" http://<ip_address>:5001/login 
  ```
  This will return a token. Pass the token in subsequent API calls, e.g:
  ```
  curl -F 'data=@<path_to_your_local_image_file>' -H "x-access-token: <the_jwt_access_token>" http://<ip_address>:5001/api/upload
  ```
