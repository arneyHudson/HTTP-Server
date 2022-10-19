"""
- NOTE: REPLACE 'N' Below with your section, year, and lab number
- CS2911 - 011
- Fall 2022
- Lab 5 - HTTP Server
- Names:
  - Josh Sopa
  - Hudson Arney

An HTTP server

Introduction: (Describe the lab in your own words):
This lab creates an HTTP server using a TCP connection. It first has to send a response of bytes
from web resources that are given.


Summary: (Summarize your experience with the lab, what you learned, what you liked,what you disliked,
and any suggestions you have for improvement):
This lab was very interesting because we got to learn how to read request headers, how to create response headers,
and send the requested data through a body of bytes. The hardest part of this lab was debugging the response bytes and
making sure we got every part of the response correct.
Parsing the request header was the easier part of this lab, as we understood the contents of the
header and understood what the different parts meant. This lab gave enough information for us to create it without other
resources. Suggestions for the lab: We wished that the /styles.css in the lab description didn't have a typo because it
caused us to have to look back at the code and wondering what was wrong.



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
    print(header)
    valid_version = check_version(header['version'])
    status_code = check_resource(header['resource'])
    if valid_version:
        send_response(header['resource'], status_code, request_socket)
    else:
        send_response(header['resource'], 400, request_socket)


pass  # Replace this line with your code


def check_version(version):
    """
    Checks if the version is correct
    :param version: the version being requested
    :return: if the version is 1.1
    """
    return version == b'HTTP/1.1'


def check_resource(header):
    resources = [b'/', b'/index.html', b'/msoe.png',
                 b'/styles.css']
    if header in resources:
        code = 200
    else:
        code = 404
    return code


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
    :return: dictionary of first line content
    """
    line = dict()

    typ = get_request_type(data_socket)
    line['type'] = typ

    # get resource
    data = data_socket.recv(1)
    resource = b''
    while data != b'\x20':
        resource += data
        data = data_socket.recv(1)
    line['resource'] = resource

    # get ok status
    data = data_socket.recv(1)
    ok = b''
    while data != b'\x0d':
        ok += data
        data = data_socket.recv(1)
    line['version'] = ok

    # read line feed
    data_socket.recv(1)

    return line


def get_request_type(data_socket):
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


def send_response(resource, status_code, data_socket):
    """
    Depending on the file type being passed which is determined by the resource type,
    the header will be created
    :param data_socket: The socket to where the data needs to be sent
    :param resource: describes the file type
    :param status_code: for the status line
    :return: the sent data to the data_socket
    """
    # depending on what the resource is it will create the associating file_path
    file_path = b''
    if resource == b'/' or resource == b'/index.html':
        file_path = './index.html'
    elif resource == b'/msoe.png':
        file_path = './msoe.png'
    elif resource == b'/styles.css':
        file_path = './styles.css'

    # creates the status line for the header
    header = create_status_line(status_code)
    if status_code != 200:
        data_socket.sendall(header)
    else:
        header += create_header(file_path)
        body = convert_file_to_bytes(file_path)
        print(header+body)
        data_socket.sendall(header + body)
    data_socket.close()


def create_status_line(status_code):
    """
    creates the status line that contains the http version and the status code
    :param status_code: the status code for the given response
    :return: the status line (first line)
    """

    # bytes for the HTTP Version
    http_version = "HTTP/1.1".encode('utf-8')

    # reason phrase which depends on the status code given
    reason_phrase = ""
    if status_code == 200:
        reason_phrase = "OK"
    elif status_code == 400:
        reason_phrase = "Bad Request"
    elif status_code == 404:
        reason_phrase = "Not Found"

    # returns the http version, followed by a space, followed by the status code given, followed by a space,
    # finally followed by the reason phrase of the status code and a CRLF
    return http_version + b'\x20' + str(status_code).encode() \
           + b'\x20' + reason_phrase.encode('utf-8') + b'\x0d\x0a'


def get_mime_type(file_path):
    """
    Try to guess the MIME type of file (resource), given its path (primarily its file extension)
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
    :return: If file_path designates a normal file, an integer value representing the file size in bytes
             Otherwise (no such file, or path is not a file), None
    :rtype: int or None
    """
    # Initially, assume file does not exist
    file_size = None
    if os.path.isfile(file_path):
        file_size = os.stat(file_path).st_size
    return file_size


def create_header(file_path):
    """
    The header that has all the required response types with everything in raw bytes
    :param file_path: the file_path type which determines
    :return: the header with the date followed by CRLF,
    non-persistent connection type followed by CRLF,
    content type from the mime type followed by CRLF,
    and content length which ends with CRLF CRLF
    """
    return create_date() + b'\x0d\x0a' + \
           'Connection: close'.encode() + b'\x0d\x0a' + \
           'Content-Type: '.encode() + get_mime_type(file_path).encode() + b'\x0d\x0a' + \
           'Content-Length: '.encode() + get_file_size(file_path).to_bytes(2, 'big') \
           + b'\x0d\x0a\x0d\x0a'


def create_date():
    """
    helper method for the date that is required for the header
    :return: the date in standard HTTP format
    """
    timestamp = datetime.datetime.utcnow()
    timestring = timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return 'Date: '.encode('utf-8') + timestring.encode('utf-8')


def convert_file_to_bytes(file_path):
    """
    Creates the bytes of the body of the message from the given file_path
    :param file_path: string containing path to (resource) file
    :return: the converted bytes from the resource
    """

    # reads the file as a binary file
    with open(os.path.join(file_path), 'rb') as fobj:
        raw_bytes = fobj.read()
        print(raw_bytes)
    return raw_bytes


main()

# Replace this line with your comments on the lab
