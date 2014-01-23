import os
from winreg import *

appNames = ["spotify", "evernote", "VLC"]


username = os.getenv("USERNAME")


def detect(text, names=appNames):
    for name in names:
        if text.lower().find(name.lower()) > -1:
            print("found in name list : " + text)
            return True
    return False


def removeFromUninstall(key, subkey):
    print("deleted : " + subkey)
    DeleteKeyEx(key, subkey)


# takes a predicate function op
def loopKeys(key, op):
    subKeyCounts = QueryInfoKey(key)[0]
    for i in range(subKeyCounts):
        try:
            subkeyName = EnumKey(key, i)
            subkey = OpenKey(key, subkeyName)
            if op(subkey, subkeyName):
                return (subkey, subkeyName)
            #print(subkey)
        #except FileNotFoundError:
            #print("'DisplayName' is not found in " + subkeyName)
        except UnicodeEncodeError:
            print("UnicodeEncodeError for key " + subkeyName)
        except OSError:
            print("already deleted: " + subkeyName)


def userReg():
    #SID is in HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList
    reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    profileKey = OpenKey(reg, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList")
    sidKey = loopKeys(profileKey, lambda k, n: filterSID(k, n))
    userKey = ConnectRegistry(None, HKEY_USERS)
    return OpenKey(userKey, str(sidKey[1]) + r"\Software\Microsoft\Windows\CurrentVersion\Uninstall")


def sysReg():
    reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    return OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")


def sys64Reg():
    reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    return OpenKey(reg, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall")


def clean(reg):
    loopKeys(reg, lambda x, y: cleanKey(x, y))


# sid predicate
def filterSID(subkey, subkeyName):
    try:
        profilePath = (QueryValueEx(subkey, "ProfileImagePath")[0])
        if username in profilePath:
            return True
        else:
            return False
    except FileNotFoundError:
        #print("'ProfileImagePath' is not found in " + subkeyName)
        pass


def cleanKey(subkey, subkeyName):
    try:
        displayName = (QueryValueEx(subkey, "DisplayName")[0])
        if "Microsoft" not in displayName and "Windows Driver" not in displayName:
            print("found app : ", displayName)
            if detect(displayName):
                removeFromUninstall(key, subkeyName)
        return False
    except FileNotFoundError:
        #print("'DisplayName' is not found in " + subkeyName)
        pass


def main():
    clean(userReg())
    clean(sysReg())
    clean(sys64Reg())


if __name__ == "__main__":
    main()
