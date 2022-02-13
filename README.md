# Zwift Wine Runner

This handy python script will automatically install and launch Zwift on Linux systems.

It will also automatically login on Zwift saving your password into your system keystore, check for updates, and run user defined commands before launching Zwift.

## Prerequisites

 * python3
 * pip3
 * libnotify
 * GTK3
 * wine
 * winetricks

## Zwift Wine Runner installation

Install the prerequisites with your Linux distribution package manager. 
Download the `zwift-wine-runner` repository by cloning it with git, or using the "Download Zip" function on github, and extract it anywhere on your filesystem.

Open a terminal inside the `zwift-wine-runner` directory, and run
```pip3 install -r requirements.txt``

Then run
```./zwift.py configure```

 * Username and password: these will be used for automatically login to Zwift.
 * DPI: use `192` if you're running Zwift on a HiDPI display. Otherwise leave the default value of `96`.
 * NVIDIA Prime render offload: if you have a system with hybrid display (Intel+NVIDIA), select Y to run Zwift on your NVIDIA discrete graphic card.
 * Check power supply before launch: this will warn you if your laptop is not plugged to AC Power (I've lost a few rides by completely draining my battery, so that's kinda useful...)
 * Custom script: you can launch a custom shell script before launching script. For instance, you can enforce connecting to the right WiFi network: `nmcli connection up <Wifi-Network>`

## Zwift Installation

Open a terminal inside the `zwift-wine-runner` directory, and run
```./zwift.py install```

This should automatically download and install Zwift and its dependencies into a new Wine prefix (`$HOME/.local/share/Zwift-Wine-Runner`)
If anything goes wrong, you can review installation logs in `$HOME/.cache/Zwift-Wine-Runner/logs/`.

At the end of the installation, you will have two new entries in your applications menu: `Zwift` and `Zwift Wine Launcher`. Please ignore (or better, delete) the first, and *only* use the latter.

## Launching Zwift

Use the `Zwift Wine Launcher` application entry in your launcher menu, or just use `./zwift.py run` in your terminal.

It is important that you avoid changing the active window after launching Zwift, or the update checking process and the automatic password typing will not work.

## Uninstall

Open a terminal inside the `zwift-wine-runner` directory, and run
```./zwift.py prune```

