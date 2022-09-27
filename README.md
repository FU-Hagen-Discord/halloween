# Discord Halloween Adventure

## Setup

### Setup des Discord Servers
1. Um den Bot nutzen zu können benötigst du zunächst einen Discord-Server. Klicke dazu in Discord in der Serverliste auf folgenden Button:\
![](https://nextcloud.dnns01.dev/index.php/s/JAaA2xQ7LGLn7yC/download/add_server.png)\
Es erscheint daraufhin ein Dialog über den ein neuer Discord Server erstellt werden kann.
2. Erstelle eine Kategorie auf dem Server über einen Rechtsklick in der Channelliste links.
3. Erstelle in der neu erstellten Kategorie einen Channel über das Plussymbol rechts vom Kategorienamen.
4. Gehe in die User Settings über das Zahnrad unten links \
![](https://nextcloud.dnns01.dev/index.php/s/qi3RxD7tPXY8dzN/download/user_settings.png)
5. In den User Settings unter "Erweitert" den Developer Mode einschalten und dann die User Settings wieder verlassen.

### Erstellen des Bot Accounts
1. Geh auf https://discord.dev und logge dich dort mit deinem Discord Account ein. 
2. Klicke anschließend links oben auf "Applications" und danach rechts oben auf "New Application"
3. Im nächsten Schritt kannst du deinem Bot einen tollen Namen geben. Sei kreativ!
4. Danach wähle auf der linken Seite "Bot" aus und klicke rechts auf den Button "Add Bot" und bestätige mit "Yes, do it!"
5. Schalte alle Privileged Intents ein und bestätige mit einem Klick auf "Save Changes" \
![](https://nextcloud.dnns01.dev/index.php/s/ioGB82WLpypy42Y/download/bot_intents.png)
6. Klicke auf "Reset Token" und bestätige mit "Yes, do it!" und du bekommst ein Token angezeigt. Dieses musst du dir für später merken. Aber ACHTUNG!!! Niemand außer dir darf dein Token kennen! \
![](https://nextcloud.dnns01.dev/index.php/s/wfdJf8ALAJTm4dg/download/token.png)
7. Wechlse auf der linken Seite zu "OAuth2" und dann darunter auf "URL Generator". Wähle dort die Scopes und Bot Permissions aus, wie du sie im folgenden Screenshot siehst und kopiere die generierte URL unten.\
![](https://nextcloud.dnns01.dev/index.php/s/sdcqP8NeQYHPqPC/download/scopes_and_permissions.png)
8. Füge diese URL in deinem Browser ein
9. Wähle deinen Testserver aus, bestätige mit "Continue", im nachfoldenden Fenster mit "Authorize" und löse das dämliche Captcha, um den Bot auf deinen Server einzuladen\
![](https://nextcloud.dnns01.dev/index.php/s/zdcomDJTzJCxRQ7/download/add_bot_1.png)
![](https://nextcloud.dnns01.dev/index.php/s/8Jkxr9CCYQcofHt/download/add_bot_2.png)
10. Der Bot sollte nun als User auf deinem Server zu finden sein (allerdings noch Offline)

### Setup des Bots
1. Nachdem du das Repository geklont und Python 3.10 installiert hast, kannst du mit der Einrichtung des Bots starten. Hier beschrieben sind zwei Wege, wie du das tun kannst, entweder durch Verwendung von PyCharm als IDE, oder direkt im Terminal. 
   * Einrichtung unter PyCharm
     1. Klicke auf Open und wähle das Verzeichnis des Repositories aus.
     2. Du solltest dann gefragt werden, wo du dein Virtual Environment erstellen möchtest. Das kannst du mit "Ok" bestätigen \
     ![](https://nextcloud.dnns01.dev/index.php/s/D3mXdS6QDYTgX8x/download/create_venv.png)
     3. Öffne auf der linken Seite die Datei `halloween.py`. Du solltest oben bei den imports keine roten Linien sehen.
   * Sonstige Einrichtung
     1. Nachdem du das Repository geklont hast, und Python 3.10 installiert hast, erstelle ein Virtualenvironment im Terminal mit 
     `python -m venv venv` während du dich im Verzeichnis des Repository befindest
     2. Aktiviere das venv unter Linux mit `source venv/bin/activate`
     3. Mit `python -m pip install -r requirements.txt` installierst du die benötigten Bibliotheken in deinem Virtualenvironment
2. Kopiere die Datei `.env.template` und füge sie als `.env` im gleichen Verzeichnis wieder ein.
3. Öffne die gerade erstellte `.env Datei` und trage dort die entsprechenden Werte ein (alle Werte hinter dem `=` eintragen, ohne Anführungszeichen)
   * `DISCORD_TOKEN`: Hier muss das vorher erstellte Token eingefügt werden
   * `DISCORD_ACTIVITY`: Hier kann die Activity eingetragen werden, also qas dein Bot gerade macht. Zum Beispiel `Halloween-Adventure`
   * `DISCORD_PROD`: Hier trägst du `False` ein
   * `DISCORD_HALLOWEEN_CATEGORY`: Hier gehört die ID der zuvor erstellten Kategorie hin. Die ID bekommst du, indem du einen Rechtsklick auf die Kategorie in Discord machst und dort dann auswählst, dass du die ID kopieren möchtest
   * `DISCORD_ELM_STREET_CHANNEL`: Hier kommt die ID des zuvor erstellten Channels hin. Um an die ID zu kommen auch hier einen Rechtsklick auf den Channel machen. In diesem Channel werden dann die Runden gestartet.
4. Nun müsstest du eigentlich den Bot starten können. Das kannst du entweder tun, indem du im Terminal mit aktiviertem Virtual Environment `python halloween.py` eingibst, oder indem du in PyCharm eine entsprechende Konfiguration erstellst.
   1. Klicke in PyCharm oben rechts auf das Dropdown links neben dem Play Button und wählst dort "Edit Configurations..." aus\
   ![](https://nextcloud.dnns01.dev/index.php/s/z5SddopdK4FL69M/download/edit_config_1.png)
   2. Klicke im nächsten Fenster oben links auf das Plus und wähle dann "Python" aus \
   ![](https://nextcloud.dnns01.dev/index.php/s/ekBNapPGd8w8HDg/download/edit_config_2.png)
   3. Klicke anschließend auf das Ordnersymbol rechts von "Script path:" und wähle dort die `halloween.py` im Hauptverzeichnis des Repositories aus. \
   ![](https://nextcloud.dnns01.dev/index.php/s/ADb4bWXbbGxxYEL/download/edit_config_3.png)
   4. Klicke auf Ok und erneut auf Ok. Anschließens solltest du über den Play Button von PyCharm den Bot starten können.
   5. Sobald der Bot gestartet ist, sollte er kurz darauf in Discord als Online auftauchen. 