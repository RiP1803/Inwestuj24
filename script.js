
const newsUrl = './news.json';

async function loadNews(){
  try{
    const res = await fetch(newsUrl + '?_=' + Date.now());
    if(!res.ok) throw new Error('Cannot fetch news.json');
    const data = await res.json();
    renderNews(data.articles || []);
    renderSources(data.articles || []);
  }catch(e){
    document.getElementById('news-list').innerHTML = '<div class="card">Błąd ładowania wiadomości.</div>';
    console.error(e);
  }
}

function renderNews(articles){
  const container = document.getElementById('news-list');
  container.innerHTML = '';
  if(!articles.length){ container.innerHTML = '<div class="card">Brak dostępnych artykułów.</div>'; return; }
  articles.slice(0,20).forEach(a => {
    const el = document.createElement('article');
    el.className = 'article card';
    const pub = a.published ? new Date(a.published).toLocaleString('pl-PL') : '';
    el.innerHTML = `
      <h2><a href="${a.link}" target="_blank" rel="noopener noreferrer">${escapeHtml(a.title)}</a></h2>
      <div class="meta">${escapeHtml(a.source)} • ${pub}</div>
      <div class="excerpt">${escapeHtml(a.summary || '')}</div>
      <a class="read-btn" href="${a.link}" target="_blank" rel="noopener noreferrer">Czytaj więcej</a>
    `;
    container.appendChild(el);
  });
}

function renderSources(articles){
  const ul = document.getElementById('sources');
  const sources = Array.from(new Set(articles.map(a=>a.source))).slice(0,50);
  ul.innerHTML = sources.map(s=>`<li>${escapeHtml(s)}</li>`).join('\n');
}

function escapeHtml(text){ if(!text) return ''; return text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'); }

loadNews();
