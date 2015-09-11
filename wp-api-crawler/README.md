# Méthodologie

La base de données est constituée des documents de l'ARC5 et de la base de données récupérées via le site des ARCs. Afin de permettre un meilleur traitement des informations, une phase importante de nettoyage et de formatage des données étaient nécessaires. 

Pour organiser la lecture sous forme de réseau, nous avons décidé de nous appuyer sur les 2 composants traditionnels des réseaux : les *nodes* et les *edges*. Néanmoins, une des difficultés reste la composition des réseaux d'après les éléments des données. Doit-t-on considérer une thèse comme un noeud ou comme un lien ? Nous avons ainsi choisi de définir un ensemble d'entités que nous pouvons considérer soit comme lien, soit comme noeud. 

Les thèses par exemple  permettent de regrouper : labos, doctorants, directeurs, etc. par des liens uniques. Elles peuvent également considérées uniquement comme des liens (dématérialisées) ou comme des entités à part entière. Cet encart méthodologique nous amène ici à nous questionner sur la représentation des liens, et plus notamment sur leurs constitutions. Si nous voulons voir comment un projet au long cours à générer davantage de relations entre les participants il nous faut alors l'oublier.



