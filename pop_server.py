import socket
import threading
import uuid
import typing
from helper_files.MessageWrapper import MessageWrapper
from concurrent.futures import Future, ThreadPoolExecutor
from structlog import get_logger, BoundLogger
from helper_files.ConfigWrapper import ConfigWrapper



def retrieve_port() -> int:
    try:
        my_port = int(input("Enter a port number (non-privileged ports are > 1023): "))
        if my_port > 1023:
            return my_port
        
        else:
            print("Port number must be greater than 1023.")
            return retrieve_port()
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        return retrieve_port()

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

def main() -> None:
    listening_port = retrieve_port()
    logger = get_logger()
    config = ConfigWrapper(logger,"general_config")

    # create a thread pool with 100 threads
    executor = ThreadPoolExecutor(max_workers=config.get_max_threads())
    loop_server(logger, config, listening_port, executor)


if __name__ == "__main__":
    main()