let recognition;
let isRecording = false;

export function enableSpeechToText() {
  const recordBtn = document.getElementById('chat-record');
  const input = document.getElementById('chat-input');

  if (!window.webkitSpeechRecognition) {
    console.warn("🎙️ SpeechRecognition desteklenmiyor.");
    recordBtn.disabled = true;
    return;
  }

  recognition = new webkitSpeechRecognition();
  recognition.lang = 'tr-TR';
  recognition.interimResults = false;
  recognition.continuous = true; // 🔥 durdurulana kadar

  recordBtn.addEventListener('click', () => {
    if (!isRecording) {
      startRecording(recordBtn, input);
    } else {
      stopRecording(recordBtn);
    }
  });

  recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map(result => result[0].transcript)
      .join('');

    input.value = transcript;
  };

  recognition.onerror = (e) => {
    console.error('🎙️ Ses hatası:', e);
    stopRecording(recordBtn);
  };

  recognition.onend = () => {
    if (isRecording) stopRecording(recordBtn);
  };
}

function startRecording(btn, input) {
  try {
    recognition.start();
    isRecording = true;
    btn.classList.add('recording');
  } catch (err) {
    console.error("🎙️ Kayıt başlatılamadı:", err);
  }
}

function stopRecording(btn) {
  recognition.stop();
  isRecording = false;
  btn.classList.remove('recording');
}