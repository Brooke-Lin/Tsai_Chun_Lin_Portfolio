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
});

closeButton.addEventListener('click', () => {
  chatSection.classList.remove('active');
});


//connect the website to the API
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatBox = document.getElementById("chat-box");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = chatInput.value;
  chatBox.innerHTML += `<p><b>You:</b> ${question}</p>`;

  const response = await fetch(`http://127.0.0.1:8001/ask?question=${encodeURIComponent(question)}`);
  const data = await response.json();

  chatBox.innerHTML += `<p><b>Digital Twin:</b> ${data.answer}</p>`;
  chatInput.value = "";
});
