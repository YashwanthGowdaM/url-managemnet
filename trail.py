from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = 'dashboard_data.json'

def init_data_file():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "ServiceNow": [
                {"name": "Unified Ops Dashboard", "url": "https://example.com/ops"},
                {"name": "RITM - Monitoring View", "url": "https://example.com/monitoring"}
            ],
            "Kafka Dashboard": [
                {"name": "Confluent Brokers", "url": "https://example.com/brokers"},
                {"name": "Kafka Producer Monitoring", "url": "https://example.com/producers"}
            ],
            "Gemfire Dashboards": [
                {"name": "Gemfire Cluster Metrics", "url": "https://example.com/gemfire"},
                {"name": "Capacity Gemfire Near Month", "url": "https://example.com/capacity"}
            ]
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(initial_data, f, indent=2)

def read_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def write_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ----------------------------------------------------------------
# DARK GLASS THEME TEMPLATE (Fully working)
# ----------------------------------------------------------------
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Platform Monitoring Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg1: #0f2027;
  --bg2: #203a43;
  --bg3: #2c5364;
  --accent1: #7f5af0;
  --accent2: #2cb67d;
  --card-bg: rgba(255,255,255,0.08);
  --text: #e5e5e5;
  --muted: #9ca3af;
  --shadow: 0 8px 30px rgba(0,0,0,0.6);
}
* {margin:0;padding:0;box-sizing:border-box;font-family:'Poppins',sans-serif;}
body {
  background: linear-gradient(135deg,var(--bg1),var(--bg2),var(--bg3));
  color: var(--text);
  min-height: 100vh;
  padding: 30px;
}
header {
  background: var(--card-bg);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 25px 35px;
  box-shadow: var(--shadow);
  margin-bottom: 25px;
  border: 1px solid rgba(255,255,255,0.1);
}
h1 {
  font-size: 28px;
  background: linear-gradient(135deg,var(--accent1),var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
p {color: var(--muted);}
.stats {
  display:flex;gap:20px;margin-top:10px;
}
.stat-item {
  background: linear-gradient(135deg,var(--accent1),var(--accent2));
  color:#fff;padding:8px 18px;border-radius:12px;font-size:14px;
}
.add-form, .card {
  background: var(--card-bg);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 25px;
  box-shadow: var(--shadow);
  border: 1px solid rgba(255,255,255,0.1);
  margin-bottom: 25px;
}
.add-form h2 {
  background: linear-gradient(135deg,var(--accent1),var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 15px;
}
.form-row {display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:15px;}
.form-group label {color:var(--muted);font-size:14px;margin-bottom:5px;display:block;}
.form-group input {
  width:100%;padding:10px;border:none;border-radius:10px;
  background:rgba(255,255,255,0.1);color:#fff;
}
.form-group input:focus {outline:none;background:rgba(255,255,255,0.2);}
.btn {
  background: linear-gradient(135deg,var(--accent1),var(--accent2));
  color:white;border:none;padding:10px 25px;border-radius:10px;
  cursor:pointer;transition:0.3s;
}
.btn:hover {transform:translateY(-3px);}
.dashboard-grid {
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
  gap:25px;
}
.card-header {
  display:flex;justify-content:space-between;align-items:center;
  border-bottom:1px solid rgba(255,255,255,0.1);
  padding-bottom:10px;margin-bottom:15px;
}
.card-title {
  font-size:18px;
  background: linear-gradient(135deg,var(--accent1),var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.delete-category, .delete-link {
  background: linear-gradient(135deg,#ff3b3b,#ff7676);
  border:none;color:white;padding:5px 10px;border-radius:6px;
  cursor:pointer;font-size:12px;
}
.link-item {
  background: rgba(255,255,255,0.05);
  border-radius:10px;padding:8px 12px;margin-bottom:8px;
  display:flex;justify-content:space-between;align-items:center;
}
.link-item:hover {background:rgba(255,255,255,0.1);}
.link-item a {color:#93c5fd;text-decoration:none;font-size:14px;}
.empty-state {text-align:center;padding:40px;background:var(--card-bg);border-radius:20px;}
.notification {
  position:fixed;top:20px;right:20px;
  background:var(--card-bg);backdrop-filter:blur(15px);
  padding:12px 20px;border-radius:10px;box-shadow:var(--shadow);
}
</style>
</head>
<body>
<header>
  <h1>⚡ Platform Monitoring Dashboard</h1>
  <p>Manage and organize all your monitoring links</p>
  <div class="stats">
    <div class="stat-item">📊 <span id="totalCategories">0</span> Categories</div>
    <div class="stat-item">🔗 <span id="totalLinks">0</span> Links</div>
  </div>
</header>

<div class="add-form">
  <h2>➕ Add New Link</h2>
  <form id="linkForm">
    <div class="form-row">
      <div class="form-group">
        <label>📁 Category:</label>
        <input type="text" id="category" required placeholder="e.g., ServiceNow">
      </div>
      <div class="form-group">
        <label>🏷️ Link Name:</label>
        <input type="text" id="linkName" required placeholder="e.g., Ops Dashboard">
      </div>
      <div class="form-group">
        <label>🌐 Link URL:</label>
        <input type="url" id="linkUrl" required placeholder="https://example.com">
      </div>
    </div>
    <button type="submit" class="btn">✨ Add Link</button>
  </form>
</div>

<div class="dashboard-grid" id="dashboard"></div>

<script>
let dashboardData = {};

async function loadData(){
  const res = await fetch('/api/data');
  dashboardData = await res.json();
  renderDashboard();
  updateStats();
}
async function saveData(){
  const res = await fetch('/api/data',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(dashboardData)
  });
  if(res.ok){renderDashboard();updateStats();return true;}
  return false;
}
function updateStats(){
  const totalCategories = Object.keys(dashboardData).length;
  const totalLinks = Object.values(dashboardData).reduce((a,b)=>a+b.length,0);
  document.getElementById('totalCategories').textContent = totalCategories;
  document.getElementById('totalLinks').textContent = totalLinks;
}
function renderDashboard(){
  const c = document.getElementById('dashboard');
  c.innerHTML='';
  const cats = Object.keys(dashboardData);
  if(!cats.length){c.innerHTML='<div class="empty-state"><h3>📭 No links yet</h3></div>';return;}
  cats.forEach(cat=>{
    const links = dashboardData[cat];
    const html = links.map((l,i)=>`
      <li class="link-item">
        <a href="${l.url}" target="_blank">🔗 ${l.name}</a>
        <button class="delete-link" onclick="deleteLink('${cat}',${i})">🗑️</button>
      </li>`).join('');
    const card = document.createElement('div');
    card.className='card';
    card.innerHTML=`
      <div class="card-header">
        <h3 class="card-title">${cat}</h3>
        <button class="delete-category" onclick="deleteCategory('${cat}')">🗑️</button>
      </div>
      <ul>${html}</ul>`;
    c.appendChild(card);
  });
}
async function deleteLink(cat,i){
  if(confirm('Delete link?')){
    dashboardData[cat].splice(i,1);
    if(!dashboardData[cat].length) delete dashboardData[cat];
    if(await saveData()) note('Link deleted');
  }
}
async function deleteCategory(cat){
  if(confirm('Delete category?')){
    delete dashboardData[cat];
    if(await saveData()) note('Category deleted');
  }
}
function note(msg){
  const n=document.createElement('div');
  n.className='notification';
  n.textContent=msg;
  document.body.appendChild(n);
  setTimeout(()=>n.remove(),3000);
}
document.getElementById('linkForm').addEventListener('submit',async e=>{
  e.preventDefault();
  const c=document.getElementById('category').value.trim();
  const n=document.getElementById('linkName').value.trim();
  const u=document.getElementById('linkUrl').value.trim();
  if(!dashboardData[c]) dashboardData[c]=[];
  dashboardData[c].push({name:n,url:u});
  if(await saveData()){note('Link added');e.target.reset();}
});
loadData();
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(read_data())

@app.route('/api/data', methods=['POST'])
def save_data_route():
    data = request.json
    write_data(data)
    return jsonify({"status":"success"})

if __name__ == '__main__':
    init_data_file()
    print("🌐 Running on: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
