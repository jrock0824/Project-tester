let isTyping = false;
let currentPersona = "professional";

function adjustHeight(textarea) {
  textarea.style.height = "auto";
  textarea.style.height = Math.min(textarea.scrollHeight, 100) + "px";
}

function updateSendButton() {
  const input = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  sendBtn.disabled = !input.value.trim() || isTyping;
}

function handleKeyDown(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage(event);
  }
}

function toggleSidebar() {
  const sidebar = document.querySelector(".sidebar");
  sidebar.classList.toggle("collapsed");
}

function togglePersonaDropdown(event) {
  event.stopPropagation();
  const selector = document.getElementById("personaSelector");
  selector.classList.toggle("open");
}

function selectPersona(persona) {
  currentPersona = persona;

  const personas = {
    professional: {
      name: "Professional",
      description: "Clear and structured guidance with expert advice",
      icon: `<svg class="persona-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #2196f3;"><path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/></svg>`,
    },
    friendly: {
      name: "Friendly",
      description: "Warm and conversational, like talking to a trusted friend",
      icon: `<svg class="persona-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #4caf50;"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/></svg>`,
    },
    humorous: {
      name: "Humorous",
      description: "Gentle humor to help ease tension and stress",
      icon: `<svg class="persona-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #ff9800;"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/><path d="M7 17c0-2.5 1.5-5 5-5s5 2.5 5 5"/></svg>`,
    },
  };

  const selected = personas[persona];
  const button = document.getElementById("personaButton");

  // Force update the button content
  const iconElement = button.querySelector(".persona-icon");
  const nameElement = button.querySelector(".persona-name");
  const descElement = button.querySelector(".persona-description");

  if (iconElement && nameElement && descElement) {
    iconElement.outerHTML = selected.icon;
    nameElement.textContent = selected.name;
    descElement.textContent = selected.description;

    // Force a re-render
    button.style.display = "none";
    button.offsetHeight; // Trigger reflow
    button.style.display = "flex";
  }

  document.getElementById("personaSelector").classList.remove("open");
}

// Close persona dropdown when clicking outside
document.addEventListener("click", function () {
  document.getElementById("personaSelector").classList.remove("open");
});

async function sendMessage(event) {
  if (event) event.preventDefault();

  const input = document.getElementById("messageInput");
  const message = input.value.trim();

  if (!message || isTyping) return false;

  // Add user message
  addMessage(message, "user");

  // Clear input
  input.value = "";
  adjustHeight(input);
  updateSendButton();

  // Show typing
  showTyping();

  try {
    const response = await fetch(
      `/ask?question=${encodeURIComponent(message)}&persona=${currentPersona}`,
    );
    const data = await response.json();

    hideTyping();

    if (data.error) {
      addMessage("Sorry, I encountered an error: " + data.error, "ai");
    } else {
      addMessage(data.answer, "ai");
    }
  } catch (error) {
    hideTyping();
    addMessage(
      "Sorry, I am having trouble connecting right now. Please try again.",
      "ai",
    );
  }

  return false;
}

function addMessage(content, sender) {
  const container = document.getElementById("messages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${sender}`;

  const avatar = sender === "user" ? "👤" : "🤖";
  const bubbleClass = sender === "user" ? "user-bubble" : "ai-bubble";
  let avatarClass = sender === "user" ? "user-avatar" : "ai-avatar";

  // Add persona-specific styling for AI avatar
  if (sender === "ai") {
    if (currentPersona === "friendly") {
      avatarClass += " friendly-persona";
    } else if (currentPersona === "humorous") {
      avatarClass += " humorous-persona";
    }
  }

  let formattedContent = content;
  if (sender === "ai") {
    formattedContent = formatMarkdown(content);
  } else {
    formattedContent = `<p>${escapeHtml(content)}</p>`;
  }

  messageDiv.innerHTML = `
        <div class="message-avatar ${avatarClass}">${avatar}</div>
        <div class="message-bubble ${bubbleClass}">
            ${formattedContent}
        </div>
    `;

  container.appendChild(messageDiv);
  container.scrollTop = container.scrollHeight;
}

function formatMarkdown(text) {
  let html = text;

  // Remove code blocks and markdown artifacts
  html = html.replace(/```[\s\S]*?```/g, "");

  // Handle markdown headers (including ####)
  html = html.replace(/^#### (.*$)/gm, "<h4><strong>$1</strong></h4>");
  html = html.replace(/^### (.*$)/gm, "<h3><strong>$1</strong></h3>");
  html = html.replace(/^## (.*$)/gm, "<h2><strong>$1</strong></h2>");
  html = html.replace(/^# (.*$)/gm, "<h1><strong>$1</strong></h1>");

  // Handle headers with underlines
  html = html.replace(/^(.+)\n=+\s*$/gm, "<h2><strong>$1</strong></h2>");
  html = html.replace(/^(.+)\n-+\s*$/gm, "<h3><strong>$1</strong></h3>");

  // Bold and italic
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");

  // Handle numbered lists first
  html = html.replace(/^(\d+)\. (.+)$/gm, '<li class="numbered">$2</li>');

  // Handle bullet points
  html = html.replace(/^\* (.+)$/gm, '<li class="bullet">$1</li>');
  html = html.replace(/^- (.+)$/gm, '<li class="bullet">$1</li>');

  // Wrap consecutive numbered items in ol
  html = html.replace(
    /((<li class="numbered">[^<]*<\/li>\s*)+)/g,
    "<ol>$1</ol>",
  );
  html = html.replace(/<li class="numbered">/g, "<li>");

  // Wrap consecutive bullet items in ul
  html = html.replace(/((<li class="bullet">[^<]*<\/li>\s*)+)/g, "<ul>$1</ul>");
  html = html.replace(/<li class="bullet">/g, "<li>");

  // Clean up multiple consecutive ul/ol tags
  html = html.replace(/<\/ul>\s*<ul>/g, "");
  html = html.replace(/<\/ol>\s*<ol>/g, "");

  // Handle paragraphs - split by double newlines
  const sections = html.split(/\n\s*\n/);
  html = sections
    .map((section) => {
      section = section.trim();
      if (!section) return "";

      // Don't wrap headers, lists, or already wrapped content
      if (section.match(/^<[h1-6]|^<[uo]l|^<li/)) {
        return section;
      }

      // Split by single newlines and wrap each line in p tags
      const lines = section.split(/\n/).filter((line) => line.trim());
      return lines
        .map((line) => (line.trim() ? `<p>${line.trim()}</p>` : ""))
        .join("");
    })
    .filter((p) => p)
    .join("");

  return html;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function showTyping() {
  isTyping = true;
  updateSendButton();

  const container = document.getElementById("messages");
  const typingDiv = document.createElement("div");
  typingDiv.className = "message typing-indicator";

  let avatarClass = "ai-avatar";
  if (currentPersona === "friendly") {
    avatarClass += " friendly-persona";
  } else if (currentPersona === "humorous") {
    avatarClass += " humorous-persona";
  }

  typingDiv.innerHTML = `
        <div class="message-avatar ${avatarClass}">🤖</div>
        <div class="message-bubble ai-bubble typing">
            <p>Thinking...</p>
        </div>
    `;

  container.appendChild(typingDiv);
  container.scrollTop = container.scrollHeight;
}

function hideTyping() {
  isTyping = false;
  updateSendButton();

  const typingEl = document.querySelector(".typing-indicator");
  if (typingEl) typingEl.remove();
}

function clearChat() {
  const container = document.getElementById("messages");
  container.innerHTML = `
        <div class="message">
            <div class="message-avatar ai-avatar">🤖</div>
            <div class="message-bubble ai-bubble">
                <p>Hello! I'm here to be your supportive companion in navigating family relationships. Whether you're a parent, caregiver, or adult child facing challenges with your own parents, I understand how overwhelming family dynamics can be—especially when trauma or difficult emotions are involved.</p>
                <p>I'm here to listen, support, and help you through these moments. How are things going for you today?</p>
            </div>
        </div>
    `;
}

function selectPrompt(promptText) {
  const messageInput = document.getElementById("messageInput");
  const suggestedPrompts = document.getElementById("suggestedPrompts");

  // Populate the input field
  messageInput.value = promptText;

  // Hide suggested prompts
  suggestedPrompts.style.display = "none";

  // Adjust textarea height and enable send button
  adjustHeight(messageInput);
  updateSendButton();

  // Focus on the input
  messageInput.focus();
}

// Initialize
updateSendButton();
