# M8
Dispositif M8 - Poubelles de l'expo MAISON du Vaisseau



# Compte-rendus

## 2025_11_21 - Réinstallation sur une nouvelle raspberyy

L'installation s'est bien passée jusqu'à l'utilisation de requirements.txt :

- lgpio refuse de s'installer. En théorie, je ne devrais pas en avoir besoin, j'ai donc enlevé la ligne *lgpio==0.2.2.0* du fichier pour poursuivre l'installation.

- Je suis maintenant confronté au problème habituel : rpi_ws281x ne peut être lancé que en sudo, mais alsamixer refuse l'accès en sudo. Sur l'ancienne rpi, cela n'avais l'air de ne pas poser de problème, je en sais pas comment je me suis débrouillé à l'époque. 
    - Ha si j'ai trouvé dans le README de Templates ! Il faut créer un fichier asound.conf dans /etc/ :
    - cd /etc/
    - sudo nano asound.conf
    - Ajouter deux lignes : "defaults.pcm.card 2" et "defaults.ctl.card 2"

- Maintenant, j'ai effectivement des problèmes avec les GPIO.
    - Problèmes réglés, voir la mise à jour dans les isntructions d'installation de pgiozero dans Templates

