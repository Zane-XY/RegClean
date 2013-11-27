from winreg import *

app_names = ["spotify", "evernote", "VLC"]


def detect(text, names=app_names):
    for name in names:
        if text.lower().find(name.lower()) > -1:
            print("found in name list : " + text)
            return True
    return False


def remove_from_uninstall(key, subkey):
    print("deleted : " + subkey)
    DeleteKeyEx(key, subkey)


def clean_key(key):
    sub_key_counts = QueryInfoKey(key)[0]
    for i in range(sub_key_counts):
        try:
            subkey_name = EnumKey(key, i)
            subkey = OpenKey(key, subkey_name)
            display_name = (QueryValueEx(subkey, "DisplayName")[0])
            if "Microsoft" not in display_name:
                print("found app : ", display_name)
                if detect(display_name):
                    remove_from_uninstall(key, subkey_name)
        except FileNotFoundError:
            print("'DisplayName' is not found in " + subkey_name)
        except UnicodeEncodeError:
            print("UnicodeEncodeError for key " + subkey_name)
        except OSError:
            print("already deleted: " + subkey_name)


def user_reg():
    #SID is in HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList
    reg = ConnectRegistry(None, HKEY_USERS)
    return OpenKey(reg, r"S-1-5-21-2380125314-1135609519-1071393968-13754\Software\Microsoft\Windows\CurrentVersion\Uninstall")


def sys_reg():
    reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    return OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")


def sys64_reg():
    reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    return OpenKey(reg, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall")


def clean():
    clean_key(user_reg())
    clean_key(sys_reg())
    clean_key(sys64_reg())


def main():
    clean()


if __name__ == "__main__":
    main()
