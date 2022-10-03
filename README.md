# Discord Halloween Adventure

## Inhaltsverzeichnis
1. [Setup](#setup)
   1. [Setup des Discord Servers](#setup-des-discord-servers)
   2. [Erstellen des Bot Accounts](#erstellen-des-bot-accounts)
   3. [Setup des Bots](#setup-des-bots)
2. [Aufbau der story.json](#aufbau-der-storyjson)

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

## Aufbau der story.json

Beispiel story.json: 

```json
{
  "events": {
    "continue": [
      {
        "text": "Ihr geht weiter zur nächsten Tür.",
        "next": "doors"
      }
    ],
    "skip": [
      {
        "text": "Ihr seit euch nicht sicher, was ihr von der Tür halten sollt und lauft weiter.",
        "next": "doors",
        "courage_min": 5,
        "courage_max": 7
      }
    ],
    "doors": [
      {
        "text": "Ihr seht eine alte Heuschupfe auf einem Feld stehen. \nZwischen den Balken leuchtet der unstete Schein eines offenen Feuers hindurch. \nNach dem Motto: \"Wer nicht wagt, der nicht gewinnt\", macht ihr euch auf den Weg. \nDas höfliche Klopfen an der Tür entfällt, da es keine Tür gibt. \nIhr werft einen Blick ins Innere und euch gefriert das Blut in den Adern. \nAuf dem Boden um ein kleines Feuer sitzen große haarige Gestallten mit riesigen Hörnern und grotesk verzogenen Gesichtern. \nIhr nehmt die Beine in die Hand und rennt los, bloß weg von diesem Ort.",
        "courage_min": 19,
        "courage_max": 21,
        "next": "doors"
      }
    ],
    "knock_on_door": [
      {
        "text": "Die Haustür wird von einem Schrank von einem Mann geöffnet. \nEuer \"Süßes oder Saures\" bleibt euch im Hals stecken, als ihr euer Gegenüber genauer anschaut. Er stützt sich auf eine Axt und sein Hemd hat feuchte rote Flecken. \nEuch verlässt der Mut und ihr lauft weiter, nicht ohne noch schnell in die Schüssel mit Süßigkeiten neben der Tür gegriffen zu haben.",
        "sweets_min": 7,
        "sweets_max": 15,
        "courage_min": 9,
        "courage_max": 16,
        "view": "knock"
      }
    ],
    "fear": [
      {
        "text": "Ihr lasst eure Blicke über die Körper euer Gruppenmitglieder schweifen. Als eure Blicke an den Beinen ankommen und ihr das Schlottern seht merkt Ihr, wie eure Beine nachgeben und Ihr zu boden sinkt. Das Sammeln von Süßigkeiten ist wohl erstmal vorüber.",
        "view": "fear"
      }
    ]
  },
  "views": {
    "door": [
      {
        "label": "Anklopfen",
        "custom_id": "elm_street:knock",
        "value": "knock_on_door"
      },
      {
        "label": "Weitergehen",
        "custom_id": "elm_street:next",
        "value": "skip"
      }
    ]
  }
}
```

Wie man an der Beispiel story.json erkennen kann, besteht diese aus zwei Hauptbereichen, den `events` und den `views`. 

Views sind Buttons, die unter einer Nachricht angezeigt werden können. In diesem Beispiel haben wir einen Ausschnitt der View `doors`. Eine View besteht dann aus einem Array von Objects, dass jeweils die Attribute `label`, `custom_id` und `value` enthält. Das Label ist der Text, der auf dem Button angezeigt wird, die custom_id muss eine eindeutige ID sein, die beispielsweise jeder "Anklopfen" Button einer `door` View hat. Zum Schluss gibt es noch den Value. Dabei handelt es sich um das Event, dass ausgelöst wird, wenn dieser Button gedrückt wird.

Die Events sind hierbei schon deutlich komplexer. Events bestehen aus einem Array von Objects. Beim Auslösen des Events wird zufällig eines aus dem Array ausgewählt und verarbeitet. Das Object eines Events enthält immer einen `text`, welcher in den jeweiligen Discord Thread gesendet wird. Es kann dann entweder ein `next` oder eine `view` enthalten. Beinhaltet es ein `next` wird anschließend dieses Event ausgeführt. Wir sehen das im obigen Beispiel am `continue` Event. Hier wird in den Chat der Text "Ihr geht weiter zur nächsten Tür" geschrieben und anschließend das Event `doors` ausgeführt. Ist stattdessen eine `view` angegeben, wie beispielsweise beim Event `doors`, so wird die referenzierte View unter der Nachricht angezeigt und der Bot wartet darauf, dass ein Button gedrückt wird. Zusätzlich dazu kann über `courage_min` und `courage_max`, sowie `sweets_min` und `sweets_max` festgelegt werden, wieviele Süßigkeiten gewonnen, bzw. Mut verloren werden kann. Im angegebenen Bereich wird dann ein zufälliger Wert ausgewürfelt. Bei den Süßigkeiten können auch negative Werte verwendet werden, um die Spieler Süßigkeiten verlieren zu lassen (beispielsweise im Falle, dass die Spieler sich erschrecken und wegrennen).   