from ProfileInstance import ProfileInstance


class PostContol:

    def loadProfile(self,data):
        profileInstance = ProfileInstance.getInstance()
        profileInstance.zoneProfiles.update(data)
        return "{'result':'success'}"