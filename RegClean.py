import os
from winreg import *

app_names = ["spotify", "evernote", "grepWin", "Bonjour", "bing",
            "Google Talk Plugin", "Royal TS", "Wget", "Tar",
            "Apple Software Update", "7-Zip", "Vim", "WinSCP",
            "iTunes", "Sublime Text", "ONAIR", "LINE", "VLC", "CMB",
            "Alipay", "bullzip", "dropbox", "google drive", "IntelliJ",
            "CopyQ", "sharpkeys", "cmake","markdownpad 2"]


username = os.getenv("USERNAME")

def removeFromUninstall(key_h, subkey_name):
    DeleteKeyEx(key_h, subkey_name)
    print("deleted : " + subkey_name)


# takes a ken handle and  apply an operation function to all keys
def loop_keys(key_h, op):
    r = []
    sub_keys_num = QueryInfoKey(key_h)[0]
    for i in range(sub_keys_num):
        try:
            subkey_name = EnumKey(key_h,i) # used by some operations like delete
            subkey_h = OpenKey(key_h, subkey_name)
            op(key_h, subkey_h, subkey_name)
        except Exception as e:
            #print(e)
            pass
    return r

# take a key and predicate returns a list of subkey names
def filter_sub_key_names(key_h, pre):
    r = []
    sub_keys_num = QueryInfoKey(key_h)[0]
    for i in range(sub_keys_num):
        try:
            subkey_name = EnumKey(key_h,i)
            subkey_h = OpenKey(key_h, subkey_name)
            if pre(subkey_h):
                r.append(subkey_name)
        except Exception as e:
            #print(e)
            pass
    return r


# SID is in HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\WindowsNT\CurrentVersion\ProfileList
def user_reg():
    HKLM_h = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    profile_key_h = OpenKeyEx(HKLM_h, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList")

    SID = filter_sub_key_names(profile_key_h, SID_filter)[0]
    user_reg_h = ConnectRegistry(None, HKEY_USERS)
    return OpenKey(user_reg_h, SID + r"\Software\Microsoft\Windows\CurrentVersion\Uninstall")


def sys_reg():
    reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    return OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")


def sys64_reg():
    reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    return OpenKey(reg, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall")


def dirty_app(app_name, names=app_names):
    if "Microsoft" not in app_name and "Windows Driver" not in app_name:
        for name in names:
            if app_name.lower().find(name.lower()) > -1:
                print("found in name list : " + app_name)
                return True
    else:
        return False

# sid predicate
def SID_filter(key_h):
    profilePath = ''
    try:
        profilePath = QueryValueEx(key_h, "ProfileImagePath")[0]
    except Exception:
        pass
    return True if username in profilePath else False


def clean_key(parent_key_h, key_h, key_name):
    try:
        display_name = QueryValueEx(key_h, "DisplayName")[0]
        #print("found app : ", display_name)
        if dirty_app(display_name):
           removeFromUninstall(parent_key_h, key_name)
    except Exception as e:
        #print(e)
        pass

def clean(reg_h):
    loop_keys(reg_h, clean_key)


def main():
    clean(user_reg())
    clean(sys_reg())
    clean(sys64_reg())


if __name__ == "__main__":
    main()
