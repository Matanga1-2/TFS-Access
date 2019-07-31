from os import path
from os import remove

class CredentialsError(Exception):
    pass

def get_credentials():
    """
    The function checks if credentials exists in the config file.
    If not, it asks for the user to input his credentials.
    :return: A 'credentials' dictionary
    """

    # Check the connection credentials, if they do not exist get and save them
    credentials = {}
    if path.isfile('./config.txt'):
        f = open("config.txt", "r")
        try:
            if f.mode == 'r':
                credentials_input = f.readlines()
                credentials['userName'] = credentials_input[0].rstrip()
                credentials['password'] = credentials_input[1].rstrip()
                credentials['uri'] = credentials_input[2].rstrip()
                credentials['project'] = credentials_input[3].rstrip()
                credentials['name'] = credentials_input[4].rstrip().replace(r'\\',r'\'').replace(r"'","")
                f.close()
            else:
                print("There was an error getting the credentials. Please try again")
                raise CredentialsError
        except IndexError:
            f.close()
            remove("config.txt")
            print("There was a problem reading your credentials. Please try again...")
            raise CredentialsError
    else:
        print("It looks like this is your first time...")
        credentials['userName'] = input("What is your TFS username? ")
        credentials['password'] = input("What is your TFS password? ")
        first_name = input("What is your first name? ")
        last_name = input("What is your last name? ")
        credentials['name'] = first_name + " " + last_name + "<NET-BET\\" + first_name + last_name[0] + ">"
        credentials['uri'] = "https://tfs2018.net-bet.net/tfs/DefaultCollection/"
        credentials['project'] = "theLotter"

        # Save credentials in config file
        f = open("config.txt", "w+")
        f.write(credentials['userName'] + "\n")
        f.write(credentials['password'] + "\n")
        f.write(credentials['uri'] + "\n")
        f.write(credentials['project'] + "\n")
        f.write(credentials['name'] + "\n")
    return credentials