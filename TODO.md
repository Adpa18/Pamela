## Mandatory part

- [ ] Open an encrypted volume in user's home folder when user log in
	- [ ] To make a mount set userid to 0 (root) in order to mount a volume
	- [ ] Detect that the user has not mounted the directory yet
	- [ ] If a user is logged in twice, it is important that the user's home directory is not unmounted the first time the user logs out.
- [ ] When user log out, close the volume

## Test cases

- [ ] A user with an encrypted home directory (e.g. pamela with the correct password)
- [ ] The above case but with a mistyped password
- [ ] A user without an encrypted home directory (e.g. root with the correct password)
- [ ] The above case but with a mistyped password
- [ ] A non-existent user (e.g. blah)

## Logging

```python
# See https://www.freedesktop.org/software/systemd/python-systemd/journal.html
import logging
from systemd.journal import JournalHandler

log = logging.getLogger('demo')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)
log.info("sent to journal")
```

## Arch

/home/<user>/.pamela_vault/
	container1
	container2
	config.json
	vault

## Build pycryptsetup module

```bash
python3 setup.py
```

## First login

- [ ] authenticate.py
	- [ ] Get user name
	- [ ] Get user password
	- [ ] Write in DB (containerName, password) if savePass

## Tasks

- [ ] config file actions
- [ ] bdd actions
- [ ] device actions
- [ ] 
- [ ] 
- [ ] 
