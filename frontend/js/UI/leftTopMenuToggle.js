export function bindMenuToggle() {
    const toggleBtn = document.getElementById('menu-toggle');
    const menuBox = document.getElementById('menu-buttons');
  
    if (!toggleBtn || !menuBox) return;
  
    toggleBtn.addEventListener('click', () => {
      menuBox.classList.toggle('active');
    });
  }