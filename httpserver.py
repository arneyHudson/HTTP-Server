"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 0NN
- Fall 202N
- Lab N
- Names:
  - 
  - 

An HTTP server

Introduction: (Describe the lab in your own words)




Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked, and any suggestions you have for improvement)





"""

import socket
import threading
import os
import mimetypes
import datetime


def main():
    """ Start the server """
    http_server_setup(8080)


def http_server_setup(port):
    """
    Start the HTTP server
    - Open the listening socket
    - Accept connections and spawn processes to handle requests

    :param port: listening port number
    """

    num_connections = 10
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_address = ('', port)
    server_socket.bind(listen_address)
    server_socket.listen(num_connections)
    try:
        while True:
            request_socket, request_address = server_socket.accept()
            print('connection from {0} {1}'.format(request_address[0], request_address[1]))
            # Create a new thread, and set up the handle_request method and its argument (in a tuple)
            request_handler = threading.Thread(target=handle_request, args=(request_socket,))
            # Start the request handler thread.
            request_handler.start()
            # Just for information, display the running threads (including this main one)
            print('threads: ', threading.enumerate())
    # Set up so a Ctrl-C should terminate the server; this may have some problems on Windows
    except KeyboardInterrupt:
        print("HTTP server exiting . . .")
        print('threads: ', threading.enumerate())
        server_socket.close()


def handle_request(request_socket):
    """
    Handle a single HTTP request, running on a newly started thread.

    Closes request socket after sending response.

    Should include a response header indicating NO persistent connection

    :param request_socket: socket representing TCP connection from the HTTP client_socket
    :return: None
    """
    header = parse_header(request_socket)
    if check_version(header['version']) is False:
        print('fart')
pass  # Replace this line with your code


def check_version(version):
    return version == b'1.1'


def check_resource(resource):
    return 200


def parse_header(data_socket):
    """
    Parses the header from the socket
    :param data_socket: socket where data is coming from
    :return: dictionary full of header values
    """
    dictionary = read_first_line(data_socket)
    header = read_header(data_socket, dictionary)
    data_socket.recv(1)
    return header


def read_header(data_socket, header):
    """
    reads the body of the header
    :param data_socket: socket where data is coming from
    :param header: dictionary to store data
    :return: dictionary full of header values
    """
    data = b''

    # Stops when header is done
    index = 0
    while data != b'\x0d':

        while data != b'\x0a':
            # Stops when line is done
            key = b''
            value = b''
            if index == 0:
                data = data_socket.recv(1)
            while data != b':':
                # Get key
                key += data
                data = data_socket.recv(1)

            # Read 20 in ascii (space)
            data = data_socket.recv(1)

            data = data_socket.recv(1)
            while data != b'\x0d':
                # Get key
                value += data
                data = data_socket.recv(1)

            # Read 0f value to exit loop
            data = data_socket.recv(1)
            header[key] = value

        index += 1
        data = data_socket.recv(1)

    return header


def read_first_line(data_socket):
    """
    reads the first line of the header
    :param data_socket: socket where data is coming from
    :return: dictonary of first line content
    """
    line = dict()

    typ = get_version(data_socket)
    line['version'] = typ

    # get status
    data = data_socket.recv(1)
    status = b''
    while data != b'\x20':
        status += data
        data = data_socket.recv(1)
    line['status'] = status

    # get ok status
    data = data_socket.recv(1)
    ok = b''
    while data != b'\x0d':
        ok += data
        data = data_socket.recv(1)
    line['ok'] = ok

    # read line feed
    data_socket.recv(1)

    return line


def get_version(data_socket):
    """
    gets the http version of the request
    :param data_socket: socket where data is coming from
    :return: the version of http requested
    """
    typ = b''
    data = data_socket.recv(1)
    while data != b'\x20':
        typ += data
        data = data_socket.recv(1)
    return typ


def get_mime_type(file_path):
    """
    Try to guess the MIME type of a file (resource), given its path (primarily its file extension)

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If successful in guessing the MIME type, a string representing the content type, such as 'text/html'
             Otherwise, None
    :rtype: int or None
    """

    mime_type_and_encoding = mimetypes.guess_type(file_path)
    mime_type = mime_type_and_encoding[0]
    return mime_type


def get_file_size(file_path):
    """
    Try to get the size of a file (resource) as number of bytes, given its path

    :param file_path: string containing path to (resource) file, such as './abc.html'
    :return: If file_path designates a normal file, an integer value representing the the file size in bytes
             Otherwise (no such file, or path is not a file), None
    :rtype: int or None
    """

    # Initially, assume file does not exist
    file_size = None
    if os.path.isfile(file_path):
        file_size = os.stat(file_path).st_size
    return file_size


main()

# Replace this line with your comments on the lab
