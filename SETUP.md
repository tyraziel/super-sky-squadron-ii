Pre-Requisits:

Git for windows:  https://git-scm.com/downloads

vscode: https://code.visualstudio.com/download

python 3
Windows - open a powershell and type in `python` to install the python interpreter from the microsoft store.

Windows Terminal (from the Microsoft Store)


Windows:

Create a virual environment with python:   python3 -m venv .pygame-ce-codemash25

Activate the virtual environment:  source .\.pygame-ce-codemash25\Scripts\activate

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

Windows - allow scripts for the current process:
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

`pip install pygame-ce`

`python test.py`
