from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ExpCon
from selenium.webdriver.chrome.options import Options
import time
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

chrome_options = Options()
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("--disable-blink-features")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
driver = webdriver.Chrome(options=chrome_options)
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)
driver.execute_cdp_cmd(
    "Network.setUserAgentOverride",
    {
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    },
)

wait = WebDriverWait(driver, 30)

months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
est = pytz.timezone("US/Eastern")

CC = ["Discover", "Fidelity", "C1"]


def run_discover():
    driver.get("https://discover.com")
    first_button = wait.until(
        ExpCon.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "a.log-in-link.btn-primary[data-toggle='modal'][data-target='.login-modal']",
            )
        )
    )
    first_button.click()
    # TODO: make this random
    time.sleep(2)
    user_element = wait.until(ExpCon.element_to_be_clickable((By.ID, "userid")))
    user_element.send_keys(os.getenv("DISCOVER_USER"))
    time.sleep(2)
    password_element = wait.until(ExpCon.element_to_be_clickable((By.ID, "password")))
    password_element.send_keys(os.getenv("DISCOVER_PASS"))
    time.sleep(1)
    login_element = wait.until(ExpCon.element_to_be_clickable((By.ID, "log-in-button")))
    login_element.click()


# TODO: Send data as text, random intervals, random daily text, try catch
def run_fidelity(balances, transactions):
    driver.get("https://digital.fidelity.com/prgw/digital/login/full-page")
    time.sleep(2)
    ######## login ########
    user_element = wait.until(
        ExpCon.element_to_be_clickable((By.ID, "dom-username-input"))
    )
    user_element.send_keys(os.getenv("FIDELITY_USER"))
    time.sleep(2)
    password_element = wait.until(
        ExpCon.element_to_be_clickable((By.ID, "dom-pswd-input"))
    )
    password_element.send_keys(os.getenv("FIDELITY_PASS"))
    time.sleep(1)
    login_element = wait.until(
        ExpCon.element_to_be_clickable((By.ID, "dom-login-button"))
    )
    login_element.click()
    time.sleep(2)

    ######## get balance ########
    cc_button_xpath = "//span[text()='Visa Signature Rewards']"
    cc_button_element = wait.until(
        ExpCon.element_to_be_clickable((By.XPATH, cc_button_xpath))
    )
    cc_button_element.click()

    balance_xpath = "//div[@data-cy='creditCardBal']"
    balance_element = wait.until(
        ExpCon.presence_of_element_located((By.XPATH, balance_xpath))
    )
    balance = balance_element.text

    available_credit_xpath = "//span[@data-cy='availableCreditValue']"
    available_credit_element = wait.until(
        ExpCon.presence_of_element_located((By.XPATH, available_credit_xpath))
    )
    available_credit = available_credit_element.text
    balances.append([balance, available_credit, "Fidelity"])

    ######## get transactions ########
    table_xpath = "//div[@class='table']"
    table_element = wait.until(
        ExpCon.presence_of_element_located((By.XPATH, table_xpath))
    )
    table_rows = table_element.find_elements(By.XPATH, "./*")
    for row in table_rows:
        txn_date_xpath = ".//div[@data-cy='ccPostTxnsDate']"
        txn_date_element = row.find_element(By.XPATH, txn_date_xpath)
        txn_date = txn_date_element.text

        txn_desc_xpath = ".//div[@data-cy='ccPostTxnsDescription']"
        txn_desc_element = row.find_element(By.XPATH, txn_desc_xpath)
        txn_desc = txn_desc_element.text

        txn_amt_xpath = ".//div[@data-cy='ccPostTxnsAmount']"
        txn_amt_element = row.find_element(By.XPATH, txn_amt_xpath)
        txn_amt = txn_amt_element.text
        transactions.append([txn_date, txn_desc, txn_amt, "Fidelity"])


def run_c1(balances, transactions):
    driver.get("https://verified.capitalone.com/auth/signin")
    time.sleep(2)

    ######## login ########
    user_element = wait.until(
        ExpCon.element_to_be_clickable((By.ID, "usernameInputField"))
    )
    user_element.send_keys(os.getenv("C1_USER"))
    time.sleep(2)
    password_element = wait.until(
        ExpCon.element_to_be_clickable((By.ID, "pwInputField"))
    )
    password_element.send_keys(os.getenv("C1_PASS"))
    time.sleep(1)
    form_element = wait.until(
        ExpCon.presence_of_element_located((By.NAME, "signInForm"))
    )
    login_element = form_element.find_element(By.TAG_NAME, "button")
    login_element.click()
    time.sleep(2)

    ######## get balance ########
    balance_dollar_xpath = "//div[contains(@class, 'primary-detail__balance__dollar')]"
    balance_dollar_element = wait.until(
        ExpCon.presence_of_element_located((By.XPATH, balance_dollar_xpath))
    )
    balance_dollar_elements = driver.find_elements(By.XPATH, balance_dollar_xpath)
    for element in balance_dollar_elements:
        if element.text != "":
            balance_dollar_element = element
            break
    balance_dollar = balance_dollar_element.text

    balance_cent_xpath = (
        "//div[contains(@class, 'primary-detail__balance__superscript')]"
    )
    balance_cent_element = wait.until(
        ExpCon.presence_of_element_located((By.XPATH, balance_cent_xpath))
    )
    balance_cent_elements = driver.find_elements(By.XPATH, balance_cent_xpath)
    for element in balance_cent_elements:
        if "$" not in element.text and element.text != "":
            balance_cent_element = element
            break
    balance_cent = balance_cent_element.text
    balance = "$" + balance_dollar + "." + balance_cent

    available_credit_dollar_xpath = "//div[@class='primary-content__amount__dollar']"
    available_credit_dollar_element = wait.until(
        ExpCon.presence_of_element_located((By.XPATH, available_credit_dollar_xpath))
    )
    available_credit_dollar = available_credit_dollar_element.text
    available_credit_cent_xpath = "//div[@class='primary-content__amount__superscript']"
    available_credit_cent_element = wait.until(
        ExpCon.presence_of_element_located((By.XPATH, available_credit_cent_xpath))
    )
    available_credit_cent = available_credit_cent_element.text
    available_credit = "$" + available_credit_dollar + "." + available_credit_cent
    balances.append([balance, available_credit, "C1"])
    time.sleep(2)

    ######## get transactions ########
    view_more_element = wait.until(ExpCon.element_to_be_clickable((By.ID, "viewMore")))
    view_more_element.click()

    table_xpath = "/html/body/div[1]/div/div/div/c1-ease-root/c1-ease-card-l2/c1-ease-card-l2-landing/c1-ease-card-transactions-view/div/c1-ease-txns/div/div[4]/div[4]/c1-ease-card-transactions-view-table/c1-ease-table/div[2]"
    table_element = wait.until(
        ExpCon.presence_of_element_located((By.XPATH, table_xpath))
    )
    table_rows = table_element.find_elements(By.XPATH, "./*")
    for row in table_rows:
        month_xpath = (
            ".//c1-ease-cell[2]/c1-ease-txns-date-and-status/div/div/div/span[1]"
        )
        month_element = row.find_element(By.XPATH, month_xpath)
        month = month_element.text
        day_xpath = (
            ".//c1-ease-cell[2]/c1-ease-txns-date-and-status/div/div/div/span[2]"
        )
        day_element = row.find_element(By.XPATH, day_xpath)
        day = day_element.text
        txn_date = month + "-" + day
        if months.index(month) + 1 < datetime.now(est).month or (
            months.index(month) + 1 == datetime.now(est).month
            and int(day) <= datetime.now(est).day
        ):
            txn_date += "-" + str(datetime.now(est).year)
        else:
            txn_date += "-" + str(datetime.now(est).year - 1)

        txn_desc_xpath = (
            ".//c1-ease-cell[3]/c1-ease-txns-description/div/span[2]/div[1]"
        )
        txn_desc_element = row.find_element(By.XPATH, txn_desc_xpath)
        txn_desc = txn_desc_element.text

        txn_amt_xpath = ".//c1-ease-cell[6]/span[1]"
        txn_amt_element = row.find_element(By.XPATH, txn_amt_xpath)
        txn_amt = txn_amt_element.text
        transactions.append([txn_date, txn_desc, txn_amt, "C1"])


def send_email(recipient_email, message):
    msg = MIMEText(message)
    msg["From"] = os.getenv("SENDER_EMAIL")
    msg["To"] = recipient_email
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(os.getenv("SENDER_EMAIL"), os.getenv("SENDER_PASS"))
    server.sendmail(os.getenv("SENDER_EMAIL"), recipient_email, msg.as_string())
    server.quit()


def send_daily_spend():
    balances = []
    transactions = []
    failed = [False, False, False]
    try:
        run_discover()
    except:
        failed[0] = True
    try:
        run_fidelity(balances, transactions)
    except:
        failed[1] = True
    try:
        run_c1(balances, transactions)
    except:
        failed[2] = True
    message = ""
    for i in range(3):
        if failed[i]:
            message += CC[i] + " failed to load\n\n"
    txns_today = [
        txn for txn in transactions if txn[0] == datetime.now(est).strftime("%b-%d-%Y")
    ]
    message += f"Total daily spend for {datetime.now(est).strftime('%A, %b %-d')}: ${str(sum([float(txn[2][1:]) for txn in txns_today]))}\n\n"
    message += "Breakdown:\n"
    for txn in txns_today:
        message += +txn[2] + ": " + txn[1] + "\n"
    message += "\n"
    message += "Balances:\n"
    for balance in balances:
        message += balance[2] + ": " + balance[0] + " available: " + balance[1] + "\n"
    send_email(os.getenv("RECIPIENT_EMAIL"), message)


send_daily_spend()

driver.quit()
