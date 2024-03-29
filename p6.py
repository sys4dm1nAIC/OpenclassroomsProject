#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Importation des modules python 
import getpass
from datetime import datetime
import logging
import os
import sys
import time
import subprocess

# Permet de définir les couleurs
RED = '\033[31m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
END = '\033[0m'

'''
Vous pouvez changer ici les informations de connexions à la bdd & au panel WP
'''
# utilisateur db wordpress
wordpress_db_user = "p6_user"
# password db wordpress
wordpress_db_password = getpass.getpass(prompt='Enter password for the wordpress DB : ')
# Email et password panel wp-admin
wp_admin_pass = getpass.getpass(prompt='Enter password for the admin user : ')
wp_admin_email = "test@p6.com"

# Liste des extensions PHP nécessaire à WordPress & Apache
ext_utils = ["libapache2-mod-php", "php-mysql", "php-curl", "php-gd", "php-xml", "php-mbstring",
"php-xmlrpc", "php-zip", "php-soap", "php-intl", "php-common"]

# Processus de création de la DB
routine_db_creation = ["CREATE DATABASE wordpress_db DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;",
"GRANT ALL ON wordpress_db.* TO '{}'@'localhost' IDENTIFIED BY '{}';".format(wordpress_db_user, wordpress_db_password),
"FLUSH PRIVILEGES;"]

# Téléchargement de WP-CLI
routine_wp_cli_creation = ["curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar",
"chmod +x wp-cli.phar",
"sudo mv wp-cli.phar /usr/local/bin/wp"]

# Installation & Configuration de WordPress à l'aide de WP-CLI
routine_wp_stuff_creation = [
"cd /var/www/html/ && /usr/local/bin/wp core download --locale=fr_FR --allow-root",
"/usr/local/bin/wp core config --dbname=wordpress_db --dbuser={} --dbpass={} --skip-check --path=/var/www/html/ --allow-root".format(wordpress_db_user, wordpress_db_password),
"/usr/local/bin/wp db create --path=/var/www/html --allow-root",
"/usr/local/bin/wp core install --url=localhost --title=TEST_P6 --admin_user=admin_p6 --admin_password={} --admin_email={} --path=/var/www/html/ --allow-root".format(wp_admin_pass, wp_admin_email)]

# Récupération de la date
now_uptime = datetime.now()
# Conversion de la date dans le format Jour:Mois:Année:Heure:Minutes:Secondes
date_uptime = now_uptime.strftime("%d_%m_%Y_%H:%M:%S")

# Calcul du temps d'exécution 
def end_task():
    print("[Execution time : {0} seconds]".format(round(time.time() - start_time)))
    sys.exit()

# Vérification des droits
def verify_root():
    if not os.geteuid() == 0:
        sys.exit("\nSeul root peut lancer ce script !\n")

# Installation d'un package linux
def pass_install_command(name_package):
    subprocess.call(["apt", "install", name_package, "-y"], stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT, shell=False)
    print(YELLOW + "[*] {} successfully installed [*]".format(name_package) + END)

# Installation de plusieurs packages sans retour
def pass_install_command_ext(name_package):
    subprocess.call(["apt", "install", name_package, "-y"], stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT, shell=False)

# Mis à jour des packages de la machine
def apt_update():
    # stdout=subprocess.DEVNULL
    subprocess.call(["apt", "update", "-y"], shell=False)
    subprocess.call(["clear"], shell=False)
    print(RED + "[*] Linux packages updated [*]" + END)

# Activer MySQLi & retsart le service apache2
def php_mysqli():
    # stdout=subprocess.DEVNULL
    # Active mysqli avec php
    subprocess.call(["phpenmod", "mysqli"], shell=False)
    # Relance le service apache2
    subprocess.call(["systemctl", "restart", "apache2"], shell=False)
    print(YELLOW + "[*] MySQLi successfully installed [*]" + END)

# Installation & Configuration de la stack LAMP
def install_lamp_stack():
    # Installe Apache2
    pass_install_command("apache2")
    # Configuration des droits pour l'user du serveur web
    subprocess.call(["chown", "-R", "www-data:www-data", "/var/www/"], stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT, shell=False)
    # MySQL Server
    pass_install_command("mysql-server")
    # PHP
    pass_install_command("php")
    # PHP Extensions for WordPress & Apache
    for i in ext_utils:
        pass_install_command_ext(i)
    print(RED + "[*] PHP extensions & Apache successfully installed [*]" + END)

# Fonction de configuration de la DB
def config_database():
    # Boucle pour exécuter chaque commande présentes dans routine_db_creation
    for i in routine_db_creation:
        subprocess.call(["mysql", "-u", "root", "-e", i], stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT, shell=False)
    
    print(RED + "[*] Wordpress Database successfully configured [*]" + END)

# Fonction de configuration de WP-CLI
def config_wp_cli():
    # Boucle pour exécuter chaque commande présentes dans routine_wp_cli
    for i in routine_wp_cli_creation:
        subprocess.call([i], shell=True)

    print(RED + "[*] WP CLI successfully installed [*]" + END)

# Fonction de configuration de WordPress
def install_wp():
    # Boucle pour exécuter chaque commande présentes dans routine_wp_stuff
    for i in routine_wp_stuff_creation:
        subprocess.call([i], shell=True)
    # Remove index.html
    subprocess.call(["rm", "/var/www/html/index.html"], stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT, shell=False)
    print(YELLOW + "[*] Wordpress successfully installed [*]\n You can check : http://localhost/" + END)

# Fonction globale qui exécute toutes les autres
def main():
    # Appelle chaque fonction une par une
    start_time = time.time()
    verify_root()
    apt_update()
    install_lamp_stack()
    config_database()
    config_wp_cli()
    install_wp()
    php_mysqli()
    # Affiche le temps d'exécution total du programme
    print("[Execution time : {0} seconds]".format(round(time.time() - start_time)))

# Permet de lancer la fonction main du programme
if __name__ == "__main__":
    main()