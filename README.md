remco
=====

<b>Remote command in Python using Pyro4, e.g. control your Raspberry PI remotely.</b>

Very simple program to do remote commmands and send (put) or retrieve (get) files.
Some local commands are also possible to navigate locally.
You could say it combines ssh and scp, except that this approach should be used on a closed network, since there is no security involved.

For this to work Pyro4 has to be installed on the local and the remote system, say this is your PI.
Then, on the PI, start the Pyro4 flameserver, but first execute:

export PYRO_FLAME_ENABLED=true

followed by:

python -m Pyro4.utils.flameserver -H x.x.x.x -p 9999

where x.x.x.x is the (fixed) IP address of the PI.

Then, on the local machine start remco.py and enter some Linux commands (without the quotes)

'ls' will ls on the PI and show the result on your local system.
'cd' will change the directory on your PI.

Local commands must be preceded by a '.', so:
'.ls' will do ls on your local system.
'.cd' will do a local cd

'put filename'    will copy a file from your current local directory to the current remote directory,

'get filename'    will do the reverse (from remote to local)
