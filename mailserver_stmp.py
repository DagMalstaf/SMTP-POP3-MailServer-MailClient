import socket
import threading

from structlog import get_logger, BoundLogger

from helper_files.ConfigWrapper import ConfigWrapper


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


def loop_server(logger: BoundLogger, config: ConfigWrapper, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as smtp_socket:
        smtp_socket.bind((config.get_host(), port))
        smtp_socket.listen()
        conn, addr = smtp_socket.accept()
        with conn:
            logger.info(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(config.get_max_size_package_tcp())
                    message = str(data)
                    concurrent_mail_service(message)
                except: # let crash for specific exception code
                    pass

def write_to_mailbox(username: str, message:str):
    #TODO: locks & signal (queue) DAG
    pass

def read_from_mailbox(username:str, message:str):
    #no locks
    pass

def main() -> None:
    listening_port = retrieve_port()
    logger = get_logger()
    config = ConfigWrapper(logger,"general_config")
    loop_server(logger, config, listening_port)


if __name__ == "__main__":
    main()
