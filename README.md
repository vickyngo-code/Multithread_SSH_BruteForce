# Multithread_SSH_BruteForce
This program performs SSH BruteForce using multithread with paramiko. 

Change "MaxStartups 10:30:100" in etc/ssh/sshd_config of your target machine to higher values so that the server does not reject connections when using too many threads to brute force in. 
(The default value of 10:30:100 allows a maximum of 5 threads before starting to throw exceptions)

Incomplete:
- User input for host ip
