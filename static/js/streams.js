const APP_ID = 'YOUR APP ID';
const TOKEN = sessionStorage.getItem('token');
const CHANNEL = sessionStorage.getItem('room');
let UID = sessionStorage.getItem('UID');
let NAME = sessionStorage.getItem('name');

const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });

let localTracks = [];
let remoteUsers = {};

let recordingInterval;
let isMicMuted = false;
const joinAndDisplayLocalStream = async () => {
    document.getElementById('room-name').innerText = CHANNEL;

    client.on('user-published', handleUserJoined);
    client.on('user-left', handleUserLeft);

    try {
        UID = await client.join(APP_ID, CHANNEL, TOKEN, UID);
    } catch (error) {
        console.error(error);
        window.open('/', '_self');
    }

    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();

    let member = await createMember();

    let player = `<div class="video-container" id="user-container-${UID}">
                     <div class="video-player" id="user-${UID}"></div>
                     <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                  </div>`;

    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
    localTracks[1].play(`user-${UID}`);
    await client.publish([localTracks[0], localTracks[1]]);
}

const handleUserJoined = async (user, mediaType) => {
    remoteUsers[user.uid] = user;
    await client.subscribe(user, mediaType);
    if (mediaType === 'video') {
        let player = document.getElementById(`user-container-${user.uid}`);
        if (player != null) {
            player.remove();
        }

        let member = await getMember(user);

        player = `<div class="video-container" id="user-container-${user.uid}">
            <div class="video-player" id="user-${user.uid}"></div>
            <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
        </div>`;

        document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
        user.videoTrack.play(`user-${user.uid}`);
    }

    if (mediaType === 'audio') {
        user.audioTrack.play();
    }
}

const handleUserLeft = async (user) => {
    delete remoteUsers[user.uid];
    document.getElementById(`user-container-${user.uid}`).remove();
}

const leaveAndRemoveLocalStream = async () => {
    clearInterval(recordingInterval); 

    for (let i = 0; i < localTracks.length; i++) {
        localTracks[i].stop();
        localTracks[i].close();
    }

    await client.leave();
    deleteMember();
    window.open('/', '_self');
}

const toggleCamera = async (e) => {
    console.log('TOGGLE CAMERA TRIGGERED');
    if (localTracks[1].muted) {
        await localTracks[1].setMuted(false);
        e.target.style.backgroundColor = '#fff';
    } else {
        await localTracks[1].setMuted(true);
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)';
    }
}

const toggleMic = async (e) => {
    console.log('TOGGLE MIC TRIGGERED');
    if (localTracks[0].muted) {
        await localTracks[0].setMuted(false);
        e.target.style.backgroundColor = '#fff';
        isMicMuted = false; 
    } else {
        await localTracks[0].setMuted(true);
        e.target.style.backgroundColor = 'rgb(255, 80, 80, 1)';
        isMicMuted = true; 
    }
}


const createMember = async () => {
    let response = await fetch('/create_member/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'name': NAME, 'room_name': CHANNEL, 'UID': UID })
    });
    let member = await response.json();
    return member;
}

const getMember = async (user) => {
    let response = await fetch(`/get_member/?UID=${user.uid}&room_name=${CHANNEL}`);
    let member = await response.json();
    return member;
}

const deleteMember = async () => {
    let response = await fetch('/delete_member/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'name': NAME, 'room_name': CHANNEL, 'UID': UID })
    });
    let member = await response.json();
}
/* 1초씩 append 방식*/
function startRecordingInterval() {
    recordingInterval = setInterval(startRecording, 1000); 
}

const startRecording = () => {
    if (isMicMuted) {
        console.log('Microphone is muted, recording is skipped.');
        return; 
    }
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {   
            const mediaRecorder = new MediaRecorder(stream);
            let audioChunks = [];

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener("stop", () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio', audioBlob, `recording_${NAME}.wav`);
 

                fetch('https://quail-relative-noticeably.ngrok-free.app/upload-audio/', {
                    method: 'POST',
                    body: formData,
                })
                .then(response => response.text())
                .then(text => {
                    console.log('Server response:', text);
                })
                .catch(error => {
                    console.error('Error uploading audio:', error);
                });
            });

            mediaRecorder.start();
            setTimeout(() => {
                mediaRecorder.stop();
            }, 1000);  
        })
        .catch(error => {
            console.error('Error accessing microphone:', error);
        });
}


// 페이지 로드 시 녹음 시작
window.onload = () => {
    joinAndDisplayLocalStream();
    startRecordingInterval(); 
}

window.addEventListener("beforeunload", deleteMember);

document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream);
document.getElementById('camera-btn').addEventListener('click', toggleCamera);
document.getElementById('mic-btn').addEventListener('click', toggleMic);