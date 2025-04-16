let recognition;
let isRecording = false;

// Türkçe kelimelerde sık yapılan hataları düzeltmek için eşleştirme listesi
const turkishCorrections = {
  'max': 'maks',
  'fix': 'fiks',
  // Daha fazla kelime ekleyebilirsiniz
};

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
    let transcript = Array.from(event.results)
      .map(result => result[0].transcript)
      .join('');
    
    // Metni düzeltme işlemi
    transcript = correctTurkishText(transcript);
    
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

/**
 * Tanınan metindeki hatalı kelimeleri düzeltir
 * @param {string} text - Speech to text'ten gelen metin
 * @return {string} - Düzeltilmiş metin
 */
function correctTurkishText(text) {
  // Kelime kelime kontrol edelim
  let words = text.split(' ');
  
  for (let i = 0; i < words.length; i++) {
    const lowerWord = words[i].toLowerCase();
    
    // Kelime düzeltme listesinde var mı kontrol edelim
    if (turkishCorrections[lowerWord]) {
      // Büyük harfle başlıyorsa düzeltilmiş kelimeyi de büyük harfle başlatalım
      if (words[i][0] === words[i][0].toUpperCase()) {
        const corrected = turkishCorrections[lowerWord];
        words[i] = corrected.charAt(0).toUpperCase() + corrected.slice(1);
      } else {
        words[i] = turkishCorrections[lowerWord];
      }
    }
  }
  
  return words.join(' ');
}

// İsteğe bağlı: Kullanıcının kendi düzeltmelerini ekleyebileceği bir fonksiyon
export function addCustomCorrection(wrongWord, correctWord) {
  turkishCorrections[wrongWord.toLowerCase()] = correctWord.toLowerCase();
  console.log(`Düzeltme eklendi: "${wrongWord}" -> "${correctWord}"`);
}