const categories = ["General", "Study", "Work", "Fitness"];
const encouragements = {
  General: [
    "Keep pushing forward!", "You're doing great!", "Stay strong!", "One step closer!",
    "Your effort matters!", "You're unstoppable!", "Every step counts!", "Progress is power!"
  ],
  Study: [
    "Books are your best friend!", "Every page you read is one step ahead!",
    "Knowledge is your superpower!", "Stay focused, student star!",
    "You're mastering the future!", "Just 10 more minutes!", "Revision is key!", "You're a scholar in progress!"
  ],
  Work: [
    "Productivity looks good on you!", "Power through those tasks!",
    "You're getting things DONE!", "Working hard, dreaming big!",
    "Emails can’t stop you!", "Keep climbing the ladder!", "You're a workplace warrior!", "Focused and fearless!"
  ],
  Fitness: [
    "Sweat today, shine tomorrow!", "Keep that heart pumping!", "Stronger with every rep!",
    "Your health is wealth!", "Push yourself a little more!", "You’re building a stronger you!", "Stay active, stay happy!", "Beast mode: ON!"
  ]
};
li.classList.add(category.toLowerCase());  // assuming `category` is Study/Work etc.


const quotes = [
  "Discipline is the bridge between goals and accomplishment.",
  "Focus on being productive instead of busy.",
  "Start where you are. Use what you have. Do what you can.",
  "Every accomplishment starts with the decision to try.",
  "Success is the sum of small efforts repeated day in and day out.",
  "Don’t limit your challenges, challenge your limits.",
  "It always seems impossible until it’s done.",
  "The secret of getting ahead is getting started.",
  "Work hard in silence, let success make the noise.",
  "Action is the foundational key to all success."
];

// Load and display random quote at top
function loadRandomQuote() {
  const quote = quotes[Math.floor(Math.random() * quotes.length)];
  const quoteBox = document.getElementById("quoteText");
  if (quoteBox) quoteBox.innerText = `"${quote}"`;
}

function showNotification(title, body) {
  if (Notification.permission === "granted") {
    new Notification(title, { body });
  } else if (Notification.permission !== "denied") {
    Notification.requestPermission().then(permission => {
      if (permission === "granted") {
        new Notification(title, { body });
      }
    });
  }
}

// Fetch and render tasks
async function fetchTasks() {
  const res = await fetch('/tasks');
  const tasks = await res.json();
  renderTasks(tasks);
}

// Render task list to UI
function renderTasks(tasks) {
  const ul = document.getElementById('taskList');
  ul.innerHTML = '';
  tasks.forEach(taskObj => {
    const li = document.createElement('li');
    li.innerText = `[${taskObj.category}] ${taskObj.task} (${taskObj.created_at.split(' ')[1]})`;

    const completeBtn = document.createElement('button');
    completeBtn.innerText = '✔️';
    completeBtn.onclick = () => completeTask(taskObj.task, taskObj.category);

    const deleteBtn = document.createElement('button');
    deleteBtn.innerText = '❌';
    deleteBtn.onclick = () => deleteTask(taskObj.task);

    li.appendChild(completeBtn);
    li.appendChild(deleteBtn);
    ul.appendChild(li);
  });
}

// Add new task
async function addTask() {
  const taskInput = document.getElementById('taskInput');
  const task = taskInput.value.trim();
  const category = document.getElementById('catSelect').value;
  if (!task) return;

  await fetch('/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task, category })
  });

  taskInput.value = '';
  fetchTasks();
  fetchTip();
}

// Delete task
async function deleteTask(task) {
  await fetch('/tasks', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task })
  });

  fetchTasks();
}

// Complete task
async function completeTask(task, category) {
  await fetch('/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task })
  });

  deleteTask(task);
  updateStreak();
  showNotification("✅ Task Complete", "Keep going! You're doing awesome!");
  displayEncouragement(category);
}

// Display encouragement dynamically
function displayEncouragement(category) {
  const list = encouragements[category] || encouragements["General"];
  const message = list[Math.floor(Math.random() * list.length)];
  document.getElementById("encourageText").innerText = "🎉 " + message;
}

// Update streak
async function updateStreak() {
  const res = await fetch('/streak');
  const data = await res.json();
  document.getElementById("streak").innerText = data.streak;
}

// Fetch daily tip
async function fetchTip() {
  const res = await fetch('/recommendation');
  const data = await res.json();
  document.getElementById("tipText").innerText = data.tip;
}

// Alert if task is not completed in 1 hour
function setupReminder() {
  setTimeout(() => {
    alert("⏰ Reminder: You haven’t completed any tasks today!");
  }, 3600000); // 1 hour
}

document.addEventListener("DOMContentLoaded", () => {
  fetchTasks();
  fetchTip();
  loadRandomQuote();
  setupReminder();
  Notification.requestPermission();
});
