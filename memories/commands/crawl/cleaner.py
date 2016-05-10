#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re


def comicsify(blob):
    PARENTHESIS = re.compile(' \((.*?)\)', re.UNICODE)
    PREFIX = set([u"l'", u"le", u"la", u"les", u"du", u"des", u"d'", u"un", u"une", u"the", u"a", u"an", "of"]) # case insensitive

    EDITORS = set([u'Editions USA', u'Marvel', u'Télé 7', u'Pocket', u'Tomic', u'Fei', u'SPE', u'Rhodos ',
                u'Le Soir Belgique', u'Stylo Bulle', u'DC ', u'Le Soir', u"Éditions L'héritage",
                u'Elisa ', u'Hachette', u'France Loisirs', u'Éditions mondiales', u'Editions Mondiales', u'DOC', u'AUT',
                u'Nucléa/Soleil', u'France Inter', u'Nathan', u'Casterman', u'Classics library', u'H.S. et Publicitaires',
                u'Bédé Chouette', u'Sagédition', u'Delcourt', u"Vents d'Ouest", u'Panini', u'éditeurs', u'TF1', u'Dupuis',
                u'Clair de Lune', u'Futuropolis', u'Studio', u'Cinebook', u'Les Humanoïdes Associés', u'Collection classique bleue', u'France Sud',
                u'Édition Misty', u'Casterman',  u'Coronet Editions', u'Éditions Grand Sud', u'Le Figaro', u'Ouest France', u'Le Monde', u'Rivages',
                u'Édition Pirate', u'Albin Michel', u'Organic Comix', u'Gallimard', u'West', u'Éditions Samedi'])

    DETAILS = set([u'n°', u'N°', u'best of', u'Best of', u'intégrale', u'Intégrale', 'Artbook', u'série', u'Série', u'part ', u'Part ', u'saison',
                u'bis', u'Almanach', u'album', 'series', 'edition', u'année', u'book', u'Grand format', u'Beau livre', u'N&B', u'Hors-série',
                u'épisode', u'Épisode', u'Volume', u'volume', u'vol.', u'Vol.', 'Livre animé', 'Preview', u'Jeunesse', u'polonais', 'collector',
                u'Collector',
                u'portugais', u'italien', u'anglais', u'num', u'Journal', u'journal', u'Magazine', 'Partie', u'partie', u'novel', u'Novel', u'mensuel',
                u'janvier', u'février', u'mars', u'avril', u'mai', u'juin', u'juillet', u'août', u'septembre', u'octobre', u'novembre', u'décembre',
                u'Janvier', u'Février', u'Mars', u'Avril', u'Mai', u'Juin', u'Juillet', u'Août', u'Septembre', u'Octobre', u'Novembre', u'Décembre',
                ])

    def year(comic):
        name = comic.pop(u'dl')
        comic.update({u'year': int(name.split(u'/')[-1]) if name else None})

    def title(comic):
        def unify(container):
            return [item for index, item in enumerate(container)
                    if item and map(lambda x: x.lower(), container).index(item.lower()) == index]

        def reformat(string):
            parentheses = PARENTHESIS.findall(string)
            string = string.split('(', 1)[0]
            for parenthesis in parentheses:
                last = parenthesis.rsplit(' ', 1)[-1]
                if last.lower() in PREFIX:
                    if ' ' not in parenthesis:
                        parenthesis = parenthesis.capitalize()
                    string = parenthesis + u' ' + string
            return string.strip()

        def clean(*args):
            return u' — '.join(unify(map(reformat, args)))

        title = comic.pop(u'titre')
        series = comic.pop(u'serie')
        num = comic.pop(u'num')
        numa = comic.pop(u'numa')
        t = '' if series.lower().startswith(title.lower()) else title
        s = '' if ((series != title and title.lower().startswith(series.lower())) or series.startswith('(AUT)')) else series

        cleaned = clean(s, t)
        comic.update({u'title': cleaned,
                      u'metadata': dict([(k, v)
                                          for k, v in [(u'title', title),
                                                      (u'series', series),
                                                      (u'num', num),
                                                      (u'numa', numa)]
                                          if v])})

    year(blob)
    title(blob)
    return blob
