
1. Install related packages

    $sudo apt-get install python2.7
    $sudo apt-get install python-pip
    $sudo pip install --upgrade pip
    $sudo pip install pymongo
    $sudo apt-get install default-jre
    $sudo pip install django
    $sudo pip install pysolr

    1.1 Install mongodb (database)

        https://docs.mongodb.com/manual/administration/install-community/

    1.2 Install solr (search engine)

        Download solr from http://apache.claz.org/lucene/solr/6.6.1/
        Tutorial of solr: http://lucene.apache.org/solr/quickstart.html

        Start solr

            $<solr folder>/bin/solr start -e cloud -noprompt


2. Prepare settings.py

    $cp settings.sample.py settings.py


3. Prepare datasets

    * For implementation, you could skip this step

    2.1 Prepare yelp datasets and update settings.py

        Donwload yelp datasets from https://www.yelp.com/dataset/download
        Update settings.py
        
            BUSINESS_FILE, USER_FILE, REVIEW_FILE, TIP_FILE, CHECKIN_FILE

    2.1 Prepare vector files and update settings.py

        Ask for vector files
        Update settings.py

            SEQ2ID_FILE, SEQ2VEC_FILE

    2.3 Prepare files for search engine

        Update indexing file name in setting.py

            INDEXING_FILE

        $python tools/prepare_dataset_for_indexing.py


3. Build up the database

    $python db/importer.py


4. Build up the search engine

    $<solr folder>/bin/post -c gettingstarted <INDEXING_FILE in settings.py>


5. Start django server

    5.1 Update your ip to ALLOWED_HOSTS in rec/settings.py

    $python manage.py runserver 0.0.0.0:8001
