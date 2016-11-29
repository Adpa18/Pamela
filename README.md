## Requirements

Add backports

```bash
# echo 'deb http://ftp.debian.org/debian jessie-backports main' > /etc/apt/sources.list
# apt update
```

```bash
# apt install python3 python3-dev python3-pip libcryptsetup-dev python3-simplejson python3-systemd python3-guestfs python3-psutil libsqlite3-dev libsqlcipher-dev
# pip3 install pysqlcipher3
```

```bash
cd /lib/x86_64-linux-gnu/security/
git clone git@git.epitech.eu:/dhiver_b/Pamela luksypam
```

Install `pycryptsetup` python module
```bash
cd pycryptsetup
# pip3 install -e .
```

Add at the end of /etc/pam.d/common-auth
```text
auth required pam_exec.so expose_authtok /lib/x86_64-linux-gnu/security/luksypam/luksypam/luksypam_auth.py
```

And at the end of /etc/pam.d/common-session
```text
session required pam_exec.so /lib/x86_64-linux-gnu/security/luksypam/luksypam/luksypam_close_session.py
```

## Bonus

* Création du conteneur + fichier de conf à la volée.
* Plug module PAM à la session SSH.
* Utilisation de systemd pour remonter les infos. avec mode verbeux ou non
* Il y a un changement du mot de passe du conteneur indépendant du pass unix au travers d'un CLI
* Multi conteneurs.
* Changement du point de montage + nom du volume.
* Python3 bitch
* Build module pycryptsetup
* Modification du module pycryptsetup (algo de hachage + True random)
* Gestion de profils (weak or not?)
* Personnalisation possible au travers de constantes
* Génération d'un conteneur vide rempli aléatoirement
* Effacement sécurisé des conteneurs
* Base de données pour stocker les mots de passes voulus
* Spécifier la taille d'un nouveau conteneur
* Gestion sécurité avancé (le .. dans les paths)
* Validateur de configuration
* Possibilité de désactiver des conteneurs
* Recode de pam_exec.so
