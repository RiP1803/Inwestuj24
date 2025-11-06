fetch("news.json")
  .then(response => response.json())
  .then(data => {
    const container = document.getElementById("news-container");
    const articles = data.articles.slice(0, 20);

    function render(category) {
      container.innerHTML = "";
      let filtered = category === "all" ? articles :
        articles.filter(a => a.source.toLowerCase().includes(category));
      filtered.forEach(a => {
        const div = document.createElement("div");
        div.className = "article";
        div.innerHTML = `
          <h2>${a.title}</h2>
          <p>${a.summary}</p>
          <a href="${a.link}" target="_blank">Czytaj więcej →</a>
          <p><small>${a.source}</small></p>
        `;
        container.appendChild(div);
      });
    }

    document.querySelectorAll("nav a").forEach(a => {
      a.addEventListener("click", e => {
        e.preventDefault();
        render(a.dataset.category);
      });
    });

    render("all");
  })
  .catch(err => {
    document.getElementById("news-container").innerHTML = "<p>Błąd ładowania danych.</p>";
  });
