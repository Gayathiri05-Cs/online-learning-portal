const $ = (id) => document.getElementById(id);
let currentUser = null;
let authMode = "login";
let currentCourse = null;
let currentLesson = null;
let toastTimer;

async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || "Something went wrong. Please try again.");
  return data;
}
function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[ch]));
}
function showToast(message) {
  const node = $("toast"); node.textContent = message; node.classList.add("show");
  clearTimeout(toastTimer); toastTimer = setTimeout(() => node.classList.remove("show"), 3000);
}
function showPage(page) {
  ["home","dashboard","course","lesson"].forEach(name => $(name+"Page").classList.toggle("hidden", name !== page));
  document.querySelectorAll(".nav-link").forEach(btn => btn.classList.toggle("active", btn.dataset.page === page));
  window.scrollTo({top:0,behavior:"smooth"});
  if (page === "home") loadCourses();
  if (page === "dashboard") loadDashboard();
}
function openAuth(mode) {
  authMode = mode;
  const register = mode === "register";
  $("authTitle").textContent = register ? "Create your account." : "Welcome back.";
  $("authSubtitle").textContent = register ? "Your learning journey starts with one small step." : "Log in to pick up where you left off.";
  $("nameField").classList.toggle("hidden", !register);
  $("authName").required = register;
  $("authPassword").autocomplete = register ? "new-password" : "current-password";
  $("authSubmit").textContent = register ? "Create account" : "Log in";
  $("switchAuth").innerHTML = register
    ? 'Already learning with us? <button type="button" onclick="openAuth(\'login\')">Log in</button>'
    : 'New to LearnSpace? <button type="button" onclick="openAuth(\'register\')">Create an account</button>';
  $("authError").classList.add("hidden"); $("authForm").reset(); $("authModal").classList.remove("hidden");
}
function closeAuth() { $("authModal").classList.add("hidden"); }
$("authModal").addEventListener("click", e => { if (e.target === $("authModal")) closeAuth(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeAuth(); });
$("authForm").addEventListener("submit", async e => {
  e.preventDefault(); const errorBox = $("authError"); errorBox.classList.add("hidden");
  const payload = {email:$("authEmail").value.trim(), password:$("authPassword").value};
  if (authMode === "register") payload.name = $("authName").value.trim();
  try {
    const data = await api(`/api/auth/${authMode}`, {method:"POST",body:JSON.stringify(payload)});
    currentUser = data.user; closeAuth(); updateAccountArea(); showToast(data.message);
    if (authMode === "register") showPage("dashboard"); else showPage("dashboard");
  } catch (err) { errorBox.textContent = err.message; errorBox.classList.remove("hidden"); }
});
function updateAccountArea() {
  $("accountArea").innerHTML = currentUser
    ? `<span class="welcome-user" style="font-size:12px;color:#61756a;margin-right:5px">Hi, ${escapeHTML(currentUser.name.split(" ")[0])}</span><button class="btn btn-outline" onclick="logout()">Log out</button>`
    : '<button class="btn btn-outline" onclick="openAuth(\'login\')">Log in</button><button class="btn btn-primary" onclick="openAuth(\'register\')">Sign up</button>';
}
async function checkUser() {
  try { const data = await api("/api/auth/me"); currentUser = data.user; updateAccountArea(); } catch { currentUser = null; }
}
async function logout() {
  try { await api("/api/auth/logout",{method:"POST"}); currentUser=null; updateAccountArea(); showToast("You have logged out."); showPage("home"); } catch(err){showToast(err.message);}
}
const icons = {python:"🐍",web:"✳",sql:"▤",ai:"✧",git:"⑂",data:"◈"};
function courseCard(course) {
  const icon = icons[course.image] || "✦";
  return `<article class="course-card"><div class="course-art ${escapeHTML(course.image)}"><span class="course-emoji">${icon}</span><span class="course-label">${escapeHTML(course.category.toUpperCase())}</span></div><div class="course-body"><div class="course-meta"><span>${course.lesson_count} lessons · ${escapeHTML(course.duration)}</span><span class="level-pill">${escapeHTML(course.level)}</span></div><h3>${escapeHTML(course.title)}</h3><p>${escapeHTML(course.description)}</p><div class="course-instructor"><div class="avatar">${escapeHTML(course.instructor.split(" ").map(s=>s[0]).join("").slice(0,2))}</div><div class="instructor-info"><b>${escapeHTML(course.instructor)}</b><small>Course instructor</small></div><button class="arrow-btn" aria-label="View ${escapeHTML(course.title)}" onclick="openCourse(${course.id})">↗</button></div></div></article>`;
}
async function loadCourses() {
  const grid = $("courseGrid"); grid.innerHTML = '<div class="loading">Finding something good to learn...</div>';
  const params = new URLSearchParams();
  if ($("searchInput").value.trim()) params.set("search",$("searchInput").value.trim());
  if ($("categoryFilter").value) params.set("category",$("categoryFilter").value);
  if ($("levelFilter").value) params.set("level",$("levelFilter").value);
  try {
    const courses = await api("/api/courses?"+params.toString());
    $("courseCount").textContent = `${courses.length} course${courses.length===1?"":"s"}`;
    grid.innerHTML = courses.length ? courses.map(courseCard).join("") : '<div class="empty-state">No courses match those filters. Try another search.</div>';
  } catch (err) { grid.innerHTML = `<div class="empty-state">${escapeHTML(err.message)}</div>`; }
}
async function loadCategories() {
  try { const cats=await api("/api/categories"); $("categoryFilter").innerHTML='<option value="">All categories</option>'+cats.map(c=>`<option value="${escapeHTML(c)}">${escapeHTML(c)}</option>`).join(""); } catch {}
}
let searchTimer;
$("searchInput").addEventListener("input",()=>{clearTimeout(searchTimer);searchTimer=setTimeout(loadCourses,250);});
$("categoryFilter").addEventListener("change",loadCourses);
$("levelFilter").addEventListener("change",loadCourses);
async function openCourse(id) {
  try {
    const data=await api(`/api/courses/${id}`); currentCourse=data.course;
    $("courseDetail").innerHTML=`<div class="detail-hero"><div><span class="eyebrow">COURSE OVERVIEW · ${escapeHTML(data.course.category.toUpperCase())}</span><h1>${escapeHTML(data.course.title)}</h1><p>${escapeHTML(data.course.description)}</p><p>Led by ${escapeHTML(data.course.instructor)} · ${escapeHTML(data.course.duration)} · ${escapeHTML(data.course.level)}</p><button class="btn btn-light" onclick="enrollCourse(${id})">Enroll in this course <span>↗</span></button></div><div class="detail-side"><span>📚 <b>${data.lessons.length} lessons</b></span><span>⏱ <b>${escapeHTML(data.course.duration)}</b></span><span>✦ <b>${escapeHTML(data.course.level)}</b></span></div></div><div class="lesson-list"><h2>What you'll learn</h2>${data.lessons.map((l,i)=>`<div class="lesson-row"><div class="lesson-number">${String(i+1).padStart(2,"0")}</div><div class="lesson-text"><b>${escapeHTML(l.title)}</b><small>Lesson ${i+1} · Reading and examples</small></div><button onclick="tryLesson(${l.id},${id})">Preview lesson ↗</button></div>`).join("")}</div>`;
    showPage("course");
  } catch(err){showToast(err.message);}
}
async function tryLesson(lessonId,courseId) {
  if (!currentUser) { showToast("Create an account and enroll to study lessons."); openAuth("register"); return; }
  try { await api(`/api/lessons/${lessonId}`); openLesson(lessonId); }
  catch { showToast("Enroll in this course first to access the lesson."); }
}
async function enrollCourse(id) {
  if (!currentUser) { openAuth("login"); return; }
  try { const result=await api(`/api/courses/${id}/enroll`,{method:"POST",body:"{}"}); showToast(result.message); await loadDashboard(); }
  catch(err){ if(err.message.toLowerCase().includes("log in"))openAuth("login"); else showToast(err.message); }
}
async function loadDashboard() {
  const target=$("dashboardContent");
  if (!currentUser) {
    target.innerHTML='<div class="empty-state"><h3>Your learning journey is waiting.</h3><p>Log in or create a free account to view your enrolled courses and progress.</p><button class="btn btn-primary" onclick="openAuth(\'login\')">Log in</button> <button class="btn btn-outline" onclick="openAuth(\'register\')">Create account</button></div>';return;
  }
  try {
    const courses=await api("/api/my-courses");
    if(!courses.length){target.innerHTML='<div class="empty-state"><h3>Your first course is one click away.</h3><p>Explore the library and enroll in a course to see it here.</p><button class="btn btn-primary" onclick="showPage(\'home\')">Explore courses</button></div>';return;}
    target.innerHTML=`<div class="dashboard-grid">${courses.map(c=>`<article class="dash-card"><div class="course-meta"><span>${escapeHTML(c.category)}</span><span class="level-pill">${c.progress===100?"Completed":c.progress+"% complete"}</span></div><h3>${escapeHTML(c.title)}</h3><p>${escapeHTML(c.description)}</p><div class="progress-head"><span>${c.completed_count} of ${c.lesson_count} lessons completed</span><b>${c.progress}%</b></div><div class="progress-track"><span style="width:${c.progress}%"></span></div><div class="dash-actions"><button class="btn btn-primary" onclick="openCourse(${c.id})">${c.progress===100?"Review course":"Continue learning"} ↗</button></div></article>`).join("")}</div>`;
  } catch(err){target.innerHTML=`<div class="empty-state">${escapeHTML(err.message)}</div>`;}
}
async function openLesson(id) {
  try {
    const lesson=await api(`/api/lessons/${id}`); currentLesson=lesson;
    const index=lesson.lesson_list.findIndex(l=>l.id===id), previous=lesson.lesson_list[index-1], next=lesson.lesson_list[index+1];
    $("lessonDetail").innerHTML=`<div class="lesson-layout"><article class="lesson-main"><span class="eyebrow dark-eyebrow">${escapeHTML(lesson.course_title.toUpperCase())} · LESSON ${index+1} OF ${lesson.lesson_list.length}</span><h1>${escapeHTML(lesson.title)}</h1><div class="lesson-content">${escapeHTML(lesson.content)}</div><div class="lesson-actions">${previous?`<button class="btn btn-outline" onclick="openLesson(${previous.id})">← Previous</button>`:""}<button class="btn btn-primary" onclick="markComplete(${id})">${lesson.completed?"✓ Completed":"Mark as complete ✓"}</button>${next?`<button class="btn btn-outline" onclick="openLesson(${next.id})">Next lesson →</button>`:`<button class="btn btn-outline" onclick="showPage('dashboard')">Back to my learning</button>`}</div></article><aside class="lesson-sidebar"><h3>Course lessons</h3>${lesson.lesson_list.map((l,i)=>`<button class="sidebar-lesson ${l.id===id?"current":""}" onclick="openLesson(${l.id})">${i+1}. ${escapeHTML(l.title)}</button>`).join("")}</aside></div>`;
    showPage("lesson");
  } catch(err){showToast(err.message);}
}
async function markComplete(id) {
  try { const result=await api(`/api/lessons/${id}/complete`,{method:"POST",body:"{}"}); showToast(`${result.message} Course progress: ${result.progress}%.`); await openLesson(id); }
  catch(err){showToast(err.message);}
}
(async function init(){await checkUser();await loadCategories();await loadCourses();})();
