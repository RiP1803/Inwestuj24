const newsUrl = './news.json';

async function loadNews(){
  try{
    const res = await fetch(newsUrl + '?_=' + Date.now());
    const data = await res.json();
    renderNews(data);
    renderSources(data);
  }catch(e){
    document.getElementById('news-list').innerHTML = '<div class="card">Błąd ładowania wiadomości.</div>'
    console.error(e)
  }
}

function renderNews(data){
  const container = document.getElementById('news-list');
  container.innerHTML = '';
  const articles = data.articles || [];

  articles.forEach(a => {
    const el = document.createElement('article');
    el.className = 'card article';
    el.innerHTML = `
      <div style="flex:1">
        <h2><a href="${a.link}" target="_blank" rel="noopener">${a.title}</a></h2>
        <div class="meta">${a.source} • ${new Date(a.published).toLocaleString('pl-PL')}</div>
        <div class="excerpt">${a.summary || ''}</div>
      </div>
    `;
    container.appendChild(el);
  })
}

function renderSources(data){
  const ul = document.getElementById('sources');
  const sources = Array.from(new Set((data.articles||[]).map(a=>a.source))).slice(0,50);
  ul.innerHTML = sources.map(s=>`<li>${s}</li>`).join('\n');
}

async function loadStats(){
  document.getElementById('sp500').textContent = '—';
  document.getElementById('wig20').textContent = '—';
  document.getElementById('btc').textContent = '—';
}

loadNews();
loadStats();

document.getElementById('search').addEventListener('input', e => {
  const q = e.target.value.toLowerCase();
  const cards = [...document.querySelectorAll('#news-list .article')];
  cards.forEach(c => {
    const text = c.innerText.toLowerCase();
    c.style.display = text.includes(q) ? '' : 'none';
  })
});

document.getElementById('filter').addEventListener('change', e => {
  const v = e.target.value;
  const cards = [...document.querySelectorAll('#news-list .article')];
  cards.forEach(c => {
    if(v==='all'){ c.style.display=''; return }
    const meta = c.querySelector('.meta').innerText.toLowerCase();
    c.style.display = meta.includes(v) ? '' : 'none';
  })
});