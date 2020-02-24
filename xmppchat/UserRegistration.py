import sys, subprocess

class UserRegistration:
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

    def register_remotely(self, registration_user, registration_passwd, server_domain):
        """
            creates a user on ejabberd-database with the ejabberdctl erlang command line tool on the chatserver
            supports sudo and no sudo command execution
            registration_user: user to registrate on the chatserver
            registration_passwd: password of the user to registrate
            server_domain: specify the jid domain like ejabberd-server
            return: return code of remote command execution -> 0: on success, 1: on error case
        """
        if self.sudo_passwd:
            COMMAND = f"echo \"{self.sudo_passwd}\" | ssh -tt -i {self.priv_key} {self.host} \"sudo ejabberdctl register {registration_user} {server_domain} {registration_passwd}\""
        else:
            COMMAND = f"ssh -tt -i {self.priv_key} {self.host} \"ejabberdctl register {registration_user} {server_domain} {registration_passwd}\""

        result = subprocess.Popen(COMMAND, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = result.communicate()
        return result.returncode




        



