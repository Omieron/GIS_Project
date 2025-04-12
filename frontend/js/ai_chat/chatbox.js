import { enableSpeechToText } from './speechToText.js';

export function adjustAi() {
  initChatBox();
  enableChatboxPin();
  enableSpeechToText();
}

function initChatBox() {
  const input = document.getElementById('chat-input');
  const sendBtn = document.getElementById('chat-send');
  const messages = document.getElementById('chat-messages');

  if (!input || !sendBtn || !messages) {
    console.warn("🛑 Chatbox elemanları bulunamadı.");
    return;
  }

  // Gönder butonuna tıklama
  sendBtn.addEventListener('click', () => {
    sendUserMessage();
  });

  // Enter tuşuna basıldığında da mesaj gönder
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // form submit varsa engelle
      sendBtn.click();
    }
  });

  function sendUserMessage() {
    const text = input.value.trim();
    if (text === '') return;

    appendMessage('user', text);
    input.value = '';

    setTimeout(() => {
      const reply = generateMockResponse(text);
      appendMessage('ai', reply);
    }, 800);
  }

  function appendMessage(role, text) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chatbox-message ${role}`;
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  function generateMockResponse(userInput) {
    return `Ben bir AI'im ve şunu anladım: "${userInput}"`;
  }
}

function enableChatboxPin() {
  const wrapper = document.getElementById('chatbox-wrapper');
  const pinButton = document.getElementById('pin-toggle');

  if (!wrapper || !pinButton) return;

  pinButton.addEventListener('click', () => {
    wrapper.classList.toggle('pinned');
    pinButton.textContent = wrapper.classList.contains('pinned') ? '📍' : '📌';
  });
}