Members:
Hai Nguyen - hai_nguyen@csu.fullerton.edu
Gordon Dan - gdan189@csu.fullerton.edu

----------------------------------------------
Assignment 1 - FTP client/server:
- Operating system: Windows 10 
- Language: python 3.7

- How to use:
Client side: python cli.py <host> <port_number>
    example: python cli.py localhost 6789
Client's commands:
	ls : list all files on the server
	get <file_name>: download <file_name> from the server and store in 'download' folder
	put <file_name>: upload <file_name> to the server and store in 'upload' folder in the server
	quit : disconnect from the server and quit

Server side: python serv.py <port_number>
    example: python serv.py 6789	

----------------------------------------------
Note:
- This project is done in Windows 10. Although cli.py sends "ls" to list the files, serv.py calls "dir"
instead of "ls -l" to list the files.

- If your computer has both python 2 and python 3, use python3 to run the *.py files
example: python3 serv.py 6789
         python3 cli.py localhost 6789
