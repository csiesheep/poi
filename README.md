
1. Start mongodb and solr

    $sudo service mongod start
    $bin/solr start -e cloud -noprompt


2. Prepare yelp datasets and vector files


3. Prepare settings.py

    $vim settings.py


4. Build up the db

    $python db/importer.py


5. Start django server

    $python manage.py runserver 0.0.0.0:8001
