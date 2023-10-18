import subprocess
import time
import sys

DEBUG = False

if "-d" in sys.argv:
    DEBUG = True

def run_test_program(listen_port, key_file, server_name, server_port, message_filename, signature_filename):
    # Start the server
    if DEBUG:
        server_command = ["python3", "server.py", listen_port, key_file , "-d"]
    else:
        server_command = ["python3", "server.py", listen_port, key_file]
        
    server_process = subprocess.Popen(server_command)

    # Give the server some time to start
    time.sleep(2)

    # Start the client
    if DEBUG:
        client_command = ["python3", "client.py", server_name, server_port, message_filename, signature_filename, "-d"]
    else:
        client_command = ["python3", "client.py", server_name, server_port, message_filename, signature_filename]
    client_process = subprocess.Popen(client_command)

    # Wait for the client to finish
    client_process.communicate()

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ["basic", "med", "adv"]:
        print("Usage: test.py [basic|med|adv] [-d]")
        sys.exit(1)

    test_type = sys.argv[1]
    folder_map = {
        "basic": ("Basic-message", "1"),
        "med": ("Medium-message", "2"),
        "adv": ("Advanced-Message", "3")
    }
    folder_name, number = folder_map[test_type]

    run_test_program("7894", 
                     f"Messages/{folder_name}/key.txt", 
                     "localhost", 
                     "7894", 
                     f"Messages/{folder_name}/message{number}.txt", 
                     f"Messages/{folder_name}/signature{number}.txt")
