# switch

create a venv

```
python3 -m venv /Users/storage/Git/switch/venv
```

Install requirments 

```
/Users/storage/Git/switch/venv/bin/python3 -m pip install -r /Users/storage/Git/switch/requirements.txt 
```

## startup on macos

create the following file under ~/Library/LaunchAgents/org.rotostampa.ftpserver.local.plist

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>ftpserver</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/storage/Git/switch/venv/bin/python3</string>
    <string>/Users/storage/Git/switch/cli.py</string>
    <string>ftpserver</string>
    <string>file://user:admin@localhost/Volumes/Path</string>
  </array>
  <key>KeepAlive</key>
  <true/>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/Users/storage/Git/switch/ftpserver.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/storage/Git/switch/ftpserver.log</string>
</dict>
</plist>
```
