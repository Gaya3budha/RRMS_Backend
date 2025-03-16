RRMS Backend

After Cloning the Project to the local folder, navigate into the project directory

For Linux run folllowing commands:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

For Windows run following commands:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


To Set up the db run the following commands
python manage.py migrate

To create a super User, run the below command
python manage.py createsuperuser

To run the appilcation, run the below command
python manage.py runserver
