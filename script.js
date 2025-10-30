//Background image 1 for Brooke animation
const timeline = gsap.timeline({ repeat: -1, repeatDelay: 2 }); // repeatDelay adds 5 seconds between loops
const chars = document.querySelectorAll(".text");

gsap.set(".one", { color: "#3498DB" });
gsap.set(".two", { color: "#E74C3C" });
gsap.set(".three", { color: "#F1C40F" });
gsap.set(".four", { color: "#3498DB" });
gsap.set(".five", { color: "#27AE60" });
gsap.set(".six", { color: "#E74C3C" });

timeline.from(chars, {
    opacity: 0,
    scale: 0,
    ease: "back.out(1.7)",
    duration: 0.6,
    stagger: 0.1
})
.to(".text", {
    "--font-weight": 900,
    duration: 1.2,
    ease: "sine.inOut",
    stagger: {
        yoyo: true,
        each: 0.1,
        repeat: 1 // keep each letter pulsing once before reset
    }
}, "+=0.5");


//Chatbox toggle
const chatSection = document.getElementById('chat-section');
const toggleButton = document.getElementById('chat-toggle');
const closeButton = document.getElementById('close-chat');

toggleButton.addEventListener('click', () => {
  chatSection.classList.toggle('active');
  
  // Ensure coming soon message is visible on GitHub Pages when chat opens
  if (isGitHubPages && chatSection.classList.contains('active')) {
    const existingMessage = chatBox.querySelector('.coming-soon');
    
    if (!existingMessage) {
      const comingSoonMessage = document.createElement('div');
      comingSoonMessage.className = 'coming-soon';
      comingSoonMessage.innerHTML = '💡 <strong>AI Chat Coming Soon!</strong><br>The interactive chat feature requires a backend server and will be available when deployed with full infrastructure.';
      chatBox.insertBefore(comingSoonMessage, chatBox.firstChild);
    }
  }
});

closeButton.addEventListener('click', () => {
  chatSection.classList.remove('active');
});


//connect the website to the API
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatBox = document.getElementById("chat-box");

// Check if we're on GitHub Pages (moved to top to avoid redeclaration)
const isGitHubPages = window.location.hostname.includes('github.io');

// Add coming soon message for GitHub Pages
if (isGitHubPages) {
  const comingSoonMessage = document.createElement('div');
  comingSoonMessage.className = 'coming-soon';
  comingSoonMessage.innerHTML = '💡 <strong>AI Chat Coming Soon!</strong><br>The interactive chat feature requires a backend server and will be available when deployed with full infrastructure.';
  chatBox.appendChild(comingSoonMessage);
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = chatInput.value.trim();
  
  if (!question) return; // Don't send empty messages
  
  // Add user message
  chatBox.innerHTML += `<p><b>You:</b> ${question}</p>`;
  chatInput.value = "";
  
  // Show different behavior for GitHub Pages vs local
  if (isGitHubPages) {
    // For GitHub Pages, show a helpful message
    chatBox.innerHTML += `<p><b>Digital Twin:</b> <em style="color: #666;">Thanks for your interest! This AI chat feature is currently available when running locally with the backend server. For now, you can view my portfolio and download my resume to learn more about my experience.</em></p>`;
    chatBox.scrollTop = chatBox.scrollHeight;
    return;
  }
  
  // Show loading indicator for local development
  chatBox.innerHTML += `<p><b>Digital Twin:</b> <em>Thinking...</em></p>`;
  chatBox.scrollTop = chatBox.scrollHeight; // Auto scroll to bottom
  
  try {
    const response = await fetch(`http://127.0.0.1:8001/ask?question=${encodeURIComponent(question)}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Remove loading indicator
    const messages = chatBox.children;
    const lastMessage = messages[messages.length - 1];
    lastMessage.remove();
    
    // Add AI response
    chatBox.innerHTML += `<p><b>Digital Twin:</b> ${data.answer}</p>`;
    
  } catch (error) {
    console.error('Chat error:', error);
    
    // Remove loading indicator
    const messages = chatBox.children;
    const lastMessage = messages[messages.length - 1];
    lastMessage.remove();
    
    // Show error message
    chatBox.innerHTML += `<p><b>Digital Twin:</b> <em style="color: red;">Sorry, I'm having trouble connecting. Please make sure the server is running and try again.</em></p>`;
  }
  
  // Auto scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;
});
