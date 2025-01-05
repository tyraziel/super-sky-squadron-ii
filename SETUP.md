# Pre-Requisits:

- Git: via a packaging manager or https://git-scm.com/downloads / (windows) https://git-scm.com/downloads/win
- vscode: https://code.visualstudio.com/download
- python 3
- - Windows - open a powershell and type in `python` to install the python interpreter from the microsoft store.
- Windows Terminal (from the Microsoft Store)

## Windows:

Create a virual environment with python in a directory that you have write permissions in.  
Open a terminal window in powershell (it should open in your "users" directory) and execute the following:

```shell
python3 -m venv .pygame-ce-codemash25
```

Activate the virtual environment by executing the following:  

```shell
.\.pygame-ce-codemash25\Scripts\activate
```

If you see an error similar to the following, then you need to enable script executions (you will also need this for the setup.ps1 script you will execute later):

```
.\.pygame-ce-codemash25\Scripts\activate : File C:\Users\Andrew\sbx\.pygame-ce-codemash25\Scripts\Activate.ps1 cannot
be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at
https:/go.microsoft.com/fwlink/?LinkID=135170.
At line:1 char:1
+ .\.pygame-ce-codemash25\Scripts\activate
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

To enable script executions and have it apply to only the current process (i.e. the powershell prompt you're currently at) execute the following:

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

and then try executing the following again:

```shell
.\.pygame-ce-codemash25\Scripts\activate
```

If all is successful then you should see something similar to the following:

```
(.pygame-ce-codemash25) PS C:\Users\Andrew> 
```

Notice that the name of your virtual environment is in the beginning of the command prompt.


`pip install pygame-ce`

`run setup`

`python codemash2025.py`


To leave or deactivate your venv execute 
```
deactivate
``` 

And you should see the command prompt return to normal (the virutal environment is no longer prefixed at the prompt)

Linux Based:

If the venv command fails, install the proper python3-venv package from your system's package manager.
wsl ubnutu 22.04LTS:

```
$ python3 -m venv .pygame-ce-codemash25
The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.10-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.

Failing command: ['/home/andrew/sbx/.pygame-ce-codemash25/bin/python3', '-Im', 'ensurepip', '--upgrade', '--default-pip']

$ sudo apt update
$ sudo apt install python3-venv
```

create venv, activate, install pip reqs and install ansible-core.
If not present install unzip/zip

If the ansible-playbook command fails with the following error, install zip.

```
Unable to find required 'unzip' or 'unzip' binary in the path.
```

```
sudo apt install zip
```


Chromebook: (tested on amd64 architecture)

(https://code.visualstudio.com/blogs/2020/12/03/chromebook-get-started)

Settings - search for linux in the top search bar.

Click on "Set up Linux development environment"
Under "Developers" in the Linux development environment, click "Set up" button.

On the Set Up Linux development environment: Click Next

Keep defaults (user name and disk size) and click "Install"

It downloads a virtual machine, then starts a command prompt (took about 1:40 [mi:ss] on a test chromebook)

Install gnome-keyring

Download vscode for your Chromebook's architecture, click show downloads and click to install the .deb file.  Click install from the "install app with linux" box.  Click Ok.  Install should complete and you should see vscode in your apps list under "linux apps", if it didn't work you'll need to manually install vscode by copying the file from your downloads to linux files and then in the command prompt - sudo apt install <location_of_file> -- allow the signing key which shows up about 70-80% into the installation.


`code .` in the terminal to test

apt install python3.11-venv
create venv and activate, install pip reqs, install ansible-core


Windows based systems:  
execute 
`cd setup`
`setup.ps1`

Linux based systems (Including Chromebook Linux Development Environment and Windows WSL):
after activating the python virtual environment execute:
`cd setup`
`ansible-playbook setup.yaml`




The Assets:

Kenney Fonts:  https://kenney.nl/assets/kenney-fonts
Kenney Space Shooter Redux:  https://kenney.nl/assets/space-shooter-redux
