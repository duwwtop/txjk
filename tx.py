import json
import time
import requests
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.lighthouse.v20200324 import lighthouse_client, models
try:
    #【配置（替换引号内容）】
    #腾讯云配置，建议使用子账户！详见https://console.cloud.tencent.com/cam/capi
    SecretId=""
    SecretKey=""
    #地域，默认香港，详见https://cloud.tencent.com/document/api/1207/47564#.E5.9C.B0.E5.9F.9F.E5.88.97.E8.A1.A8
    region="ap-hongkong"
    #流量限制百分比 90%
    percent= 0.9
    
    #-------------------
    #推送配置：默认使用Bot推送实例状态，使用Bot推送流量超警/恢复消息。
    #--------------------   
    
    #MSG酱推送，请在引号内填入你的SendToken，详见https://msg.2525.in
    Sendtoken=""
    Sendqq=""
    #【配置部分结束】




    #-------------------
    cred = credential.Credential(SecretId,SecretKey)
    httpProfile = HttpProfile()
    httpProfile.endpoint = "lighthouse.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = lighthouse_client.LighthouseClient(cred, region, clientProfile)
    #获取实例列表
    req_instances = models.DescribeInstancesRequest()
    params = {
    
    }
    req_instances.from_json_string(json.dumps(params))
    resp_instances = client.DescribeInstances(req_instances) 
    s1=json.loads(resp_instances.to_json_string())['InstanceSet']
    for j in range (len(s1)):
        params.setdefault("InstanceIds",[]).append(s1[j]['InstanceId'])#获取实例ID        
    
    #获取实例流量
    req = models.DescribeInstancesTrafficPackagesRequest()
    req.from_json_string(json.dumps(params))  
    resp = client.DescribeInstancesTrafficPackages(req)
    s2=json.loads(resp.to_json_string())["InstanceTrafficPackageSet"]
    GB=1024*1024*1024
    for i in range (len(s2)):
        InstanceId= s2[i]['InstanceId']
        s3= s2[i]['TrafficPackageSet'][0]
        InstanceState =s1[i]["InstanceState"]
        TrafficPackageTotal = round(s3['TrafficPackageTotal']/GB,2)
        TrafficUsed = round(s3['TrafficUsed']/GB,2)
        TrafficPackageRemaining=str(round(s3['TrafficPackageRemaining']/GB,2))  

        #推送实例状态
        msg= "实例ID：" + InstanceId + '\n' + "实例状态：" + InstanceState + '\n' + "总流量：" + str(TrafficPackageTotal) + "GB" + '\n' + "已使用：" + str(TrafficUsed) + "GB" + '\n' + "剩余：" + TrafficPackageRemaining + "GB"
        Server_Push= "https://msg.2525.in/send/?msgqq=753658584&type=1&token=" + Sendtoken + "&toqq=" + Sendqq + "&text=" + msg
        requests.get(url=Server_Push).text
        print(msg)

        if (TrafficUsed/TrafficPackageTotal<percent):                 
            if (InstanceState == "RUNNING"):
                print("一切正常")
            else:
                req_Start = models.StartInstancesRequest()
                params_Start = {

                }
                params_Start.setdefault("InstanceIds",[]).append(InstanceId)
                req_Start.from_json_string(json.dumps(params_Start))
                resp_Start = client.StartInstances(req_Start)
                #推送开机结果 
                RequestId_1= resp_Start.to_json_string()
                msg_1= "流量充足，尝试开机" + '\n' + "实例ID：" + InstanceId + '\n' + "总流量：" + str(TrafficPackageTotal) + "GB" + '\n' + "已使用：" + str(TrafficUsed) + "GB" + '\n' + "剩余：" + TrafficPackageRemaining + "GB" + '\n' + "RequestId：" + RequestId_1
                Server_Push_1= "https://msg.2525.in/send/?msgqq=753658584&type=1&token=" + Sendtoken + "&toqq=" + Sendqq + "&text=" + msg_1
                requests.get(url=Server_Push_1).text
                print(msg_1)               
        else:
            if (InstanceState == "RUNNING"):
                print(InstanceId,":","流量超出限制，自动关闭")
                req_Stop = models.StopInstancesRequest()
                params_Stop = {

                }
                params_Stop.setdefault("InstanceIds",[]).append(InstanceId)
                req_Stop.from_json_string(json.dumps(params_Stop))
                resp_Stop = client.StopInstances(req_Stop) 
                print(resp_Stop.to_json_string())
                #推送关机结果 
                RequestId_2= resp_Stop.to_json_string()
                msg_2= "流量超出限制，自动关闭" + '\n' + "实例名称：" + InstanceId + '\n' + "总流量：" + str(TrafficPackageTotal) + "GB" + '\n' + "已使用：" + str(TrafficUsed) + "GB" + '\n' + "剩余：" + TrafficPackageRemaining + "GB" + '\n' + "RequestId：" + RequestId_2
                Server_Push_2= "https://msg.2525.in/send/?msgqq=753658584&type=1&token=" + Sendtoken + "&toqq=" + Sendqq + "&text=" + msg_2
                requests.get(url=Server_Push_2).text
                print(msg_2)               
            else:
                print("已关机")
        
        #添加时间戳
        print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print ("--------------------")
except TencentCloudSDKException as err: 
    print(err) 
