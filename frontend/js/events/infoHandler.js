export function renderBuildingStats(features) {
    const counts = {};
  
    features.forEach(f => {
      const kat = f.properties?.ZEMINUSTUKATSAYISI ?? 0;
      const key = `${kat} kat`;
      counts[key] = (counts[key] || 0) + 1;
    });
  
    const list = document.getElementById('kat-istatistik');
    list.innerHTML = '';
  
    Object.entries(counts).sort((a, b) => parseInt(a[0]) - parseInt(b[0])).forEach(([kat, sayi]) => {
      const li = document.createElement('li');
      li.textContent = `${kat}: ${sayi} bina`;
      list.appendChild(li);
    });
  }