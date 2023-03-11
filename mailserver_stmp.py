import socket
import threading
import uuid
import typing
from helper_files.MessageWrapper import MessageWrapper
from concurrent.futures import Future, ThreadPoolExecutor
from structlog import get_logger, BoundLogger
from helper_files.ConfigWrapper import ConfigWrapper

# define a semaphore to limit the number of concurrent connections
file_semaphore = threading.Semaphore(1)

# define a dictionary to store the mail process information
tasks = {}


def retrieve_port() -> int:
    # Port to listen on (non-privileged ports are > 1023)
    # implement soft alert -> continue code working if possible
    try:
        my_port = int(input())
        return my_port
    except:
        pass


# consumer
def service_mail_request(data: str, config: ConfigWrapper) -> None:
    data = MessageWrapper()
    usernameTo = data.getToUsername()
    write_to_mailbox(usernameTo, data.getMessageBody())
    

def concurrent_mail_service(data: str, config: ConfigWrapper, executor: ThreadPoolExecutor) -> None:
    # generate a unique task ID
    task_id = uuid.uuid4().hex
    
    # store the task information in the dictionary
    tasks[task_id] = {
        "status": "queued",
        "data": data
    }
    
    # submit the task to the thread pool
    future = executor.submit(service_mail_request, data, config)
    print(f"Task {task_id} submitted to thread pool: {future}")
    
    # update the task status to running
    tasks[task_id]["status"] = "running"
    
    # create a lambda function that calls the handle_result function
    # with the task_id and Future object as arguments
    callback = lambda f: handle_result(task_id, f)

    # register the callback function with the Future object
    future.add_done_callback(callback)


def handle_result(task_id: str, future: Future) -> typing.Any:
    try:
        result = future.result()
        print(f"Task completed with result: {result}")
        # handle the result here


    except Exception as e:
        print(f"Task failed with exception: {e}")
        # update the task status to failed
        tasks[task_id]["status"] = "failed"


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


def loop_server(logger: BoundLogger, config: ConfigWrapper, port: int, executor: ThreadPoolExecutor) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as smtp_socket:
        smtp_socket.bind((config.get_host(), port))
        smtp_socket.listen()
        conn, addr = smtp_socket.accept()
        with conn:
            logger.info(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(config.get_max_size_package_tcp())
                    if not data:
                        # no data received, client has closed the connection
                        logger.info("No data received, closing connection")
                        break
                    message = str(data)
                    concurrent_mail_service(message, config, executor)

                except ConnectionResetError:
                    # client has closed the connection unexpectedly
                    logger.exception("Client closed the connection unexpectedly")
                    break
                except socket.timeout:
                    # no data received within timeout period
                    logger.exception("No data received from client within timeout period")
                except KeyboardInterrupt:
                    # user has interrupted the program execution
                    logger.info("Program interrupted by user")
                    break
                except ValueError:
                    # data received cannot be converted to string
                    logger.exception("Received data cannot be converted to string")
                except Exception as e:
                    # any other exception
                    logger.exception(f"An error occurred: {e}")
                    break

def write_to_mailbox(username: str, message:str) -> None:
    file_semaphore.acquire()

    with open('/{username}/my_mailbox.txt', 'a') as file:
        file.write(message + '\n')    
        file.flush()

    file_semaphore.release()
    
    

def read_from_mailbox(username:str, message:str):
    #no locks
    pass

def main() -> None:
    listening_port = retrieve_port()
    logger = get_logger()
    config = ConfigWrapper(logger,"general_config")
    # create a thread pool with 100 threads
    executor = ThreadPoolExecutor(max_workers=config.get_max_threads())
    loop_server(logger, config, listening_port, executor)


if __name__ == "__main__":
    main()
