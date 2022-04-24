import os
import psutil
import time
from drowsy.log import Loggable
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def browser_error_handler(func):
    def inner(driver, *args, **kwargs):
        try:
            return func(driver, *args, **kwargs)
        except (WebDriverException, AttributeError):
            driver.logger.exception("Web driver encountered an error.")
            driver.close_driver()
    return inner


class BrowserController(Loggable):

    def __init__(self, extension_paths=None):
        self.driver = None
        self.driver_app = None
        self._pid = None
        self.extension_paths = extension_paths or []
        super(BrowserController, self).__init__()

    @property
    def default_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--profile-directory=Default")
        options.add_argument("--start-maximized")
        for extension_path in self.extension_paths:
            for extension_version in os.listdir(extension_path):
                temp_path = os.path.join(extension_path, extension_version)
                if os.path.isdir(temp_path):
                    full_extension_path = temp_path
                    options.add_argument(
                        f"--load-extension={full_extension_path}")
        options.add_experimental_option(
            "excludeSwitches", ['enable-automation'])
        return options

    @browser_error_handler
    def _init_nba_app(self, username, password):
        if self.driver_app == "nba" and self.driver:
            # ensure we're not in full screen mode
            try:
                video_player = WebDriverWait(self.driver, 1).until(
                    expected_conditions.element_to_be_clickable((
                        By.XPATH,
                        ('//div[contains(@class, "nlQuadPlayer") and '
                         'contains(@class, "sel")]'))))
                if video_player:
                    webdriver.ActionChains(self.driver).move_to_element(
                        video_player).perform()
                    fullscreen_button = WebDriverWait(self.driver, 1).until(
                        expected_conditions.element_to_be_clickable((
                            By.XPATH,
                            ('//div[contains(@class, "nlQuadPlayer") and '
                             'contains(@class, "sel")]'
                             '//div[contains(@class, "nlFullscreenBtnExit")]')
                        ))
                    )
                    if fullscreen_button:
                        fullscreen_button.click()
            except WebDriverException:
                # if something went wrong then we weren't in fullscreen
                pass
            time.sleep(.5)
            self.driver.maximize_window()
            return
        options = self.default_options
        options.add_argument("--app=https://www.nba.com/")
        self.driver_app = "nba"
        self.driver = webdriver.Chrome(options=options)
        self._pid = self.driver.service.process.pid
        time.sleep(1)
        WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((
                By.ID, "onetrust-accept-btn-handler"))).click()
        self.driver.find_element(By.ID, "nbaMenuButton").click()
        self.driver.find_element(By.ID, "nbaMenuNBASignIn").click()
        self.driver.find_element(By.ID, "nbaLoginModalId").send_keys(
            username)
        self.driver.find_element(By.ID, "nbaLoginModalPw").send_keys(
            password)
        WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((
                By.ID, "nbaLoginModalSignIn"))).click()
        # self.driver.find_element(By.ID, "nbaMenuButton").click()
        time.sleep(1)
        WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((
                By.ID, "nbaMenuButton"))).click()
        WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((
                By.ID, "nbaMenuMyAccount")))
        self.driver.find_element(By.ID, "nbaMenuButton").click()
        return True

    @browser_error_handler
    def play_nba_game(self, username, password, team=None):
        """Play an NBA league pass game.

        Opens a browser to nba.com, logs in, and starts a game
        in full screen mode.

        :param str username: NBA LP username
        :param str password: NBA LP password
        :param str team: 3 letter team abbreviation
        :return: `True` if the game was loaded successfully, `False`
            otherwise.

        """
        self._init_nba_app(username, password)
        games = []
        game_elements = self.driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'ScoreboardGame_game__')]")
        for game_element in game_elements:
            try:
                watch_link = game_element.find_element(By.XPATH, "a")
            except WebDriverException:
                continue
            game_data = {"watchLink": watch_link}
            game_lines = game_element.text.split("\n")
            if game_lines and len(game_lines) == 6:
                game_data["awayTeam"] = game_lines[2]
                game_data["awayScore"] = game_lines[3]
                game_data["homeTeam"] = game_lines[4]
                game_data["homeScore"] = game_lines[5]
            elif game_lines and len(game_lines) == 9:
                # playoffs!?
                game_data["awayTeam"] = game_lines[3]
                game_data["awayScore"] = game_lines[4]
                game_data["homeTeam"] = game_lines[6]
                game_data["homeScore"] = game_lines[7]
            else:
                continue
            if game_lines and game_lines[0] == "FINAL":
                game_data["status"] = "COMPLETED"
                game_data["period"] = 4
            elif game_lines and game_lines[0] == "HALF":
                game_data["status"] = "BREAK"
                game_data["period"] = 3
            elif game_lines and game_lines[0].startswith("Q"):
                game_data["status"] = "LIVE"
                game_data["period"] = int(game_lines[0][1])
            elif game_lines and game_lines[0].startswith("END Q"):
                game_data["status"] = "BREAK"
                game_data["period"] = int(game_lines[0][1]) + 1
            elif game_lines and game_lines[0][0].isdigit():
                game_data["status"] = "PREGAME"
                game_data["period"] = 0
            games.append(game_data)
        game = None
        for game in games:
            if game["awayTeam"].lower() == team or game["homeTeam"].lower() == team:
                break
            else:
                game = None
        if not game:
            return True
        self.driver.get(game["watchLink"].get_attribute("href"))
        # wait until new page has loaded
        WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((
                By.ID, "nbaMenuButton")))
        # now check to see if the stream options popped up
        time.sleep(1)
        stream_elements = self.driver.find_elements(
            By.CLASS_NAME, "nba-action-body-row-double") or []
        if not stream_elements:
            # it's pregame...click the Watch button
            watch_button = self.driver.find_element(
                By.XPATH,
                '//button[@data-id="nba:games:game-details:hero:watch"]')
            watch_button.click()
            time.sleep(1)
            modal = WebDriverWait(self.driver, 5).until(
                expected_conditions.element_to_be_clickable((
                    By.ID, "nbaModalContent")))
            try:
                modal.find_element(
                    By.CLASS_NAME, "nba-action-body-unavailable")
                time.sleep(5)
                self.close_driver()
                return True
            except NoSuchElementException:
                stream_elements = self.driver.find_elements(
                    By.CLASS_NAME, "nba-action-body-row-double") or []
        stream_elements += self.driver.find_elements(
            By.CLASS_NAME, "nba-action-body-row-single") or []
        preferred_stream_element = None
        secondary_stream_element = None
        while stream_elements and not preferred_stream_element:
            stream_element = stream_elements.pop()
            # Prefer national broadcasts
            if "ESPN" in stream_element.text or (
                    "TNT" in stream_element.text or
                    "ABC" in stream_element.text):
                preferred_stream_element = stream_element
                stream_elements = []
            elif "HOME" in stream_element.text and (
                    "Spurs" not in stream_element.text):
                secondary_stream_element = stream_element
            elif "AWAY" in stream_element.text and (
                    "Spurs" not in stream_element.text and
                    secondary_stream_element is None):
                secondary_stream_element = stream_element
        preferred_stream_element = (
                preferred_stream_element or secondary_stream_element)
        preferred_stream_element.click()
        fullscreen_button = WebDriverWait(self.driver, 20).until(
            expected_conditions.element_to_be_clickable((
                By.XPATH,
                ('//div[contains(@class, "nlQuadPlayer") and '
                 'contains(@class, "sel")]'
                 '//div[contains(@class, "nlFullscreenBtn")]'))))
        time.sleep(3)
        fullscreen_button.click()
        return True

    def close_driver(self):
        if self.driver is not None:
            self.driver_app = None
            try:
                self.driver.close()
            except WebDriverException:
                self.logger.warning(
                    "Browser was closed manually. Terminating driver process.")
                if self._pid:
                    proc = psutil.Process(pid=self._pid)
                    proc.kill()
            self.driver = None
            self._pid = None

    def __del__(self):
        self.logger.info("Removing browser driver.")
        self.close_driver()
