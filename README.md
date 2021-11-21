# Multithread_SSH_BruteForce
This program performs SSH BruteForce using multithread with paramiko.

# Notes
1. Make sure to keep the usernames.txt and the 100pass.txt in the same folder as the SSHMultithread.py
2. The default value of MaxStartups 10:30:100 in etc/ssh/sshd_config in the target machine allows for maximum 5 threads before the code starts throwing exception.

# Usage
SSHMultithread.py [-h] ip [threads] [passwords] [usernames]
