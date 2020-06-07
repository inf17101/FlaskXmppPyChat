import sys, subprocess

class UserManagement:
    """
        this class should registrate a user on ejabberd chatserver database
        it validates whether registration process was successfully or not
    """

    def __init__(self, host, connection_user, passwd="", priv_key="", sudo_passwd=""):
        self.host = host
        self.connection_user = connection_user
        self.passwd = passwd
        self.priv_key = priv_key
        self.sudo_passwd = sudo_passwd

    def create_user_remotely(self, username, passwd, server_domain):
        """
            creates a user on ejabberd-database with the ejabberdctl erlang command line tool on the chatserver
            supports sudo and no sudo command execution
            username: user to registrate on the chatserver
            passwd: password of the user to registrate
            server_domain: specify the jid domain like ejabberd-server
            return: return code of remote command execution -> 0: on success, 1: on error case
        """
        if self.sudo_passwd:
            COMMAND = f"echo \"{self.sudo_passwd}\" | ssh -tt -i {self.priv_key} {self.host} \"sudo ejabberdctl register {username} {server_domain} {passwd}\""
        else:
            COMMAND = f"ssh -tt -i {self.priv_key} {self.host} \"ejabberdctl register {username} {server_domain} {passwd}\""

        result = subprocess.Popen(COMMAND, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = result.communicate()
        return result.returncode

    def delete_user_remotely(self, username, server_domain):
        """
            deletes a user on ejabberd-database with the ejabberdctl erlang command line tool on the chatserver
            supports sudo and no sudo command execution
            username: user to registrate on the chatserver
            server_domain: specify the jid domain like ejabberd-server
            return: return code of remote command execution -> 0: on success, 1: on error case
        """
        if self.sudo_passwd:
            COMMAND = f"echo \"{self.sudo_passwd}\" | ssh -tt -i {self.priv_key} {self.host} \"sudo ejabberdctl unregister {username} {server_domain}\""
        else:
            COMMAND = f"ssh -tt -i {self.priv_key} {self.host} \"ejabberdctl unregister {username} {server_domain}\""

        result = subprocess.Popen(COMMAND, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = result.communicate()
        return result.returncode

    def change_password_remotely(self, username, server_domain, new_password):
        """
            changes the password of a user on ejabberd-database with the ejabberdctl erlang command line tool on the chatserver
            supports sudo and no sudo command execution
            username: user to registrate on the chatserver
            server_domain: specify the jid domain like ejabberd-server
            new_password: new password of the user
            return: return code of remote command execution -> 0: on success, 1: on error case
        """
        if self.sudo_passwd:
            COMMAND = f"echo \"{self.sudo_passwd}\" | ssh -tt -i {self.priv_key} {self.host} \"sudo ejabberdctl change_password {username} {server_domain} {new_password}\""
        else:
            COMMAND = f"ssh -tt -i {self.priv_key} {self.host} \"ejabberdctl change_password {username} {server_domain} {new_password}\""

        result = subprocess.Popen(COMMAND, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = result.communicate()
        return result.returncode




