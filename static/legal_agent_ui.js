const bootstrap = window.LEGAL_AGENT_BOOTSTRAP || {};

const collectionSelect = document.getElementById("collection");
const documentTitleSelect = document.getElementById("document-title");
const articleNumberInput = document.getElementById("article-number");
const domainSelect = document.getElementById("domain");
const yearSelect = document.getElementById("year");
const languageSelect = document.getElementById("language");
const topKInput = document.getElementById("top-k");
const topKValue = document.getElementById("top-k-value");
const queryInput = document.getElementById("query");
const askButton = document.getElementById("ask-button");
const askForm = document.getElementById("ask-form");
const requestStatus = document.getElementById("request-status");
const conversation = document.getElementById("conversation");
const sources = document.getElementById("sources");
const embeddingBackend = document.getElementById("embedding-backend");
const generationMode = document.getElementById("generation-mode");
const collectionCount = document.getElementById("collection-count");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function parseApiResponse(response) {
  const rawText = await response.text();
  try {
    return { ok: response.ok, status: response.status, data: JSON.parse(rawText) };
  } catch (error) {
    const compact = rawText.trim().slice(0, 220);
    const message = compact.startsWith("<")
      ? "Server returned HTML instead of JSON. Check the Flask terminal for the backend traceback."
      : `Server returned a non-JSON response: ${compact || "empty response"}`;
    return {
      ok: false,
      status: response.status,
      data: { error: message },
    };
  }
}

function populateSelect(selectElement, values, placeholder) {
  const currentValue = selectElement.value;
  selectElement.innerHTML = `<option value="">${placeholder}</option>`;
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    if (currentValue === value) {
      option.selected = true;
    }
    selectElement.appendChild(option);
  });
}

async function loadState() {
  const response = await fetch(`/api/state?collection=${encodeURIComponent(collectionSelect.value)}`);
  const parsed = await parseApiResponse(response);
  const payload = parsed.data;
  if (!parsed.ok) {
    throw new Error(payload.error || "Could not load collection metadata.");
  }
  embeddingBackend.textContent = payload.embedding_backend;
  generationMode.textContent = payload.generation_mode;
  collectionCount.textContent = payload.summary.count;

  populateSelect(documentTitleSelect, payload.summary.titles, "All documents");
  populateSelect(domainSelect, payload.summary.domains, "All");
  populateSelect(languageSelect, payload.summary.languages, "All");
  populateSelect(yearSelect, payload.summary.years.map(String), "All years");
}

function addMessage(kind, label, content) {
  const article = document.createElement("article");
  article.className = `message message-${kind}`;
  article.innerHTML = `
    <div class="message-meta">${escapeHtml(label)}</div>
    <p>${escapeHtml(content)}</p>
  `;
  conversation.appendChild(article);
  conversation.scrollTop = conversation.scrollHeight;
}

function renderSources(items, appliedFilter) {
  if (!items.length) {
    sources.innerHTML = `
      <article class="source-empty">
        <p>No chunks matched this question${appliedFilter && Object.keys(appliedFilter).length ? " with the current filter" : ""}.</p>
      </article>
    `;
    return;
  }

  sources.innerHTML = items
    .map((item) => {
      const metadata = item.metadata || {};
      const metaBits = [
        metadata.document_title,
        metadata.article_number ? `Article ${metadata.article_number}` : "",
        metadata.language,
        metadata.year,
      ].filter(Boolean);
      return `
        <article class="source-card">
          <div class="source-rank">#${item.rank}</div>
          <div class="source-header">
            <h3>${escapeHtml(metadata.document_title || "Untitled chunk")}</h3>
            <span class="source-score">score ${Number(item.score).toFixed(4)}</span>
          </div>
          <p class="source-meta">${escapeHtml(metaBits.join(" · "))}</p>
          <p class="source-preview">${escapeHtml(item.preview)}</p>
          <details class="source-content">
            <summary>Show full chunk</summary>
            <p>${escapeHtml(item.content)}</p>
          </details>
        </article>
      `;
    })
    .join("");
}

async function askAgent(event) {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (!query) {
    requestStatus.textContent = "Enter a question first.";
    return;
  }

  const payload = {
    collection: collectionSelect.value,
    query,
    top_k: Number(topKInput.value),
    document_title: documentTitleSelect.value,
    article_number: articleNumberInput.value.trim(),
    domain: domainSelect.value,
    year: yearSelect.value,
    language: languageSelect.value,
  };

  addMessage("user", "You", query);
  askButton.disabled = true;
  requestStatus.textContent = "Agent is retrieving evidence...";

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const parsed = await parseApiResponse(response);
    const data = parsed.data;
    if (!parsed.ok) {
      throw new Error(data.error || "Request failed.");
    }

    addMessage("agent", "Agent", data.answer);
    renderSources(data.sources || [], data.metadata_filter || {});
    embeddingBackend.textContent = data.embedding_backend;
    generationMode.textContent = data.generation_mode;
    if (data.warning) {
      requestStatus.textContent = data.warning;
    } else {
      requestStatus.textContent = Object.keys(data.metadata_filter || {}).length
        ? `Answered with filter ${JSON.stringify(data.metadata_filter)}.`
        : "Answered from the full collection.";
    }
  } catch (error) {
    addMessage("system", "System", `Request failed: ${error.message}`);
    requestStatus.textContent = "Request failed.";
  } finally {
    askButton.disabled = false;
  }
}

function bindQuestionChips() {
  document.querySelectorAll(".question-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      queryInput.value = chip.dataset.question || "";
      queryInput.focus();
    });
  });
}

topKInput.addEventListener("input", () => {
  topKValue.textContent = topKInput.value;
});

collectionSelect.addEventListener("change", async () => {
  requestStatus.textContent = "Loading collection metadata...";
  await loadState();
  requestStatus.textContent = "Collection ready.";
});

askForm.addEventListener("submit", askAgent);
bindQuestionChips();
topKValue.textContent = topKInput.value;

if (bootstrap.defaultCollection) {
  collectionSelect.value = bootstrap.defaultCollection;
}

loadState().catch(() => {
  requestStatus.textContent = "Could not load collection metadata.";
});
