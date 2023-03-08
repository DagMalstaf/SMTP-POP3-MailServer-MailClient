import socket


HOST = "127.0.0.1"
MAX_SIZE_TCP_PACKET = 65535

def retrieve_port() -> int:
    # Port to listen on (non-privileged ports are > 1023)
    # implement soft alert -> continue code working if possible
    try:
        my_port = int(input())
        return my_port
    except:
        pass


# consumer
def service_mail_request(data: str):
    username = data
    with open('/{username}/my_mailbox.txt', 'w') as file:
    file.write()

    # Close the file
    file.close()

    pass

#producer
def concurrent_mail_service(data: str):
    producer_thread = threading.Thread(target=service_mail_request, args=(data,))
    producer_thread.start()
    print(f"Producer thread started")

    pass

def service_mail_request(data: str):
    #pop3 function implementation
    pass

def POP3_HELO():
    pass

def POP3_MAIL_FROM():
    pass

def POP3_RCPT_TO():
    pass

def POP3_DATA():
    pass

def POP3_QUIT():
    pass

def concurrent_mail_service(data: str):
    # maybe lock for max events
    pass

def loop_server(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(MAX_SIZE_TCP_PACKET)
                    message = str(data)
                    concurrent_mail_service(message)
                except: # let crash for specific exception code
                    pass

def write_to_mailbox(username: str, message:str):
    #locks & signal (queue)
    pass

def read_from_mailbox(username:str, message:str):
    #no locks
    pass

def main() -> None:
    listening_port = retrieve_port()
    loop_server(listening_port)


if __name__ == "__main__":
    main()
