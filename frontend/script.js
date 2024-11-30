let currentSession = '';
let sessions = {};
let sessionOrder = [];

// When the page loads, fetch the list of available sessions
window.onload = () => {
    fetchSessions();
};

// Fetch sessions from the backend
function fetchSessions() {
    fetch("/list_sessions")
        .then(response => response.json())
        .then(data => {
            sessions = {};  // Clear current sessions object
            sessionOrder = [];  // Clear current session order

            // Iterate over each session returned by the backend
            data.sessions.forEach(sessionName => {
                sessions[sessionName] = { messages: [] };  // Add each session to the sessions object
                sessionOrder.push(sessionName);  // Add each session to the session order array
            });

            // After fetching and updating session data, update the UI
            updateSessionList();

            // Load the last used session from localStorage after sessions are populated
            const lastUsedSession = localStorage.getItem('lastUsedSession');
            if (lastUsedSession && sessions[lastUsedSession]) {
                switchSession(lastUsedSession);  // Automatically switch to the last active session
            }
        })
        .catch(error => {
            console.error('Error fetching sessions:', error);
        });
}

// Function to toggle the dropdown menu
function toggleDropdown(event) {
    event.stopPropagation();
    const dropdown = event.currentTarget.nextElementSibling;
    closeAllDropdowns();  // Close other dropdowns
    dropdown.classList.toggle('show');
}

// Function to close all dropdowns when clicking outside
function closeAllDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown-content');
    dropdowns.forEach(dropdown => dropdown.classList.remove('show'));
}

// Update the session list UI
function updateSessionList() {
    const sessionList = document.getElementById("sessionList");
    sessionList.innerHTML = '';  // Clear existing sessions

    // Render each session from the sessionOrder array
    for (let session of sessionOrder) {
        sessionList.innerHTML += `
            <li class="session-item" onclick="switchSession('${session}')">
                <span class="session-name">${session}</span>
                <button class="dropdown-button" onclick="toggleDropdown(event); event.stopPropagation();">▼</button>
                <div class="dropdown-content">
                    <a href="#" onclick="renameSession('${session}'); event.stopPropagation();">Rename</a>
                    <a href="#" onclick="removeSession('${session}'); event.stopPropagation();">Delete</a>
                </div>
            </li>`;
    }
}

// Add event listener to close dropdowns when clicking outside
document.addEventListener('click', closeAllDropdowns);

// Add event listeners for buttons
document.getElementById("sendButton").addEventListener("click", sendMessage);
document.getElementById("addSessionBtn").addEventListener("click", promptForSessionName);
document.getElementById("removeSessionBtn").addEventListener("click", () => {
    if (currentSession) {
        removeSession(currentSession);  // Remove current session
    }
});

// Function to prompt for a new session name
function promptForSessionName() {
    const sessionName = prompt("Enter session name:");
    if (sessionName) {
        addSession(sessionName.trim());
    }
}

// Function to send a message
function sendMessage() {
    const userInputElement = document.getElementById("userInput");
    const userInput = userInputElement.value.trim();
    const mode = document.getElementById("modeToggle").value;

    if (!userInput) return; // Stop if input is empty

    const chatWindow = document.getElementById("chatWindow");

    // Add user message to chat window
    const userMessageDiv = document.createElement("div");
    userMessageDiv.className = "message user";
    userMessageDiv.textContent = userInput;
    chatWindow.appendChild(userMessageDiv);

    // Clear the input field
    userInputElement.value = '';

    // Fetch bot response
    // Fetch bot response
    fetch("/query", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: userInput, mode: mode }),
    })
    .then(response => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
    })
    .then(data => {
        const botResponse = data.text_response;

        // Convert Markdown to HTML (simple handling)
        const markdownHtml = marked.parse(botResponse);

        // Display the response in the chat window
        const botMessageDiv = document.createElement("div");
        botMessageDiv.className = "message bot";
        botMessageDiv.innerHTML = markdownHtml;

        chatWindow.appendChild(botMessageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight; // Auto-scroll
    })
    .catch(error => {
        console.error('Error fetching response:', error);
        const errorMessageDiv = document.createElement("div");
        errorMessageDiv.className = "message bot error";
        errorMessageDiv.textContent = "Error fetching response. Please try again.";
        chatWindow.appendChild(errorMessageDiv);
    });


// Function to save the conversation to the database
function saveMessageToDatabase(userMessage, botResponse) {
    fetch("/save_message", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            session_name: currentSession,  // Ensure `currentSession` is defined globally
            user_message: userMessage,
            bot_response: botResponse
        }),
    })
    .catch(error => {
        console.error('Error saving message:', error);
        // Optionally, you can display an error message to the user here
    });
}


// Function to add a new session
function addSession(sessionName) {
    if (sessionName && !sessions[sessionName]) {
        sessions[sessionName] = { messages: [] };
        sessionOrder.unshift(sessionName);
        updateSessionList();

        // Save session to database
        fetch("/save_session", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ session_name: sessionName }),
        })
        .then(() => {
            switchSession(sessionName);
            localStorage.setItem('lastUsedSession', sessionName);
        })
        .catch(error => {
            console.error('Error saving session:', error);
        });
    } else {
        alert("Session name already exists or is invalid.");
    }
}

// Function to remove the current session
function removeSession(sessionName) {
    if (sessionName && confirm(`Are you sure you want to delete the session "${sessionName}"?`)) {
        fetch(`/delete_session/${sessionName}`, {
            method: "DELETE",
        })
        .then(() => {
            delete sessions[sessionName];
            sessionOrder = sessionOrder.filter(session => session !== sessionName);
            updateSessionList();

            if (sessionName === currentSession) {
                currentSession = '';  // Reset to no session
                document.getElementById("userInput").value = '';
                document.getElementById("chatWindow").innerHTML = '';
                localStorage.removeItem('lastUsedSession');
            }
        })
        .catch(error => {
            console.error('Error deleting session:', error);
        });
    }
}

// Function to switch between sessions
function switchSession(sessionName, event) {
    // Prevent session switch if the click comes from the dropdown button
    if (event && event.target.classList.contains('dropdown-button')) {
        return;
    }

    // Only switch session if it's different from the current one
    if (currentSession !== sessionName) {
        currentSession = sessionName;

        const chatWindow = document.getElementById("chatWindow");
        chatWindow.innerHTML = '';  // Clear chat window

        // Remove active class from all sessions
        const sessionItems = document.querySelectorAll("#sessionList li");
        sessionItems.forEach(item => item.classList.remove("active-session"));

        // Add active class to the clicked session
        const activeSession = [...sessionItems].find(item => item.querySelector('.session-name').textContent === sessionName);
        if (activeSession) {
            activeSession.classList.add("active-session");
        }

        // Fetch session data and load chat messages
        fetch(`/load_session/${sessionName}`)
            .then(response => {
                if (!response.ok) throw new Error('Session not found');
                return response.json();
            })
            .then(data => {
                // Populate chat window with the messages
                data.messages.forEach(message => {
                    chatWindow.innerHTML += `<div class="message user">${message.user_message}</div>`;
                    chatWindow.innerHTML += `<div class="message bot">${message.bot_response}</div>`;
                });
                // Auto-scroll to the bottom of the chat window
                chatWindow.scrollTop = chatWindow.scrollHeight;
            })
            .catch(error => {
                console.error('Error loading session:', error);
                chatWindow.innerHTML += `<div class="message bot">Hi, What can I help you with today?</div>`;
            });

        // Store the last used session in localStorage
        localStorage.setItem('lastUsedSession', currentSession);
        console.log(`Switched to session: ${sessionName}`);
    }
}


// Function to rename the session
function renameSession(oldSessionName) {
    const newSessionName = prompt("Enter new session name:", oldSessionName);
    if (newSessionName && newSessionName !== oldSessionName && !sessions[newSessionName]) {
        // Rename in local sessions
        sessions[newSessionName] = sessions[oldSessionName];
        delete sessions[oldSessionName];
        sessionOrder = sessionOrder.map(session => session === oldSessionName ? newSessionName : session);
        updateSessionList();

        // Fetch call to the backend
        fetch(`/rename_session/${oldSessionName}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ new_session_name: newSessionName }), // Correct payload
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            switchSession(newSessionName);
            localStorage.setItem('lastUsedSession', newSessionName);
        })
        .catch(error => {
            console.error('Error renaming session:', error);
        });
    } else {
        alert("Session name already exists or is invalid.");
    }
}


const userInput = document.getElementById("userInput");

userInput.addEventListener("input", () => {
    userInput.style.height = 'auto'; // Reset the height
    userInput.style.height = `${userInput.scrollHeight}px`; // Set the new height
});
