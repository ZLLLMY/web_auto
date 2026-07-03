from pages.saucelab_loginpage import SauselabLoginPage


class Sauselab:

    @staticmethod
    def login(driver, username, password):
        lp = SauselabLoginPage(driver)
        lp.get_username_field().send_keys(username)
        lp.get_password_field().send_keys(password)
        lp.get_login_button().click()