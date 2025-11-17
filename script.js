//BACKGROUND IMAGE 1 FOR BROOKE ANIMATION

const timeline = gsap.timeline({ repeat: -1, repeatDelay: 2 }); 
//gsap.timeline() lets you chain multiple animations in a sequence
//repeat: -1 means loop forever
//repeatDelay: 2 means wait 2 seconds before repeating the whole animation
const chars = document.querySelectorAll(".text");

gsap.set(".one", { color: "#FFEAF3" });
gsap.set(".two", { color: "#FFDFF0" });
gsap.set(".three", { color: "#FFD3EB" });
gsap.set(".four", { color: "#FFC8E6" });
gsap.set(".five", { color: "#FFBDDF" });
gsap.set(".six", { color: "#FFB3D9" });
//These lines set different colors for elements with classes .one, .two, .three, etc
//They do not animate - they just immediately apply styles

timeline.from(chars, {
    opacity: 0,
    scale: 0,
    ease: "back.out(1.7)",
    duration: 0.6,
    stagger: 0.1
})
//This animates all letters (chars):
//opacity: 0 means letters start invisible
//scale: 0 means they start tiny and grow to normal size
//ease: "back.out(1.7)" gives a bounce-back effect
//duration: 0.6 means each animation lasts 0.6 seconds
//stragger: 0.1 means letters appear one after another every 0.1s, not all at once

.to(".text", {
    "--font-weight": 900,
    duration: 1.2,
    ease: "sine.inOut",
    stagger: {
        yoyo: true,
        each: 0.1,
        repeat: 1 
    }
}, "+=0.5");
//Targets all elements with class .text
//Animates the CSS variable --font-weight to 900
//Uses sine.inOut for smoother pulsing
//Starts 0.5 seconds after the previous animation finishes (+=0.5)
//Inside the stragger: 
//each: 0.1 animates each letter with a 0.1s delay between them
//yoyo: true after going to bold, it returns back to normal
//repeat: 1 pulses only once (forward and backward)

// Fixed typo in comments: "stragger" -> "stagger"





//CUSTOM BURGER MENU ANIMATION

document.addEventListener('DOMContentLoaded', function() {
//This ensures all HTML elements exist before the script tries to access them
    const burgerContainer = document.getElementById('burger-container');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.getElementById('navbarmenu');
    const bsCollapse = new bootstrap.Collapse(navbarCollapse, { toggle: false });
    //This creates a Collapse object that allows you to open and close the menu using JavaScript:
    //bsCollapse.show(), bsCollapse.hide(), bsCollapse.toggle()
    //{toggle: false} means: don't automatically open/close the menu when creating this object
    
    navbarToggler.addEventListener('click', function() {

    });
    //Bootstrap already handles the toggle. So this click event is not used to open the menu - it's only here in case you need to sync custom animations

    navbarCollapse.addEventListener('show.bs.collapse', function() {
        burgerContainer.classList.add('open');
    });
    //Adds class .open to trigger your CSS animation 
    
    navbarCollapse.addEventListener('hide.bs.collapse', function() {
        burgerContainer.classList.remove('open');
    });
    //Removes .open so burger returns to normal
    
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                bsCollapse.hide();
            }
        });
    });
    //On small screens (<992px = mobile/tablet). If the menu is open, and the user clicks any navigation link, then close the menu automatically
});





// 1. CHATBOX TOGGLE (OPEN/CLOSE FEATURE)

const chatSection = document.getElementById('chat-section');
const toggleButton = document.getElementById('chat-toggle');
const closeButton = document.getElementById('close-chat');

toggleButton.addEventListener('click', () => {
  chatSection.classList.toggle('active');
  
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



// 2. CONNECTING WEBSITE TO THE API

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatBox = document.getElementById("chat-box");
//This part prepares everything needed to call your AI



// 3. REQUEST CONTROL (PREVENT SPAM/ DUPLICATES)

let isProcessing = false;
//Prevents sending a new request if one is still running
let lastRequestTime = 0;
const REQUEST_DELAY = 1000;
//Minimum 1 second between messages
let lastResponseContent = ""; 
//Avoid showing the same response twice (useful for Groq or AI that sometimes repeats)

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



// 4. SUGGESTED QUESTIONS SYSTEM

//An array of pre-made questions that your AI will answer
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

//Creating the suggestion buttons
function createSuggestedQuestions() {
  const suggestionsContainer = document.createElement('div');
  suggestionsContainer.className = 'suggested-questions';
  
  const intro = document.createElement('p');
  intro.textContent = 'Try asking me about:';
  suggestionsContainer.appendChild(intro);
  
  // Only show up to 3 suggested questions to keep the UI compact
  chatSuggestions.suggestions.slice(0, 3).forEach(suggestion => {
    const button = document.createElement('button');
    button.className = 'suggestion-btn';
    button.textContent = suggestion.question;
    button.addEventListener('click', () => handleSuggestionClick(suggestion.question));
    suggestionsContainer.appendChild(button);
  });
  
  return suggestionsContainer;
}



// 5. WHEN USER CLICKS A SUGGESTED QUESTION

async function handleSuggestionClick(question) {
//This is one of the most important parts
  if (isProcessing) {
    console.log('Request already in progress, ignoring duplicate click');
    return;
  }//It prevents double requests
  
  const currentTime = Date.now();
  if (currentTime - lastRequestTime < REQUEST_DELAY) {
    console.log('Rate limit: Please wait before making another request');
    return;
  }//It prevents spam clicking

  lastRequestTime = currentTime;
  
  isProcessing = true;
  
  try {
    // Clear any existing input
    chatInput.value = "";
    
    //Add message to chat
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

// 6. GITHUB PAGES MODE
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
