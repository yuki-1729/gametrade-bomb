import os
import time
import yaml
import base64
import colorama
import tls_client

from faker import Faker
from bs4 import BeautifulSoup
from anticaptchaofficial.recaptchav2proxyless import *

class MailBox:
    def __init__(self):
        self.session = tls_client.Session(
            client_identifier="safari_16_0",
            random_tls_extension_order=True
        )

        response = self.session.put("https://www.developermail.com/api/v1/mailbox")
        self.name = response.json()["result"]["name"]
        self.token = response.json()["result"]["token"]

    def get_message(self):
        while True:
            response = self.session.get(
                f"https://www.developermail.com/api/v1/mailbox/{self.name}",
                headers={
                    "X-MailboxToken": self.token
                }
            )
            try:
                msg_id = response.json()["result"][0]
                break
            except:
                time.sleep(1)

        response = self.session.get(
            f"https://www.developermail.com/api/v1/mailbox/{self.name}/messages/{msg_id}",
            headers={
                "X-MailboxToken": self.token
            }
        )

        for line in base64.b64decode(response.json()["result"].split("\r\n\r\n")[2].encode()).decode().split("\n"):
            if line.startswith("https://gametrade.jp/signup/complete?email="):
                return line.strip()

class Gametrade:
    def __init__(self, remember_token = None, anticap_key = None):
        self.anticap_key = anticap_key

        self.fake = Faker()
        self.mailbox = MailBox()
        self.session = tls_client.Session(
            client_identifier="safari_ios_16_0",
            random_tls_extension_order=True
        )

        if remember_token != None:
            self.session.cookies.set("remember_token", remember_token)

    def create_account(self):
        nickname = self.fake.user_name()
        email = f"{self.mailbox.name}@developermail.com"
        password = self.fake.password(12, special_chars=False, digits=True, upper_case=False, lower_case=True)

        response = self.session.get("https://gametrade.jp/signup_info")
        soup = BeautifulSoup(response.text, "html.parser")
        token = soup.find("meta", attrs={"name": "csrf-token"}).get("content")
        
        try:
            g_recaptcha_response = self.solve_captcha()
            if g_recaptcha_response == None:
                return None
        except:
            return None
        
        response = self.session.post(
            "https://gametrade.jp/users",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "utf8": "✓",
                "authenticity_token": token,
                "user[nickname]": nickname,
                "user[email]": email,
                "user[password]": password,
                "invited_user[invite_code]": "",
                "g-recaptcha-response": g_recaptcha_response
            }
        )

        remember_token = self.session.cookies.get("remember_token")
        if remember_token == None:
            return None
        
        verify_link = self.mailbox.get_message()
        self.session.get(verify_link)

        return remember_token

    def like_product(self, product_url):
        product_id = product_url.split("/")[-1]

        response = self.session.get(product_url)
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            token = soup.find("meta", attrs={"name": "csrf-token"}).get("content")
        except:
            return False

        response = self.session.post(
            f"https://gametrade.jp/exhibits/{product_id}/thinkings",
            headers={
                "Accept": "*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript",
                "Origin": "https://gametrade.jp",
                "Referer": product_url,
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "X-Csrf-Token": token,
            },
            data={
                "utf8": "✓",
                "button": ""
            }
        )

        if response.status_code == 200:
            return True
        else:
            return False

    def solve_captcha(self):
        solver = recaptchaV2Proxyless()

        solver.set_key(self.anticap_key)
        solver.set_website_url("https://gametrade.jp")
        solver.set_website_key("6Le806QeAAAAAPAPS1HufPdR-c4wvdJcgqif7cFO")

        response = solver.solve_and_return_solution()

        if response == 0:
            return None
        else:
            return response
        
def generate_account():
    print(f"{colorama.Fore.GREEN}「config.yml」をロード中{colorama.Fore.RESET}")
    with open("config.yml", "r", encoding="utf-8", errors="ignore") as file:
        config = yaml.safe_load(file)
    
    many = input(f"{colorama.Fore.YELLOW}生成数:{colorama.Fore.RESET} ")
    if not many.isnumeric():
        print(f"{colorama.Fore.RED}個数の指定が無効です{colorama.Fore.RESET}")
        return

    print(f"{colorama.Fore.GREEN}生成を開始します{colorama.Fore.RESET}")

    remember_tokens = []

    max_loop = int(many)

    for i in range(max_loop):
        current_loop = i + 1

        gametrade = Gametrade(None, config["anticap_key"])
        remember_token = gametrade.create_account()
        if remember_token == None:
            print(f"[{current_loop}/{max_loop}] {colorama.Fore.RED}作成失敗{colorama.Fore.RESET}")
            continue
        print(f"[{current_loop}/{max_loop}] {colorama.Fore.GREEN}作成成功: {colorama.Fore.YELLOW}{remember_token}{colorama.Fore.RESET}")
        remember_tokens.append(remember_token)

    with open("tokens.txt", "w", encoding="utf-8", errors="ignore") as file:
        file.write("{0}".format("\n".join(remember_tokens)))

    print(f"{colorama.Fore.GREEN}生成が完了しました(アカウントは「tokens.txt」に保存されました){colorama.Fore.RESET}")

def like_bomb():
    print(f"{colorama.Fore.GREEN}「tokens.txt」をロード中{colorama.Fore.RESET}")
    with open("tokens.txt", "r", encoding="utf-8", errors="ignore") as file:
        tokens = file.read().splitlines()
    try:
        tokens.remove("")
    except:
        pass

    product_url = input(f"{colorama.Fore.YELLOW}商品URL:{colorama.Fore.RESET} ")
    
    print(f"{colorama.Fore.GREEN}爆を開始します{colorama.Fore.RESET}")

    success = 0
    failed = 0

    for token in tokens:
        gametrade = Gametrade(token, None)
        result = gametrade.like_product(product_url)
        if result:
            success += 1
            print(f"{colorama.Fore.GREEN}成功: {token}{colorama.Fore.RESET}")
        else:
            failed += 1
            print(f"{colorama.Fore.RED}失敗: {token}{colorama.Fore.RESET}")

    print(f"{colorama.Fore.GREEN}爆が完了しました{colorama.Fore.RESET}")
    print(f"{colorama.Fore.GREEN}成功数: {success}{colorama.Fore.RESET}")
    print(f"{colorama.Fore.RED}失敗数: {failed}{colorama.Fore.RESET}")

def main():
    colorama.init(convert=True)

    os.system("cls")

    while True:

        print("=== Select Menu ===")
        print(f"{colorama.Fore.YELLOW}[1]{colorama.Fore.RESET} アカウント生成")
        print(f"{colorama.Fore.YELLOW}[2]{colorama.Fore.RESET} いいね爆")

        select = input("Select: ")
        os.system("cls")

        if select == "1":
            generate_account()
            break
        elif select == "2":
            like_bomb()
            break
        else:
            pass

if __name__ == "__main__":
    main()
    os.system("pause")