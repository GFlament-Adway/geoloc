# READ ME Geoloc

## Requirement 

### Environnement : 
* Python 3

###  Packages : 
* Usuel : json, time, warnings, ...
* Selenium

### Installation : 
* Pour les packages :
```
pip install -r requirements.txt
```

* Pour sélénium, installer le webdriver firefox comme expliquer ici : https://www.selenium.dev/documentation/fr/webdriver/driver_requirements/


### Organisation du projet :
* Dans le dossier scrap se trouve la fonction principale.
* Dans le dossier utils se trouve l'ensemble des fonctions qui permettent d'écrire dans la base de données, de générer les requêtes et les fonctions utiles au scraping. 
En particulier celles qui permettent d'accepter les cookies, qui discriminent si un point appartient à l'entreprise ...
* Dans le dossier settings se trouve l'ensemble des fichiers pour ajouter des options.