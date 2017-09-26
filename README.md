
1. Install related packages

    $sudo apt-get install python2.7
    $sudo apt-get install python-pip
    $sudo pip install --upgrade pip
    $sudo pip install pymongo
    $sudo apt-get install default-jre
    $sudo pip install django
    $sudo pip install pysolr
    $sudo pip install plotly

    $sudo apt-get install neo4j
    $sudo mkdir /var/run/neo4j
    $sudo rm /var/lib/neo4j/data/dbms/auth
    $sudo neo4j-admin set-initial-password sheep1234
    $sudo vim /etc/neo4j/neo4j.conf
    un-comment dbms.connectors.default_listen_address=0.0.0.0

    $sudo neo4j start / stop / status / restart

    $sudo pip install py2neo


2. Prepare settings.py

    $cp settings.sample.py settings.py


3. Setup PYTHONPATH

    In the repository folder
    For linux
    $export PYTHONPATH=`pwd`

    For window
    $SET PYTHONPATH='<repository folder>'


4. Prepare datasets

    * For implementation, you could skip this step

    4.1 Prepare yelp datasets and update settings.py

        Donwload yelp datasets from https://www.yelp.com/dataset/download
        Update settings.py
        
            BUSINESS_FILE, USER_FILE, REVIEW_FILE, TIP_FILE, CHECKIN_FILE

    4.2 Prepare vector files and update settings.py

        Ask the administrator for vector files
        Update settings.py

            SEQ2ID_FILE, SEQ2VEC_FILE

    4.3 Prepare files for search engine

        Update indexing file name in setting.py

            INDEXING_FILE

        $python tools/prepare_dataset_for_indexing.py



5. Build up the database

    * For implementation, you could skip this step and
      ask the administrator for the settings of database

    5.1 Install mongodb (database)

        https://docs.mongodb.com/manual/administration/install-community/

    5.2 Modify conf of mongodb and start mongodb

        $sudo vim /etc/mongodb.conf

        $sudo service mongod start
        or
        $sudo mongod --auth --dbpath /var/lib/mongodb

    5.3 Import data

        $python db/importer.py


6. Build up the search engine

    * For implementation, you could skip this step and
      ask the administrator for the settings of solr and modify settings.py

        SOLR_HOST
        SOLR_PORT
        SOLR_CORE

    6.1 Install solr (search engine)

        Download solr from http://apache.claz.org/lucene/solr/6.6.1/
        Tutorial of solr: http://lucene.apache.org/solr/quickstart.html

    6.2 Start solr

        $<solr folder>/bin/solr start -h <host> -p <post>

    6.3 Built solr search engine

        $<solr folder>/bin/solr create -c <core_name>
        $<solr folder>/bin/post -h <host> -p <post> -c <core_name> <INDEXING_FILE in settings.py>

    6.4 Delete all data from solr search engine

        $curl "http://<host>:<port>/solr/<core>/update?stream.body=<delete><query>*:*</query></delete>&commit=true"


7. Start django server

    7.1 Update your ip to ALLOWED_HOSTS in rec/settings.py

    7.2 Start django local server

        $python manage.py runserver 0.0.0.0:8001
