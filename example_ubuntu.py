from gi.repository import Accounts, GObject, Signon
import flickrapi


class AuthProxy(object):
    SERVICE_TYPE = "sharing"
    SUPPORTED_ACCOUNTS = ("flickr")
    # you can get those values below from accounts-console:
    # $ accounts-console list
    # find your flickr account id and run:
    # $ accounts-console show <id>
    # look for ConsumerKey and ConsumerSecret values
    UBUNTU_FLICKR_API_KEY = u"d87224f0b467093b2a87fd788d950e27"
    UBUNTU_FLCIKR_API_SECRET = u"4c7e48102c226509"

    def __init__(self):
        self.flickrapi = None

    def get_account(self):
        account = None
        manager = Accounts.Manager.new_for_service_type(AuthProxy.SERVICE_TYPE)
        # iterate through all available sharing accounts
        for account_service in manager.get_enabled_account_services():
            provider_name = account_service.get_account().get_provider_name()
            if provider_name in AuthProxy.SUPPORTED_ACCOUNTS:
                account = account_service
                break
        return account

    def request_token(self):
        account_service = self.get_account()
        if account_service:
            auth_data = account_service.get_auth_data()
            identity = auth_data.get_credentials_id()
            session_data = auth_data.get_parameters()
            auth_session = \
                Signon.AuthSession.new(identity, auth_data.get_method())

            auth_session.process(session_data, auth_data.get_mechanism(),
                                 self.login_cb, None)
        else:
            print("No flickr account found.")
            # you may consider launching

    def login_cb(self, session, reply, error, user_data):
        if error:
            if self._token_failure_cb:
                self._token_failure_cb(error)

        if "AccessToken" in reply:
            token = flickrapi.auth.FlickrAccessToken(
                    unicode(reply["AccessToken"]),
                    unicode(reply["TokenSecret"]),
                    u"write",
                    unicode(reply["fullname"]),
                    unicode(reply["username"]),
                    unicode(reply["user_nsid"]))
            self.flickrapi = flickrapi.FlickrAPI(
                    AuthProxy.UBUNTU_FLICKR_API_KEY,
                    AuthProxy.UBUNTU_FLCIKR_API_SECRET,
                    token=token)

            # checking token validity is required to properly
            # initialize the provided token in flickrapi
            if self.flickrapi.token_valid():
                print("flickrapi is usable!")
                rsp = self.flickrapi.test.login()
                print("flickrapi.test.login(): %s" % rsp.get("stat"))
            else:
                print("Error: token is not valid")
        else:
            # there was no token in data
            print("No token found in data!")


def main():
    ap = AuthProxy()
    ap.request_token()
    # you need a glib or gtk+ mainloop to be able to handle accounts callback
    GObject.MainLoop().run()

if __name__ == "__main__":
    main()

# More details on Online Accounts framework for app developers:
# http://developer.ubuntu.com/resources/technologies/online-accounts/for-application-developers/
