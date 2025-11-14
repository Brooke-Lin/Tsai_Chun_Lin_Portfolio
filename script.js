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

// Custom Burger Menu Animation
document.addEventListener('DOMContentLoaded', function() {
    const burgerContainer = document.getElementById('burger-container');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.getElementById('navbarmenu');
    const bsCollapse = new bootstrap.Collapse(navbarCollapse, { toggle: false });
    
    // Handle burger menu click - let Bootstrap handle the toggle
    navbarToggler.addEventListener('click', function() {
        // Bootstrap will handle opening/closing, we just sync the animation
    });
    
    // Handle Bootstrap collapse events to sync burger animation
    navbarCollapse.addEventListener('show.bs.collapse', function() {
        burgerContainer.classList.add('open');
    });
    
    navbarCollapse.addEventListener('hide.bs.collapse', function() {
        burgerContainer.classList.remove('open');
    });
    
    // Close menu when clicking on nav links (for mobile)
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Check if we're on mobile/tablet and menu is open
            if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                // Close the Bootstrap collapse
                bsCollapse.hide();
            }
        });
    });
});


//Chatbox toggle
const chatSection = document.getElementById('chat-section');
const toggleButton = document.getElementById('chat-toggle');
const closeButton = document.getElementById('close-chat');

toggleButton.addEventListener('click', () => {
  chatSection.classList.toggle('active');
  
  // Add suggested questions if not already present when chat opens
  if (chatSection.classList.contains('active')) {
    const existingSuggestions = chatBox.querySelector('.suggested-questions');
    if (!existingSuggestions) {
      const suggestedQuestions = createSuggestedQuestions();
      chatBox.appendChild(suggestedQuestions);
      chatBox.scrollTop = chatBox.scrollHeight;
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

// Prevent multiple concurrent requests
let isProcessing = false;
let lastRequestTime = 0;
const REQUEST_DELAY = 1000; // Minimum 1 second between requests
let lastResponseContent = ""; // Track last response to prevent duplicates

// Debounce function to prevent rapid requests
function debounce(func, delay) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

// Function to check if response is duplicate
function isDuplicateResponse(response) {
  const normalizedResponse = response.trim().toLowerCase();
  if (normalizedResponse === lastResponseContent) {
    console.log('Duplicate response detected, skipping display');
    return true;
  }
  lastResponseContent = normalizedResponse;
  return false;
}

// Predefined suggestion questions (answers will come from AI)
const chatSuggestions = {
  "suggestions": [
    {
      "question": "What is your education background?",
      "category": "education"
    },
    {
      "question": "Tell me about your recent projects?",
      "category": "projects"
    },
    {
      "question": "What is your working experience?",
      "category": "experience"
    },
    {
      "question": "What are your technical skills?",
      "category": "skills"
    },
    {
      "question": "What are your career goals?",
      "category": "career"
    },
    {
      "question": "Tell me about the Book 2 Drive project?",
      "category": "projects"
    },
    {
      "question": "What salary range are you looking for?",
      "category": "employment"
    },
    {
      "question": "What programming languages do you know?",
      "category": "skills"
    }
  ]
};

// Function to create suggested questions
function createSuggestedQuestions() {
  const suggestionsContainer = document.createElement('div');
  suggestionsContainer.className = 'suggested-questions';
  
  const intro = document.createElement('p');
  intro.textContent = 'Try asking me about:';
  suggestionsContainer.appendChild(intro);
  
  chatSuggestions.suggestions.forEach(suggestion => {
    const button = document.createElement('button');
    button.className = 'suggestion-btn';
    button.textContent = suggestion.question;
    button.addEventListener('click', () => handleSuggestionClick(suggestion.question));
    suggestionsContainer.appendChild(button);
  });
  
  return suggestionsContainer;
}

// Function to handle suggestion clicks
async function handleSuggestionClick(question) {
  // Prevent duplicate requests
  if (isProcessing) {
    console.log('Request already in progress, ignoring duplicate click');
    return;
  }
  
  // Rate limiting - prevent rapid requests
  const currentTime = Date.now();
  if (currentTime - lastRequestTime < REQUEST_DELAY) {
    console.log('Rate limit: Please wait before making another request');
    return;
  }
  lastRequestTime = currentTime;
  
  isProcessing = true;
  
  try {
    // Clear any existing input
    chatInput.value = "";
    
    // Add user message
    const userMsg = document.createElement('p');
    userMsg.innerHTML = `<b>You:</b> ${question}`;
    chatBox.appendChild(userMsg);
    
    // Remove suggestions after first use
    const suggestionsElement = chatBox.querySelector('.suggested-questions');
    if (suggestionsElement) {
      suggestionsElement.remove();
    }
    
    // Handle different environments
    if (isGitHubPages) {
      const staticMsg = document.createElement('p');
      staticMsg.innerHTML = `<b>Digital Twin:</b> <em style="color: #666;">Thanks for your interest! This AI chat feature is currently available when running with the backend server. For now, you can view my portfolio and download my resume to learn more about my experience.</em>`;
      chatBox.appendChild(staticMsg);
      chatBox.scrollTop = chatBox.scrollHeight;
      return;
    }
  
    // Show loading indicator
    const loadingMsg = document.createElement('p');
    loadingMsg.innerHTML = `<b>Digital Twin:</b> <em class="typing-indicator">Thinking<span class="dots">...</span></em>`;
    chatBox.appendChild(loadingMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    try {
      // Add unique timestamp and request ID to prevent caching and duplicates
      const timestamp = new Date().getTime();
      const requestId = Math.random().toString(36).substr(2, 9);
      const apiUrl = `/api/chat?question=${encodeURIComponent(question)}&t=${timestamp}&rid=${requestId}`;
      
      console.log('Making suggestion API request:', requestId, question);
      
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Remove loading indicator
      loadingMsg.remove();
      
      // Add AI response
      const responseMsg = document.createElement('p');
      responseMsg.innerHTML = `<b>Digital Twin:</b> ${data.answer}`;
      
      if (data.source === 'rag_system') {
        responseMsg.innerHTML += ` <small style="color: #888;">(AI-powered response)</small>`;
      }
      
      chatBox.appendChild(responseMsg);
      
    } catch (error) {
      console.error('Chat error:', error);
      
      // Remove loading indicator
      if (loadingMsg.parentNode) {
        loadingMsg.remove();
      }
      
      // Show error message
      const errorMsg = document.createElement('p');
      errorMsg.innerHTML = `<b>Digital Twin:</b> <em style="color: #e74c3c;">I'm having trouble accessing my knowledge base. Please try asking in the chat box below.</em>`;
      chatBox.appendChild(errorMsg);
    }
    
    // Auto scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
    
  } finally {
    // Always reset processing flag
    isProcessing = false;
  }
}

// Initialize suggested questions when page loads
const suggestedQuestions = createSuggestedQuestions();
chatBox.appendChild(suggestedQuestions);

// Check if running on GitHub Pages (static hosting without backend)
const isGitHubPages = window.location.hostname.includes('github.io');

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = chatInput.value.trim();
  
  if (!question) return; // Don't send empty messages
  
  // Prevent duplicate requests
  if (isProcessing) {
    console.log('Request already in progress, ignoring form submission');
    return;
  }
  
  // Rate limiting - prevent rapid requests
  const currentTime = Date.now();
  if (currentTime - lastRequestTime < REQUEST_DELAY) {
    console.log('Rate limit: Please wait before making another request');
    return;
  }
  lastRequestTime = currentTime;
  
  isProcessing = true;
  
  try {
    // Remove suggested questions after first interaction
    const suggestionsElement = chatBox.querySelector('.suggested-questions');
    if (suggestionsElement) {
      suggestionsElement.remove();
    }
    
    // Add user message
    const userMsg = document.createElement('p');
    userMsg.innerHTML = `<b>You:</b> ${question}`;
    chatBox.appendChild(userMsg);
    
    // Clear input immediately
    chatInput.value = "";
    
    // Show different behavior for different environments
    if (isGitHubPages) {
      // For GitHub Pages, show a helpful message
      const staticMsg = document.createElement('p');
      staticMsg.innerHTML = `<b>Digital Twin:</b> <em style="color: #666;">Thanks for your interest! This AI chat feature is currently available when running locally with the backend server. For now, you can view my portfolio and download my resume to learn more about my experience.</em>`;
      chatBox.appendChild(staticMsg);
      chatBox.scrollTop = chatBox.scrollHeight;
      return;
    }
  
    // Show loading indicator with typing effect
    const loadingMsg = document.createElement('p');
    loadingMsg.innerHTML = `<b>Digital Twin:</b> <em class="typing-indicator">Thinking<span class="dots">...</span></em>`;
    chatBox.appendChild(loadingMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    try {
      // Add unique timestamp and request ID to prevent caching and duplicates
      const timestamp = new Date().getTime();
      const requestId = Math.random().toString(36).substr(2, 9);
      const apiUrl = `/api/chat?question=${encodeURIComponent(question)}&t=${timestamp}&rid=${requestId}`;
      
      console.log('Making form API request:', requestId, question);
      console.log('API URL:', apiUrl);
      
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('API Response:', data);
      
      // Remove loading indicator
      if (loadingMsg.parentNode) {
        loadingMsg.remove();
      }
      
      // Add AI response with typing effect
      const responseMsg = document.createElement('p');
      responseMsg.innerHTML = `<b>Digital Twin:</b> ${data.answer}`;
      
      // Add source indicator if available
      if (data.source === 'rag_system') {
        responseMsg.innerHTML += ` <small style="color: #888;">(AI-powered response)</small>`;
      }
      
      chatBox.appendChild(responseMsg);
      
    } catch (error) {
      console.error('Chat error:', error);
      
      // Remove loading indicator
      if (loadingMsg.parentNode) {
        loadingMsg.remove();
      }
      
      // Show error message
      const errorMsg = document.createElement('p');
      errorMsg.innerHTML = `<b>Digital Twin:</b> <em style="color: #e74c3c;">I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment, or feel free to explore my portfolio for more information about my background.</em>`;
      chatBox.appendChild(errorMsg);
    }
    
    // Auto scroll to bottom
    chatBox.scrollTop = chatBox.scrollHeight;
    
  } finally {
    // Always reset processing flag
    isProcessing = false;
  }
});
