## Description
This project is a fullstack smartlock system on a raspberry pi. The user can be authentificated with either RFID, QR-Code, Password or Face recognition

## Intallation
to setup the system environment and dependencies run in terminal. Change <user> with your rpi username, also in the launch_app.sh
```bash
cd /home/<user>/Desktop
git clone <this_reop_git_url>
cd Smartlock-System
bash setup_app.sh
```

## Configuration
- If you are using a touch display, you need to configure Kivy to use it as an input source. 
    To do this, edit the file ~/.kivy/config.ini and go to the [input] section. Remove this line:
    ``hid_%(name)s = probesysfs,provider=hidinput`` or add this line if it fits the touch screen better:
    ``mtdev_%(name)s = probesysfs,provider=mtdev``
- Go to the [graphics] section and change the value of 'fullscreen' like this: ``fullscreen = 1``. Because the value: 0 means no fullscreen
- On the [kivy] section change the value of 'keyboard_mode' like this:  ``keyboard_mode = systemanddock``
## To launch the app
```bash
bash launch_app.sh
```
## For auto run in reboot
Run in the terminal
```bash
crontab -e
```
Add this line:
```
@reboot bash /home/<user>/Desktop/Smartlock-System/launch_app.sh
```
