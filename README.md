# switch

create a venv

```
python3 -m venv Git/switch/venv
```

Install requirments 

```
Git/switch/venv/bin/python3 -m pip install -r Git/switch/requirements.txt 
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
    <string>/opt/homebrew/bin/node</string>
    <string>/opt/homebrew/bin/webdav-runner</string>
    <string>server</string>
  </array>
  <key>KeepAlive</key>
  <true/>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/Users/rdv/.webdav-runner/webdav-runner.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/rdv/.webdav-runner/webdav-runner.log</string>
</dict>
</plist>
```
