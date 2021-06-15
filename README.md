# Google Review Manager
Please see ReviewManager_v2 for a functional, up-to-date rendition of this app.





A django web app for requesting google reviews from clients via text and email, and a flask API updated with the aid of a web scraper to update client review status. Such automation has increased google review counts for an ABQ doctor's office by 250% in 4 months.


## Flask server
### --- to run locally, in server/api:
source .venv/bin/activate
export FLASK_APP=application.py
export FLASK_ENV=development
flask run

## Django app 
views.py - modify filepaths
image.py, requestAgain.py - edit user info for text/email, and directly modify messages if desired

### --- to run locally, in app/buttonpython:
python manage.py runserver 127.0.0.1:8002

