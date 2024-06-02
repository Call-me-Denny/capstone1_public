from django.shortcuts import render
from django.http import JsonResponse
import random
import time
from agora_token_builder import RtcTokenBuilder
from .models import RoomMember
import json
from django.views.decorators.csrf import csrf_exempt



# Create your views here.

def lobby(request):
    return render(request, 'base/lobby.html')

def room(request):
    return render(request, 'base/room.html')


def getToken(request):
    appId = "YOUR APP ID"
    appCertificate = "YOUR APP CERTIFICATE"
    channelName = request.GET.get('channel')
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)

    return JsonResponse({'token': token, 'uid': uid}, safe=False)


@csrf_exempt
def createMember(request):
    data = json.loads(request.body)
    member, created = RoomMember.objects.get_or_create(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )

    return JsonResponse({'name':data['name']}, safe=False)


def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')

    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )
    name = member.name
    return JsonResponse({'name':member.name}, safe=False)

@csrf_exempt
def deleteMember(request):
    data = json.loads(request.body)
    member = RoomMember.objects.get(
        name=data['name'],
        uid=data['UID'],
        room_name=data['room_name']
    )
    member.delete()
    return JsonResponse('Member deleted', safe=False)


import os
from django.conf import settings
from faster_whisper import WhisperModel
import os
from datetime import datetime
from queue import Queue
import io
import wave,pyaudio

os.environ['KMP_DUPLICATE_LIB_OK']='True'
model_size = "large-v3"
model = WhisperModel(model_size, device="cuda", compute_type="float16")

"""1초 append모델"""
import re
last_mention = {}
file_idx={}
@csrf_exempt
def upload_audio(request):
    global last_mention
    global file_idx
    if request.method == 'POST' and 'audio' in request.FILES:
        audio_file = request.FILES['audio']
        original_filename = audio_file.name
        username = original_filename.split('_')[1].split('.')[0]  # 파일 이름에서 사용자 이름 추출
        if username not in file_idx:
            file_idx[username]=0
        filename = f'recording_{username}_{file_idx[username]}.wav'  #정석은 webm인듯
        save_path = os.path.join(settings.MEDIA_ROOT, 'recordings', filename)
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))

        with open(save_path, 'ab+') as destination:
            for chunk in audio_file.chunks(): #chunk들을 write, chunk byte
                destination.write(chunk)
         
        segments, info = model.transcribe(save_path, beam_size=1, language='ko', vad_filter=True)
        transcribed_message = "".join([segment.text for segment in segments]).strip()

        timestamp = int(time.time())
        time_formatted = time.strftime("%H:%M:%S", time.localtime(timestamp))
        record_file_path = "record.txt"
        if transcribed_message!="": #wav파일 분석해봐
            if username in last_mention: #이전에 말한게 있어?
                if (last_mention[username] == transcribed_message ): #이전에 말한거랑 지금 분석한거랑 동일하면 => 아 얘가 말이 끝났구나
                    with open(record_file_path, "a") as file:
                        file.write(f"[{time_formatted}] {username} : {transcribed_message}\n")
                    del last_mention[username]
                    if os.path.exists(save_path):
                        os.remove(save_path)
                        file_idx[username]+=1
                else: #동일하지 않다면 => 계속 말하고 있는 중이구나
                    last_mention[username] = transcribed_message
            else: #이전에 말한게 없다면 => 이제 말을 시작하는 구나
                last_mention[username] = transcribed_message

    return JsonResponse({'message': f"[{time_formatted}] {username} : {transcribed_message}\n" if transcribed_message else 'No transcribed message'}, status=200)

