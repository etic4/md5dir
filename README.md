# md5dir - Calculer la somme md5 d'un répertoire

Ce module comprend un utilitaire en ligne de commande qui permet de calculer la somme md5 du contenu d'un répertoire (commande `md5`), ainsi que de comparer deux répertoires (commande `compare`).

La commande `md5` peut retourner soit la somme md5 de l'ensemble des fichiers inclus dans le dossier, soit un fichier texte comprenant les sommes de chacun des fichiers inclus dans le dossier.

La commande `compare` compare deux répertoires.

Le module peut être installé avec pip:

    python3 -m pip install md5dir

Le module est compatible avec python 3.5+

## Usage

Pour calculer la somme md5 d'un répertoire et l'écrire sur la sortie standard:

    md5dir md5 chemin/du/répertoire -u

Pour calculer les sommes md5 du contenu d'un répertoire et l'écrire dans le fichier 'outfile.txt'.

    md5dir md5 chemin/du/répertoire -o outfile.txt

Pour comparer les sommes md5 du contenu de deux répertoires:

    md5dir compare chemin/du/répertoire autre/chemin


L'aide et les options:

    md5dir --help

L'aide et les options d'une commande:

    md5dir md5 --help


Ce code est sous licence WTFPL.
