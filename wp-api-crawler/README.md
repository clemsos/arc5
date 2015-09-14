# Méthodologie

La base de données est constituée des documents de l'ARC5 et de la base de données récupérées via le site des ARCs. Afin de permettre un meilleur traitement des informations, une phase importante de nettoyage et de formatage des données étaient nécessaires. 

Pour organiser la lecture sous forme de réseau, nous avons décidé de nous appuyer sur les 2 composants traditionnels des réseaux : les *nodes* et les *edges*. Néanmoins, une des difficultés reste la composition des réseaux d'après les éléments des données. Doit-t-on considérer une thèse comme un noeud ou comme un lien ? Nous avons ainsi choisi de définir un ensemble d'entités que nous pouvons considérer soit comme lien, soit comme noeud. 

Les thèses par exemple  permettent de regrouper : labos, doctorants, directeurs, etc. par des liens uniques. Elles peuvent également considérées uniquement comme des liens (dématérialisées) ou comme des entités à part entière. Cet encart méthodologique nous amène ici à nous questionner sur la représentation des liens, et plus notamment sur leurs constitutions. Si nous voulons voir comment un projet au long cours à générer davantage de relations entre les participants il nous faut alors l'oublier.



## Data ARC5:

    # python parse_projects.py
    52 projets
    24 etablissements
    10 ecole-doctorales
    23 theses
    104 personnes
    1 postdocs

    # python parse_partenaires.py 
    total : 141 partenaires

    # python parse_subventions.py 

    27 subventions in 2012_projets.csv
    54 subventions in 2013_projets.csv
    Total : 54 subventions.

## Data WP


    # http://arcs.test/wp-json/posts?type=bdd_projet&filter%5Bposts_per_page%5D=1000
    3 'results in ' 'bdd_projet' with 'arc5'

    # http://arcs.test/wp-json/posts?type=bdd_these&filter%5Bposts_per_page%5D=1000
    36/131 'results in ' 'bdd_these' with 'arc5'

## Formating diff : 

* projet.json.name: "MARA. Monnaie antique en Rh\u00f4ne-Alpes : du document mon\u00e9taire \u00e0 son exploitation "
* subvention.projet: "MARA. Monnaie antique en Rhone-Alpes : du document mon\u00e9taire \u00e0 son exploitation"
* partenaires.postdoc : "Monnaie imp\u00e9riale et corpus numismatique en Rh\u00f4ne-Alpes - MARA (postdoc) "
* wp.title : "Monnaie antique en Rhône-Alpes : du document monétaire à son exploitation"
