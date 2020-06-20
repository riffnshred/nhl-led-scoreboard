![nhl_setup](../../assets/images/nhl_setup.gif)
In the score board root, there is a compiled version of the nhl_setup.py.  You can run this and it will look for a config.json or config.json.sample in the config directory (not the src/config directory).  If those files don't exist, it will present you with defaults and you can select what you want.  After answering all of the questions, the app will create a config.json in the config directory and you can then run your scoreboard.  If it finds a config.json or config.json.sample, it will use the values in those as defaults in the questions.

To run the compiled app, do the following:

```
./nhl_setup
```

> **_NOTE:_** The compiled app will be slower than running the python code as it has to uncompress some libraries to disk first.  Running as the compiled app removes the need to do any type of package installs with pip.

If you want to run this as pure python and not the app, you will need to install the following pip3 packages:

```
printtools==1.2
questionary==1.5.1
regex==2020.2.20
```
As the RGB matrix library needs to run as the root user, you will need to install using sudo.  

```
sudo pip3 install printtools
sudo pip3 install questionary
sudo pip3 install regex
```

If you run the python script from the src/nhl_setup directory you will need to give the full path of the config directory so it can find the config.json.  For example:

```
python3 src/nhl_setup/nhl_setup.py /home/pi/source/nhl-led-scoreboard/config
```

If the app can't find your config directory, it will error out and tell you it can't find it.

The very first thing you will see is this:

🥅🏒🚨 Do you see a net,stick and horn?  (Y/n)

Hit yes it you see them.  This means your terminal has nice fancy fonts installed.  If you see something like:

   Do you see a net,stick and horn?  (Y/n)

Hit no because your terminal doesn't like fancy fonts.

## Common error messages you might encounter
| Error Message  |  What it means |
|---|---|
| Could not make backup of config/config.json. This is normal for first run.  Message: [Errno 2] No such file or directory: 'config/config.json' |  The config.json file does not exist.  You can continue without issue. |
| Error making backup of config/config.json. Error: [Errno 2] No such file or directory: 'config/config.json' | Same as above but for older version of nhl_setup |
| json.decoder.JSONDecodeError: Expecting ',' delimiter: line 69 column 20 (char 1075) [17959] Failed to execute script nhl_setup | This means your starting config.json is corrupt, was it edited improperly |
| PermissionError: [Errno 13] Permission denied: 'config/config.json' [3838] Failed to execute script nhl_setup | Did you create a config.json by running sudo nano config.json?  If so, run the nhl_setup app with sudo

>## Notes to create a compiled nhl_setup app
The PyInstaller package was used to created an executable app.  It was the only one that I could get to work properly.  Once you install pyinstaller, this is the command line that I used to create an compiled version:
```
pyinstaller --onefile --add-data '/usr/local/lib/python3.7/dist-packages/pyfiglet:./pyfiglet'  nhl_setup.py
```

This will create a build and dist directory in the same directory as the nhl_setup.py.  Under the dist directory is the compiled executable.  The only downside to this is it's slower to run than runinng via python directly.

