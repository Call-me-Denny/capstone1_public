# RealTime STT with MOM

## 설명 
Agora Web SDK와 Django를 이용한 화상회의
FasterWhisper를 활용한 실시간 음성 처리기능
ChatGPT API를 활용한 MOM 작성 자동화

##  사용방법

#### 1 - Clone repo
```
git clone https://github.com/Call-me-Denny/capstone1.git
```

#### 2 - Install requirements
```
cd capstone1
pip install -r requirements.txt
```

#### 3 - Update Agora credentals
해당 프로젝트를 사용하기 위해서는 AgoraSDK의 key를 수정해야합니다.

###### views.py
```
def getToken(request):
    appId = "YOUR APP ID"
    appCertificate = "YOUR APPS CERTIFICATE"
    ......
```

###### streams.js
```
....
const APP_ID = 'YOUR APP ID'
....
```


#### 4 - Start server
```
python manage.py runserver
```


