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

// Predefined suggestions and answers
const chatSuggestions = {
  "suggestions": [
    {
      "question": "What is your education background?",
      "answer": "I have a Master of Applied Information Technology from Victoria University (2024-2025) with a GPA of 6.25. My coursework included Advanced Web Development, Database Systems, Software Engineering, Cloud Computing, and Cybersecurity. I also have a Master of Information Systems & Advertising from University of Queensland (2021-2023) with a GPA of 5.37, where I worked on database design and system analysis projects."
    },
    {
      "question": "Tell me about your recent projects?",
      "answer": "My most recent major project is Book 2 Drive - a driving lesson booking application I led as part of a 3-person university team. I designed the responsive UI using HTML, CSS, JavaScript, and PHP, implemented user authentication, and created a MySQL database. I've also built several portfolio projects including a responsive News Homepage and an Interactive Multi-Step Form with validation, both showcasing my frontend development skills."
    },
    {
      "question": "Tell me about your working experience?",
      "answer": "I’m currently working at Kitchen Montague, where I focus on providing excellent customer service, managing orders efficiently, and maintaining a high standard of teamwork in a fast-paced environment. Previously, I worked as a Technical Support Intern at Ben Curtains (Jan 2025 – Apr 2025), where I organized website content, updated product images using WordPress, and assisted with technical and sales-related tasks. These experiences have helped me develop strong communication, problem-solving, and time management skills."
    },
    {
      "question": "What are your technical skills?",
      "answer": "I’m familiar with using HTML, CSS, JavaScript, and Bootstrap to develop responsive web applications. Recently, I started learning PHP while working on the Book 2 Drive project, where I applied it to handle backend functionality and database operations. I also have some backend experience from my analysis project at the University of Queensland, where I worked on database design and data processing tasks. In addition, I’m comfortable using Git and GitHub for version control."
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
    button.addEventListener('click', () => handleSuggestionClick(suggestion.question, suggestion.answer));
    suggestionsContainer.appendChild(button);
  });
  
  return suggestionsContainer;
}

// Function to handle suggestion clicks
function handleSuggestionClick(question, answer) {
  // Add user message
  chatBox.innerHTML += `<p><b>You:</b> ${question}</p>`;
  
  // Add AI response
  chatBox.innerHTML += `<p><b>Digital Twin:</b> ${answer}</p>`;
  
  // Remove suggestions after first use
  const suggestionsElement = chatBox.querySelector('.suggested-questions');
  if (suggestionsElement) {
    suggestionsElement.remove();
  }
  
  // Auto scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Initialize suggested questions when page loads
const suggestedQuestions = createSuggestedQuestions();
chatBox.appendChild(suggestedQuestions);

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = chatInput.value.trim();
  
  if (!question) return; // Don't send empty messages
  
  // Add user message
  chatBox.innerHTML += `<p><b>You:</b> ${question}</p>`;
  chatInput.value = "";
  
  // Show different behavior for different environments
  if (isGitHubPages) {
    // For GitHub Pages, show a helpful message
    chatBox.innerHTML += `<p><b>Digital Twin:</b> <em style="color: #666;">Thanks for your interest! This AI chat feature is currently available when running locally with the backend server. For now, you can view my portfolio and download my resume to learn more about my experience.</em></p>`;
    chatBox.scrollTop = chatBox.scrollHeight;
    return;
  }
  
  // Show loading indicator
  chatBox.innerHTML += `<p><b>Digital Twin:</b> <em>Thinking...</em></p>`;
  chatBox.scrollTop = chatBox.scrollHeight; // Auto scroll to bottom
  
  try {
    // Determine API URL based on environment
    const apiUrl = (window.location.hostname.includes('vercel.app') || window.location.hostname.includes('tsai-chun-lin-portfolio'))
      ? '/api/chat'  // Vercel serverless function endpoint
      : 'http://127.0.0.1:8001/ask';  // Local development
    
    const response = await fetch(`${apiUrl}?question=${encodeURIComponent(question)}`);
    
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
    chatBox.innerHTML += `<p><b>Digital Twin:</b> <em style="color: red;">Sorry, I'm having trouble connecting. Please try again in a moment.</em></p>`;
  }
  
  // Auto scroll to bottom
  chatBox.scrollTop = chatBox.scrollHeight;
});
