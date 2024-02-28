from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

def main():
    # Define the directory where the files will be stored
    ftp_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()
    
    # Define a user with write access
    authorizer.add_user("admin", "admin123", ftp_directory, perm="elradfmw")
    
    # Instantiate an FTP handler object
    handler = FTPHandler
    handler.authorizer = authorizer
    
    # Define the address and port of the server
    server_address = ("192.168.0.200", 21)
    
    # Instantiate the FTP server
    server = FTPServer(server_address, handler)
    
    # Start the FTP server
    server.serve_forever()

if __name__ == "__main__":
    main()
