function togglePassword() {
    let passwordField = document.getElementById("password");
    if (passwordField) {
        passwordField.type = (passwordField.type === "password") ? "text" : "password";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    setupEventListeners();
    if (document.getElementById("mcqForm")) {
        loadMCQTest();
    }
});

// ✅ Setup Event Listeners for Buttons and Forms
function setupEventListeners() {
    // Register Form Submission
    let registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", handleRegister);
    }

    // Login Form Submission
    let loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", handleLogin);
    }

    // Start MCQ Test
    let mcqTestBtn = document.getElementById("startMCQTest");
    if (mcqTestBtn) mcqTestBtn.addEventListener("click", () => window.location.href = "/mcq-test");

    // Start Coding Test
    let codingTestBtn = document.getElementById("startCodingTest");
    if (codingTestBtn) codingTestBtn.addEventListener("click", () => window.location.href = "/coding-test");

    // Logout Button
    let logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function () {
            localStorage.removeItem("token");
            alert("Logged out successfully!");
            window.location.href = "/login";
        });
    }

    // MCQ Form Submission
    let mcqForm = document.getElementById("mcqForm");
    if (mcqForm) {
        mcqForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            await submitMCQTest();
        });
    }
}

// ✅ Register User
async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const mobile_number = document.getElementById("mobile").value;
    const language = document.getElementById("language").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/auth/register/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, mobile_number, language, password })
        });

        if (response.ok) {
            alert("Registration successful!");
            window.location.href = "/login";
        } else {
            const errorData = await response.json();
            alert("Registration failed: " + (errorData.detail || "Unknown error"));
        }
    } catch (error) {
        console.error("Registration error:", error);
        alert("An error occurred while registering. Try again.");
    }
}

// ✅ Login User
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/auth/token/", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `username=${username}&password=${password}`
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem("token", data.access_token);
            alert("Login Successful!");
            window.location.href = "/dashboard";
        } else {
            alert("Invalid Credentials. Try Again!");
        }
    } catch (error) {
        console.error("Login error:", error);
        alert("An error occurred while logging in. Try again.");
    }
}

// ✅ Load MCQs
async function loadMCQTest() {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Unauthorized access! Please login.");
        window.location.href = "/login";
        return;
    }

    try {
        const response = await fetch("/mcq/mcq-test/", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) throw new Error("Failed to fetch questions");

        const questions = await response.json();
        const questionsContainer = document.getElementById("mcqQuestions");
        questionsContainer.innerHTML = "";

        questions.forEach((q, index) => {
            const questionElement = document.createElement("div");
            questionElement.classList.add("question");
        
            const options = q.options.map(opt => opt || "Not Available");
        
            questionElement.innerHTML = `
                <p><b>${index + 1}. </b><span></span></p>
                <label><input type="radio" name="q${q.id}" value="${options[0]}"> <span></span></label>
                <label><input type="radio" name="q${q.id}" value="${options[1]}"> <span></span></label>
                <label><input type="radio" name="q${q.id}" value="${options[2]}"> <span></span></label>
                <label><input type="radio" name="q${q.id}" value="${options[3]}"> <span></span></label>
            `;
        
            // Set text content to avoid rendering issues
            questionElement.querySelector("p span").innerHTML = q.question;
            const labels = questionElement.querySelectorAll("label span");
            labels[0].innerHTML = options[0];
            labels[1].innerHTML= options[1];
            labels[2].innerHTML = options[2];
            labels[3].innerHTML = options[3];
        
            questionsContainer.appendChild(questionElement);
        });
        
    } catch (error) {
        console.error("Error loading MCQs:", error);
        document.getElementById("mcqQuestions").innerHTML = "<p>Error loading questions. Unauthorized access.</p>";
    }
}
//implemeting the code for the submit- mcq-test

// ✅ Submit MCQ Test
async function submitMCQTest() {
    const token = localStorage.getItem("token");
    let answers = [];

    document.querySelectorAll(".question").forEach(q => {
        const questionId = q.querySelector("input").name.replace("q", "");
        const selectedOption = q.querySelector("input:checked")?.value;

        if (selectedOption) {
            answers.push({ question_id: parseInt(questionId), selected_option: selectedOption });
        }
    });

    if (answers.length === 0) {
        alert("Please answer at least one question!");
        return;
    }
    const submitButton = document.getElementById("submitBtn");
    submitButton.disabled = true;
    submitButton.innerText = "Submitting...";

    console.log("Sending answers:", JSON.stringify(answers)); // ✅ Debug log

    try {
        const response = await fetch("/mcq/submit-mcq-test/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(answers)
        });

        const responseData = await response.json();
        console.log("Response:", responseData); // ✅ Debug log

        if (response.ok) {
            document.getElementById("mcqResult").innerText = `Your Score: ${responseData.score} / 20`;
            submitButton.innerText = "Test Already Submitted";
            submitButton.style.backgroundColor = "#ccc";
            submitButton.disabled = true;
        }else {
            // 👇 Handle duplicate submission case
            if (responseData.detail && responseData.detail.toLowerCase().includes("already submitted"))
                {
                alert("⚠️ You have already submitted the MCQ test. You cannot submit it again.");
                submitButton.innerText = "Already Submitted";
                submitButton.style.backgroundColor = "#ccc";
                submitButton.disabled = true;
            } else {
                alert(`Error: ${responseData.detail}`);
                submitButton.disabled = false;
                submitButton.innerText = "Submit Test";
            }
        }
    } catch (error) {
        console.error("MCQ Submission Error:", error);
        alert("An error occurred while submitting the test. Try again.");
        submitButton.disabled = false;
        submitButton.innerText = "Submit Test";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const startCodingTestBtn = document.getElementById("startCodingTest");

    if (startCodingTestBtn) {  // ✅ Check if the button exists
        startCodingTestBtn.addEventListener("click", function () {
            window.location.href = "/coding-test";  // Change this to the correct coding test page URL
        });
    } else {
        console.error("Error: 'startCodingTestBtn' not found in the DOM.");
    }
});



async function loadCodingTest() {
    const token = localStorage.getItem("token");
    if (!token) {
        alert("Unauthorized access! Please login.");
        window.location.href = "/login";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/coding/coding-question/", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) throw new Error("Failed to fetch coding questions");

        const questions = await response.json();
        console.log("API Response:", questions);  // Debugging response

        // ✅ Ensure response is an array
        if (!Array.isArray(questions) || questions.length === 0) {
            console.error("Invalid or empty response");
            document.getElementById("codingQuestions").innerHTML = "<p>No coding questions available.</p>";
            return;
        }

        const questionsContainer = document.getElementById("codingQuestions");
        questionsContainer.innerHTML = "";  // Clear old questions

        // ✅ Loop through all questions and display them
        questions.forEach(q => {
            const questionElement = document.createElement("div");
            questionElement.classList.add("question");

            // ✅ Create Test Cases Section
            let testCasesHTML = "<ul>";
            q.test_cases.slice(0,2).forEach(tc => {
                testCasesHTML += `<li><b>Input:</b> ${tc.input}, <b>Expected Output:</b> ${tc.expected_output}</li>`;
            });
            testCasesHTML += "</ul>";

            // ✅ Add Question + Test Cases + Attempt Button
            questionElement.innerHTML = `
                <p><b>${q.question}</b></p>
                <div class="test-cases">
                    <b>Example :</b> ${testCasesHTML}
                </div>
                <button onclick="attemptCoding(${q.question_id})">Attempt</button>
            `;
            questionsContainer.appendChild(questionElement);
        });

    } catch (error) {
        console.error("Error loading coding questions:", error);
        document.getElementById("codingQuestions").innerHTML = "<p>Error loading questions. Please try again.</p>";
    }
}

function attemptCoding(questionId) {
    window.location.href = `/code-editor?questionId=${questionId}`;
}



document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("codingQuestions")) {
        loadCodingTest();
    }
});
