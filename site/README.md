# Interface de consultation

Le dossier `site/` contient l'interface web statique qui rend le registre
canonique consultable publiquement sur GitHub Pages. C'est strictement une
vue **en lecture seule** des données du registre — toutes les corrections
remontent par PR sur les YAML sources.

## Rôle

- Exposer les 1669+ variantes du registre dans une vue tabulaire
  filtrable et recherchable.
- Offrir une vue **éclatée** (une ligne par variante) et une vue
  **consolidée** (les sous-variantes appartenant à un même
  `variant_group` sont regroupées sous une ligne unique, avec toggle
  d'expansion).
- Donner un accès direct aux liens externes (`joydiv.org`, Discogs) et
  un panneau de détail par variante.
- Ne **jamais** afficher de champ privé : tout ce qui touche à la
  possession (`ownership`, prix payé, photos perso) vit dans le repo
  séparé `joy-division-collection` et n'a aucune représentation ici.

## Comment c'est généré

1. `scripts/build_site_data.py` parcourt `data/variants/*.yml`, applique
   le filtre de visibilité publique (cf. `public_view()` dans le
   script), et produit `site/data/all-variants.json`.
2. `.github/workflows/deploy-pages.yml` exécute ce script sur chaque
   push vers `main`, puis publie le contenu de `site/` (HTML + CSS + JS
   + JSON) comme artefact GitHub Pages, déployé sur l'URL Pages du repo.
3. Côté navigateur, `site/app.js` charge `data/all-variants.json` au
   démarrage et expose les filtres + tri + sélection via un store
   Alpine.js.

Le JSON consolidé **n'est pas commit** (cf. `.gitignore`) : il se
régénère à chaque build, ce qui évite que le repo grossisse à chaque
modification de YAML, et garantit que ce qui est servi correspond
toujours aux YAML actuellement sur `main`.

## Exécution locale (développement)

Pré-requis : Python 3 et PyYAML (`pip install pyyaml`).

```bash
# 1. Construire le JSON consolidé
python scripts/build_site_data.py

# 2. Lancer un serveur statique pour servir site/
#    (file:// ne permet pas le fetch des assets locaux)
python -m http.server --directory site 8000

# 3. Ouvrir http://localhost:8000 dans un navigateur
```

Modifications côté frontend :

- `site/index.html` — structure et Alpine bindings.
- `site/style.css` — palette restreinte à 3 couleurs d'accent, responsive
  basique (table → cards sous 720 px).
- `site/app.js` — store Alpine `registry` (chargement, filtres, tri,
  mode de vue, sélection).

Aucune chaîne de build frontend : pas de bundler, pas de minification,
pas de hash de cache. Le code source est ce qui est servi.

## Comment contribuer

- **Corriger une variante** : éditer le YAML correspondant dans
  `data/variants/`, ouvrir une PR. Le workflow régénère automatiquement
  le site après le merge.
- **Améliorer l'interface** : éditer `site/index.html`,
  `site/style.css` ou `site/app.js`. La PR ne nécessite pas de
  régénérer `data/all-variants.json` localement (le workflow le fait au
  déploiement) — mais tester localement avec un serveur statique reste
  recommandé.

Ne jamais éditer `site/data/all-variants.json` à la main : c'est un
fichier généré, toute modification serait écrasée au prochain build.
