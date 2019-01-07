#!/usr/bin/env python
# -*- coding: utf-8 -*-

# compatible python 3.5+

import os
import hashlib
from difflib import unified_diff
from typing import IO, Optional, Generator, Tuple, List, Any, AnyStr

import click

__all__ = ["HashList", "Directory", "cli"]

APPNAME = "md5dir"


class HashList:
    """Représente la liste des sommes md5 d'un répertoire
    """
    def __init__(self, dirpath: Optional[str]=None) -> None:
        self.hashlist: List[Tuple[str, str]] = list()
        self.dirpath = dirpath

    def add(self, doublet: Tuple[str, str]) -> None:
        """Ajoute un chemin relatif et le md5 du fichier correspondant
        """
        self.hashlist.append(doublet)


    def read_file(self, filepath: str) -> None:
        """Lit un fichier et le parse.
        """
        hashs = list()

        abs_filepath = os.path.abspath(filepath)

        if not os.path.isfile(abs_filepath):
            raise Exception("N'est pas un fichier: {}".format(abs_filepath))

        with open(filepath) as f:
            content = [line for line in f.readlines() if not line.startswith("#")]

        if not content:
            raise Exception("HashList.read(): Le fichier {filepath} est vide".format(filepath=filepath))

        for line in content:
            splitted = line.split()
            # Check minimal qu'on a bien une liste de chemins+hash
            assert len(splitted) == 2

            hashs.append((splitted[0], splitted[1]))

        self.hashlist = hashs


    def write_file(self, destfile: str) -> None:
        """Ècrit la liste de noms de fichier et md5 associés dans un fichier
        """
        abs_destfile = os.path.abspath(destfile)

        with open(destfile, "w") as f:
            f.write("# Sommes md5 de {dirpath}\n".format(dirpath=self.dirpath))
            for line in self.lines():
                f.write(line + "\n")

        print("\nSommes md5 écrites dans {abs_destfile}\n".format(abs_destfile=abs_destfile))


    def lines(self) -> List[str]:
        """Retourne les lignes chemin+espaces+md5 justifiées. Pratique pour générer une diff et
         utilisé pour écrire dans un fichier.
        """
        _lines = list()

        justified = self._justify(self.hashlist)

        for relfilepath, spaces, md5 in justified:
            _lines.append("{relfilepath}{spaces}{md5}".format(relfilepath=relfilepath, spaces=spaces, md5=md5))

        return _lines


    def compare(self, other: Any) -> str:
        """Compare cette liste avec une autre
        """
        if self == other:
            return "Les sommes md5 sont identiques."
        else:
            txt = "Les sommes md5 sont différentes!"
            txt += self.diff(other)

            return txt


    def diff(self, other: Any) -> str:
        """Retourn la diff de cette liste avec une autre
        """
        diff_text = "\n".join([line for line in unified_diff(self.lines(), other.lines(), fromfile=self.dirpath, tofile=other.dirpath, n=0)])

        return diff_text


    def __eq__(self, other: Any) -> bool:
        self.hashlist.sort()
        other.hashlist.sort()

        return self.hashlist == other.hashlist


    def _justify(self, md5_list: List[Tuple[str, str]], min_dist: int=5) -> List[Tuple[str, str, str]]:
        """Retourne une liste comprenant des expaces permettant la justification
        """
        justified = list()
        longest = 0

        for filepath, md5 in md5_list:
            if len(filepath) > longest:
                longest = len(filepath)

        for filepath, md5 in md5_list:
            spaces = " " * (longest - len(filepath))
            spaces += " " * min_dist
            justified.append((filepath, spaces, md5))

        return justified



class Directory:
    def __init__(self, dirpath: str) -> None:
        self.dirpath = os.path.abspath(dirpath)


    def md5(self, include_hidden: bool=False, verbose: bool=False) -> str:
        """Retourne la somme md5 d'un répertoire.
        """
        md5 = hashlib.md5()

        for filepath, relfilepath in self._get_filepaths(include_hidden):
            if verbose:
                print("Ajout de la somme md5 de {relfilepath}".format(relfilepath=relfilepath))

            with open(filepath, "rb") as fb:
                md5.update(fb.read())

        return md5.hexdigest()


    def md5_list(self, include_hidden: bool=False, verbose: bool=False) -> HashList:
        """Retourne la liste des éléments d'un répertoire avec les sommes md5 associées.
        """
        hashlist = HashList(self.dirpath)

        for filepath, relfilepath in self._get_filepaths(include_hidden):
            if verbose:
                print("Calcul de la somme md5 de {relfilepath}".format(relfilepath=relfilepath))
            with open(filepath, "rb") as fb:
                md5 = hashlib.md5(fb.read()).hexdigest()

            hashlist.add((relfilepath, md5))

        return hashlist


    def _get_filepaths(self, include_hidden: bool) -> Generator[Tuple[str, str], None, None]:
        for d_path, dirnames, filenames in os.walk(self.dirpath):
            dirnames.sort() # pour un ordre prévisibles et comparables
            filenames.sort()
            for filename in filenames:
                if filename.startswith("."): # inclus ou pas les fichiers cachés (unix seulement?)
                    if not include_hidden:
                        continue
                filepath = os.path.join(d_path, filename)
                relfilepath = os.path.relpath(filepath, self.dirpath)

                yield filepath, relfilepath


# ################################
# Interface en ligne de commande #
# ################################

@click.group()
@click.help_option("--help", help="Affiche ce message et quitte.", is_flag=True, is_eager=True)
def cli() -> None:
    """Ce module comprend un utilitaire en ligne de commande qui permet de calculer la somme md5
    du contenu d'un répertoire (commande 'md5'), ainsi que de comparer les sommes md5 de deux répertoires (commande 'compare').
    La commande 'md5' peut retourner soit la somme md5 de l'ensemble des fichiers inclus dans le
    dossier, soit un fichier texte comprenant les sommes de chacun des fichiers inclus dans le
    dossier.
    """
    pass


@cli.command(short_help="Calcule la somme md5 d'un répertoire")
@click.argument("dirpath")
@click.option("--unique", "-u", is_flag=True, help="""Retourne la somme md5 de l'ensemble des fichiers, plutôt que de retourner une somme md5 pour chaque fichier contenu dans le dossier et les sous-dossiers.""")
@click.option("--outfile", "-o", help="Écrit le résultat dans un fichier.")
@click.option("--include_hidden", "-h", is_flag=True, help="Inclus les fichiers cachés")
@click.help_option("--help", help="Affiche ce message et quitte.", is_flag=True, is_eager=True)
def md5(dirpath: str, unique: bool, outfile: Optional[str]=None, include_hidden: bool=False) -> None:
    """Retourne la somme md5 de chacun des fichiers et sous-dossiers inclus dans le dossier ´dirpath´. Avec ´--unique´ ou ´-u´, retourne une seule somme md5 pour tout le contenu d'un répertoire.
    """

    if not os.path.isdir(dirpath):
        print("N'est pas un répertoire: {dirpath}\n".format(dirpath=dirpath))
        return

    if not unique:
        hashlist = Directory(dirpath).md5_list(include_hidden)
        if outfile:
            hashlist.write_file(outfile)
        else:
            print("Sommes md5 de {dirpath}:\n".format(dirpath=dirpath))
            for line in hashlist.lines():
                print(line)

            print()

    else:
        md5_digest = Directory(dirpath).md5(include_hidden)
        if outfile:
            with open(outfile, "w") as f:
                f.write("{}\n".format(md5_digest))
        else:
            print("Somme md5 du contenu de {}:\n".format(dirpath))
            print(md5_digest)
            print()


@cli.command(short_help="Comparer les sommes md5 de deux répertoires.")
@click.argument("dirpath1")
@click.argument("dirpath2")
@click.option("--unique", "-u", is_flag=True, help="""Compare la somme md5 de l'ensemble des fichiers, plutôt que de comparer les sommes md5 de chaque fichier contenu dans le dossier et les sous-dossiers.""")
@click.option("--outfile", "-o", help="Écrit le résultat dans un fichier.")
@click.help_option("--help", help="Affiche ce message et quitte.", is_flag=True, is_eager=True)
def compare(dirpath1: str, dirpath2: str, unique: bool=False, outfile: str=None) -> None:
    """Compare les sommes md5 de chacun des fichiers et sous-dossiers de deux répertoires. Avec ´--unique´ ou ´-u´, ne compare que la somme md5 unique de chacun des répertoire comparé.
    """
    for pth in [dirpath1, dirpath2]:
        if not os.path.isdir(pth):
            print("N'est pas un répertoire: {}".format(pth))
            return

    first = Directory(dirpath1).md5_list()
    second = Directory(dirpath2).md5_list()

    comp = first.compare(second)

    if outfile:
        with open(outfile, "w") as f:
            f.write(comp)
    else:
        print(comp)
        print()


if __name__ == "__main__":
    cli()
