

sudo service mongod start
bin/solr start -e cloud -noprompt

1. Prepare yelp datasets and vector files


2. Prepare settings.py

    $vim settings.py


3. Build up the db

    $python db/importer.py
