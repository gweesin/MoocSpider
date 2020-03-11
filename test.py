import re

string = """
//#DWR-INSERT
//#DWR-REPLY
dwr.engine._remoteHandleException('1583819197813','0',{javaClassName:"com.netease.edu.commons.exceptions.FrontNotifiableRuntimeException",message:"not_auth"});
"""

res = re.search('not_auth', string)
print(res)