# Evaluation-Politiques-Publiques-Culturelles

Avant de commencer, installer pandas, cartiflette, matplotlib et mapclassify s'ils ne sont pas déjà installés.

Ce projet vise à évaluer l'efficacité réelle du Pass Culture en croisant plusieurs bases de données publiques : équipements culturels, démographie, revenus et niveau de diplôme, à l'échelle de la commune (code INSEE).

Contenu du dépôt :
- data.ipynb : notebook de contitution de la base de données finale (import, nettoyage pivot, jointure des sources, statistiques descriptives) ;
- functions.py - fonctions utilitaires utilisées dans le notebook (importdata, infosbase, verifcom, carte_com, etc), à fournir séparément.

Sources de données utilisées

mettre tableau avec les sources des données utilisées

Démarche :
1. Import et nettoyage de chaque source, sélection des variables pertinentes ;
2. Pivot de chaque base pour obtenir une ligne par commune (code_insee) ;
3. Vérification de l'unicité des communes avec verifcom ;
4. Jointure des quatre bases sur code_insee pour produire la table finale df_final ;
5. Statistiques descriptives et visualisation (cartographie communale des équipements cultures avec carte_com et carte_com_cat).

Base finale : df_final
Une ligne par commune (code_insee) avec notamment :
- Identification : code_insee, libelle_geographique, departement, region ;
- Equipements culturels (nombre par commune) : nb_biblio, nb_ctr_cult, nb_ctr_art, nb_ctr_crea_art, nb_ctr_crea_mus, nb_cine, nb_conserv, nb_esp_prot, nb_libr, nb_lieu_archeo, nb_lieu_mem, nb_monum, nb_musee, nb_opera, nb_papet, nb_parc_jard, nb_scene, nb_serv_arch, nb_theatre, nb_etab_ens_sup, nb_ecrans_total, nb_salles_theatre_total, nb_total_etablissements ;
- Démographie : nb_jeunes (15-19 ans), pop_total ;
- Revenus : rev_median, pauvrete ;
- Diplômes (en part de la population) : aucun_diplome, inf_bac, dipl_sup, sup_master ;

Le détail complet des variables (type, unité, description) est disponible dans le notebook, section Variables de la base df_final.
