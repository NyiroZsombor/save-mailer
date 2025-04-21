def get_password():
    import hmac
    import json
    import time
    import getpass
    import hashlib
    import binascii

    with open("config.json") as file:
        config = json.load(file)
 
    hashed = binascii.unhexlify(config["hash"])
    salt = binascii.unhexlify(config["salt"])

    while True:
        user_input = getpass.getpass("password: ")

        if len(user_input) == 16:
            user_input = " ".join([user_input[i * 4:(i + 1) * 4] for i in range(4)])
        if len(user_input) == 20: user_input.replace(user_input[4], " ")

        hashed_input = hashlib.pbkdf2_hmac("sha256", user_input.encode(), salt, 100_000)

        if hmac.compare_digest(hashed_input, hashed):
            print("correct!")
            return user_input
        else:
            time.sleep(3)
            print("incorrect!")

def create_msg(template, config):
    from datetime import datetime
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["From"] = config["email"]
    msg["To"] = config["email"]
    msg["Subject"] = template["subject"]
    msg["X-Date"] = str(datetime.now())
    formatted = template["body"].replace("\\n", "\n").replace("\\t", "\t")
    msg.set_content(formatted)

    return msg

def create_mailbox(mailbox, imap):
    typ, response = imap.create(mailbox)
    if typ == "OK":
        print(f"created mailbox: {mailbox}")
    elif not "[ALREADYEXISTS]" in response[0].decode():
        print(f"failed to create mailbox: {mailbox}")
        print(response)

def handle_mailbox(password, msg, template, config):
    import imaplib
    from datetime import datetime

    with imaplib.IMAP4_SSL("imap.gmail.com") as imap:
        imap.login(config["email"], password)
        epoch_time = datetime.now().timestamp()
        mailbox = f'"Save mailer: {template["name"]}"'

        create_mailbox(mailbox, imap)
        imap.append(mailbox, "", imaplib.Time2Internaldate(epoch_time), msg.as_bytes())

def send_save(template, password=""):
    import os
    import ssl
    import json
    import smtplib
    import mimetypes
    import shutil

    if password == "":
        password = get_password()

    with open(template +".template.json") as file:
        template = json.load(file)

    with open("config.json") as file:
        config = json.load(file)

    path_to_save = os.path.join(template["save_path"], template["save_name"])
    zip_path = template["save_name"] + ".zip"
    msg = create_msg(template, config)
    
    is_folder = os.path.isdir(path_to_save)
    if is_folder:
        shutil.make_archive(template["save_name"], "zip", path_to_save)
        upload_path = zip_path
        filename = zip_path
    else:
        upload_path = path_to_save
        filename = template["save_name"]

    print(filename, upload_path)

    mime_type, mime_subtype = mimetypes.guess_type(filename)[0].split("/")

    with open(upload_path, "rb") as file:
        data = file.read()
        msg.add_attachment(data, maintype=mime_type,
        subtype=mime_subtype, filename=filename)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as smtp:
        smtp.login(config["email"], password)
        smtp.send_message(msg)

    handle_mailbox(password, msg, template, config)
    if is_folder: os.remove(zip_path)

    print("email sent!")

def get_latest_message(mailbox, imap):
    import email
    from email import policy

    imap.select(mailbox)
    typ, msg_ids = imap.search(None, "ALL")
    last_date = ""
    last_msg_id = 0

    if typ != "OK":
        print("error searching emails!")
        print(typ)
        return

    for msg_id in msg_ids[0].split():
        typ, raw = imap.fetch(msg_id, "(RFC822)")
        if typ != "OK":
            print("error fetching email!")
        msg = email.message_from_bytes(raw[0][1], policy=policy.default)

        date = msg.get("X-Date")
        if date > last_date:
            last_date = date
            last_msg_id = msg_id

    return last_msg_id

def load_save(template, password=""):
    import os
    import json
    import email
    import shutil
    import imaplib
    from email import policy

    if password == "":
        password = get_password()

    with open("config.json") as file:
        config = json.load(file)

    with open(template + ".template.json") as file:
        template = json.load(file)

    with imaplib.IMAP4_SSL("imap.gmail.com") as imap:
        imap.login(config["email"], password)

        mailbox = f'"Save mailer: {template["name"]}"'
        last_msg_id = get_latest_message(mailbox, imap)

        typ, raw = imap.fetch(last_msg_id, "(RFC822)")
        msg = email.message_from_bytes(raw[0][1], policy=policy.default)

        for part in msg.iter_attachments():
            filename = part.get_filename()
            is_zip = filename.endswith(".zip")
            unzip = filename.removesuffix(".zip")
            save_path = os.path.join(template["save_path"], unzip)

            if is_zip:
                if unzip == template["save_name"]:
                    with open(filename, "wb") as file:
                        file.write(part.get_payload(decode=True))

                shutil.unpack_archive(filename, save_path)
                os.remove(filename)
            else:
                if filename == template["save_name"]:
                    with open(save_path, "wb") as file:
                        file.write(part.get_payload(decode=True))

            print(f"saved {unzip}")

