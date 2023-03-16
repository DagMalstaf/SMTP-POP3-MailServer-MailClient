

# https://www.geeksforgeeks.org/args-kwargs-python/
# see MailManagement
def pop3_authentication(**kwargs) -> bool:
    username = kwargs.get("username")
    password = kwargs.get("password")
    return True
    #TODO: authentication is done on pop3 server
    #TODO: sending username and hashed password to pop3 server
    #TODO: return bool to signal successful authentication

    #TODO: IMPORTANT: ask for information on mail management on the establishment of a connection to pop3 sever
    #TODO: after authentication, but we have to send credentials to authenticate ?????


def pop3_stat() -> None:
    pass

def pop3_list(**kwargs) -> None:
    #TODO: see format in assignment
    username = kwargs["username"] # see line 24 in MailManagement
    list_emails = list()
    [print(email) for email in list_emails]
    pass

def pop3_retrieve() -> None:
    #TODO: probebly meant to retreive full body, not just the summery like in list
    # caching of list to service request?? allowed??
    input("Give serial number of mail you wish to retreive:")
    pass

def pop3_delete() -> None:
    input("Give serial number of mail you wish to delete:")
    pass

def pop3_count() -> None:
    pass

def pop3_quit() -> None:
    pass

