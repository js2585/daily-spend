import random
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

load_dotenv()

chrome_options = Options()
chrome_options.add_argument("--headless=new")
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

wait = WebDriverWait(driver, 5)

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


# TODO: Posted only works, need to test other combinations (pending and posted)
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
    try:
        no_pending_xpath = "/html/body/div[1]/app-root/div/app-dashboard/div/div/div/div[2]/div[2]/div/div/credit-card-tab/section/div/div/pvd3-tab-group/s-root/div/div[2]/s-slot/s-assigned-wrapper/pvd3-tab-panel[1]/s-root/div/div/s-slot/s-assigned-wrapper/transactions-tab/div/div[2]/p[1]/span"
        wait.until(ExpCon.presence_of_element_located((By.XPATH, no_pending_xpath)))
        first_txn_table_xpath = "/html/body/div[1]/app-root/div/app-dashboard/div/div/div/div[2]/div[2]/div/div/credit-card-tab/section/div/div/pvd3-tab-group/s-root/div/div[2]/s-slot/s-assigned-wrapper/pvd3-tab-panel[1]/s-root/div/div/s-slot/s-assigned-wrapper/transactions-tab/div/div[2]/div[2]/div"
        first_txn_table_element = None
        try:
            first_txn_table_element = wait.until(
                ExpCon.presence_of_element_located((By.XPATH, first_txn_table_xpath))
            )
        except:
            print("No transactions")
            return
        first_txn_table_rows = first_txn_table_element.find_elements(By.XPATH, "./*")
        for row in first_txn_table_rows:
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
    # TODO: test this except
    except:
        # pending and posted transactions
        first_txn_table_xpath = "/html/body/div[1]/app-root/div/app-dashboard/div/div/div/div[2]/div[2]/div/div/credit-card-tab/section/div/div/pvd3-tab-group/s-root/div/div[2]/s-slot/s-assigned-wrapper/pvd3-tab-panel[1]/s-root/div/div/s-slot/s-assigned-wrapper/transactions-tab/div/div[2]/div[2]/div"
        first_txn_table_element = None
        try:
            first_txn_table_element = wait.until(
                ExpCon.presence_of_element_located((By.XPATH, first_txn_table_xpath))
            )
        except:
            print("No transactions")
            return
        first_txn_table_rows = first_txn_table_element.find_elements(By.XPATH, "./*")
        for row in first_txn_table_rows:
            txn_date_xpath = ".//div[@data-cy='ccPendTxnsDate']"
            txn_date_element = row.find_element(By.XPATH, txn_date_xpath)
            txn_date = txn_date_element.text

            txn_desc_xpath = ".//div[@data-cy='ccPendTxnsDescription']"
            txn_desc_element = row.find_element(By.XPATH, txn_desc_xpath)
            txn_desc = txn_desc_element.text

            txn_amt_xpath = ".//div[@data-cy='ccPendTxnsAmount']"
            txn_amt_element = row.find_element(By.XPATH, txn_amt_xpath)
            txn_amt = txn_amt_element.text
            transactions.append([txn_date, txn_desc, txn_amt, "Fidelity"])
        second_table_xpath = "/html/body/div[1]/app-root/div/app-dashboard/div/div/div/div[2]/div[2]/div/div/credit-card-tab/section/div/div/pvd3-tab-group/s-root/div/div[2]/s-slot/s-assigned-wrapper/pvd3-tab-panel[1]/s-root/div/div/s-slot/s-assigned-wrapper/transactions-tab/div/div[2]/div[3]/div"
        second_table_element = wait.until(
            ExpCon.presence_of_element_located((By.XPATH, second_table_xpath))
        )
        second_table_rows = second_table_element.find_elements(By.XPATH, "./*")
        for row in second_table_rows:
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


# TODO: Pending and posted works, need to test rest of combinations (posted only)
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
    pending_table_xpath = "/html/body/div[1]/div/div/div/c1-ease-root/c1-ease-card-l2/c1-ease-card-l2-landing/c1-ease-card-transactions-view/div/c1-ease-txns/div/div[4]/div[3]/c1-ease-card-transactions-view-table/c1-ease-table/div[2]"
    pending_table_element = None
    try:
        pending_table_element = wait.until(
            ExpCon.presence_of_element_located((By.XPATH, pending_table_xpath))
        )
        pending_table_rows = pending_table_element.find_elements(By.XPATH, "./*")
        for row in pending_table_rows:
            expand_xpath = ".//c1-ease-cell[1]"
            expand_element = WebDriverWait(row, 5).until(
                ExpCon.element_to_be_clickable((By.XPATH, expand_xpath))
            )
            expand_element.click()
            extra_info_xpath = ".//c1-ease-txn-drawer"
            extra_info_element = WebDriverWait(row, 5).until(
                ExpCon.presence_of_element_located((By.XPATH, extra_info_xpath))
            )
            date_xpath = ".//div/div/div[1]/div/c1-ease-card-transactions-view-table-drawer-details/div/div[3]/div[1]/div[2]/span"
            date_element = WebDriverWait(extra_info_element, 5).until(
                ExpCon.presence_of_element_located((By.XPATH, date_xpath))
            )
            txn_date = datetime.strptime(date_element.text, "%a, %b %d, %Y").strftime(
                "%b-%d-%Y"
            )

            desc_xpath = (
                ".//c1-ease-cell[3]/c1-ease-txns-description/div/span[2]/div[1]"
            )
            desc_element = row.find_element(By.XPATH, desc_xpath)
            txn_desc = desc_element.text

            amt_xpath = ".//c1-ease-cell[6]/span[1]"
            amt_element = row.find_element(By.XPATH, amt_xpath)
            txn_amt = amt_element.text
            transactions.append([txn_date, txn_desc, txn_amt, "C1"])
    except:
        print("No pending transactions")
    posted_table_xpath = "/html/body/div[1]/div/div/div/c1-ease-root/c1-ease-card-l2/c1-ease-card-l2-landing/c1-ease-card-transactions-view/div/c1-ease-txns/div/div[4]/div[4]/c1-ease-card-transactions-view-table/c1-ease-table/div[2]"
    posted_table_element = None
    try:
        posted_table_element = wait.until(
            ExpCon.presence_of_element_located((By.XPATH, posted_table_xpath))
        )
    except:
        print("No posted transactions")
        return
    posted_table_rows = posted_table_element.find_elements(By.XPATH, "./*")
    for row in posted_table_rows:
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
        if txn_amt[0] != "-":
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
    message = "\n\n"
    try:
        run_discover()
    except:
        message += "Discover failed to load\n\n"
    try:
        run_fidelity(balances, transactions)
    except:
        message += "Fidelity failed to load\n\n"
    try:
        run_c1(balances, transactions)
    except:
        message += "C1 failed to load\n\n"
    txns_today = [
        txn for txn in transactions if txn[0] == datetime.now(est).strftime("%b-%d-%Y")
    ]
    message += f"Total daily spend for {datetime.now(est).strftime('%A, %b %-d')}: ${str(sum([float(txn[2][1:]) for txn in txns_today]))}\n\n"
    message += "Breakdown:\n"
    for txn in txns_today:
        message += txn[2] + ": " + txn[1] + ": " + txn[3] + "\n"
    message += "\n"
    message += "Balances:\n"
    for balance in balances:
        message += (
            balance[2] + ": " + balance[0] + " spent " + balance[1] + " available\n"
        )
    send_email(os.getenv("RECIPIENT_EMAIL"), message)


time.sleep(random.randint(0, 120))
send_daily_spend()

driver.quit()
