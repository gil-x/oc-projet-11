#Pur Beurre
Web application running on **Django** (Python web Framework), created for the project #8 of the course "Développeur d'application Python" of french school Openclassroom.

##Features
Following the grade system based on Food Standard Agency with five letters A-B-C-D-E, 'A' being the most 'healthy' product, this application provide a simple interface to look for better food. The application uses data from [openfoodfacts.org](https://fr.openfoodfacts.org/).

##Tech

###Procedure
1. Type the name of a product in webform
2. The application looks in local database if there are some food with better
3. If there is product matching, returns the results
4. If not, launch a request on OFF, and then return the results
5. User can register the results as favorites if has an account, if not...
6. User can create an account

###Specs
* The local database do not contains all data from OFF
* The application provide unit tests, according to Django default testing system
* The authentification is limited: you can't change your password, yet

##Licence
All code and the incredible graphic work is free. You can redistribute it and/or modify it under the terms of the *Do What The Fuck You Want To Public License*, Version 2, as published by **Sam Hocevar**. See [wtfpl](http://www.wtfpl.net/) for more details.