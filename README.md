# switch

install uv

```
brew install uv
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
    <string>/Users/storage/Scripts/switch/run.sh</string>
    <string>ftpserver</string>
    <string>file://storage:password@localhost/Volumes/Storage/Switch</string>
    <string>file://file:password@localhost/Volumes/NasMaster/DbStorage</string>
    <string>file://lastre:password@localhost/Volumes/Storage/Switch/Lastre</string>
    <string>file://machine:password@localhost/Volumes/Storage/Switch/Machine</string>
    <string>--watch</string>
    <string>/Volumes/Storage/Switch/COMMAND</string>
  </array>
  <key>KeepAlive</key>
  <true/>
  <key>RunAtLoad</key>
  <true/>
    <key>UserName</key>
    <string>storage</string>
  <key>StandardOutPath</key>
  <string>/Users/storage/Scripts/switch/ftpserver.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/storage/Scripts/switch/ftpserver.log</string>
</dict>
</plist>
```


### work with this repo

## run from cli

```run.sh ...```


## format the code

```uv run --with black black .```