// Public repository telemetry only. No private repos or research-verdict inference.
"use strict";
const fs = require("node:fs");
const path = require("node:path");
function validate(rows) {
  const expected=["principia-artificialis","sovereign-veritas","sovereign-memory-layer","veritas-holo","veritas-science"];
  if(!Array.isArray(rows)||rows.length!==expected.length)throw Error("Unexpected repository set");
  rows.forEach((r,i)=>{
    if(!r||r.repo!==expected[i]||!r.label||!r.role||typeof r.label!=="string"||typeof r.role!=="string"||typeof r.sha!=="string"||!(/^[a-f0-9]{40}$/.test(r.sha))||!(/^\d{4}-\d{2}-\d{2}$/.test(r.date))||Number.isNaN(Date.parse(r.date))||new Date(r.date).toISOString().slice(0,10)!==r.date)throw Error("Invalid row: "+i);
  });
}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&apos;"}[c]));}
function render(rows){
  validate(rows);
  const header='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 426" width="780" height="426" role="img" aria-labelledby="title desc"><title id="title">Sovereign research lab — repository telemetry</title><desc id="desc">'+esc(rows.map(r=>r.label+" "+r.sha.slice(0,12)+" "+r.date).join("; "))+'</desc><rect x="1" y="1" width="778" height="424" rx="18" fill="#0d1117" stroke="#303d4e"/><g font-family="system-ui, sans-serif"><text x="24" y="36" fill="#34d399" font-size="13" font-weight="700" letter-spacing="2">SOVEREIGN / RESEARCH LAB</text><text x="24" y="70" fill="#e6edf3" font-size="27" font-weight="700">Repository command center</text><text x="24" y="92" fill="#a6b6c7" font-size="13">Public main-branch tips • UTC commit dates • not scientific verdicts</text>';
  const cards=rows.map((r,i)=>{
    const y=110+i*54;
    return '<rect x="24" y="'+y+'" width="732" height="47" rx="8" fill="#151e29" stroke="#283848"/><circle cx="41" cy="'+(y+23)+'" r="4" fill="#22d3ee"/><text x="55" y="'+(y+20)+'" fill="#e6edf3" font-size="16" font-weight="600">'+esc(r.label)+'</text><text x="55" y="'+(y+37)+'" fill="#a6b6c7" font-size="12">'+esc(r.role)+'</text><text x="474" y="'+(y+28)+'" fill="#67e8f9" font-family="monospace" font-size="15">'+r.sha.slice(0,12)+'</text><text x="736" y="'+(y+28)+'" text-anchor="end" fill="#c5d0dc" font-size="15">'+r.date+'</text>';
  }).join("");
  return header+cards+'<text x="24" y="405" fill="#a6b6c7" font-size="12">Snapshot refreshes on source changes. See linked research records for evidence and limits.</text></g></svg>\n';
}
function mobileCommand(rows) {
  validate(rows);
  const cards = rows.map((row, index) => {
    const y = 68 + index * 59;
    return `<g transform="translate(16 ${y})"><rect width="296" height="51" rx="7" fill="#151e29"/>
      <text x="10" y="21" font-size="17" font-weight="600">${esc(row.label)}</text>
      <text x="10" y="41" fill="#67e8f9" font-family="monospace">${row.sha.slice(0, 12)}</text>
      <text x="286" y="41" text-anchor="end">${row.date}</text></g>`;
  }).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" width="328" height="370" viewBox="0 0 328 370" role="img" aria-labelledby="title">
    <title id="title">Repository command center, public main branch tips and UTC dates</title>
    <rect width="328" height="370" rx="12" fill="#0d1117"/>
    <g font-family="system-ui,sans-serif" fill="#e6edf3" font-size="14">
    <text x="16" y="29" font-size="21" font-weight="700">Repository command center</text>
    <text x="16" y="51" fill="#a6b6c7">Public main branches · UTC commit dates</text>${cards}</g></svg>\n`;
}

function mapSvg(animated = true){
 const nodes=[{x:390,y:65,t:"Veritas Science",sub:"Validation",c:"#34d399"},{x:625,y:137,t:"Sovereign Veritas",sub:"Authorization",c:"#22d3ee"},{x:625,y:300,t:"Memory Layer",sub:"Offline memory",c:"#22d3ee"},{x:390,y:375,t:"Tiny Engine",sub:"Model experiments",c:"#c4b5fd"},{x:155,y:300,t:"Quasar",sub:"Learning research",c:"#c4b5fd"},{x:155,y:137,t:"Veritas Holo",sub:"Geometry",c:"#34d399"}];
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 450" width="780" height="450" role="img" aria-labelledby="title desc"><title id="title">Research ecosystem</title><desc id="desc">Conceptual thematic relationships among Principia Artificialis and six related projects, not software dependencies.</desc>'+(animated?'<style>.orbit{animation:drift 18s linear infinite}@keyframes drift{to{stroke-dashoffset:-72}}@media(prefers-reduced-motion:reduce){.orbit{animation:none}}</style>':'')+'<rect x="1" y="1" width="778" height="448" rx="18" fill="#0d1117" stroke="#303d4e"/><g font-family="system-ui,sans-serif"><text x="24" y="29" fill="#34d399" font-size="13" font-weight="700" letter-spacing="2">RESEARCH ECOSYSTEM</text><ellipse cx="390" cy="219" rx="230" ry="150" stroke="#24465b" stroke-dasharray="3 9" fill="none" class="orbit"/>'+nodes.map(n=>'<path d="M390 219 L'+n.x+' '+n.y+'" stroke="'+n.c+'" stroke-opacity=".5" stroke-width="1.5"/>').join("")+nodes.map(n=>'<rect x="'+(n.x-106)+'" y="'+(n.y-26)+'" width="212" height="52" rx="10" fill="#15202e" stroke="'+n.c+'" stroke-opacity=".75"/><text x="'+n.x+'" y="'+(n.y-3)+'" text-anchor="middle" fill="#e6edf3" font-size="16" font-weight="600">'+n.t+'</text><text x="'+n.x+'" y="'+(n.y+15)+'" text-anchor="middle" fill="#a6b6c7" font-size="12">'+n.sub+'</text>').join("")+'<circle cx="390" cy="219" r="72" fill="#122638" stroke="#22d3ee" stroke-width="2"/><circle cx="390" cy="219" r="81" fill="none" stroke="#22d3ee" stroke-opacity=".25"/><text x="390" y="212" text-anchor="middle" fill="#67e8f9" font-size="19" font-weight="700">PRINCIPIA</text><text x="390" y="235" text-anchor="middle" fill="#e6edf3" font-size="17" font-weight="600">ARTIFICIALIS</text><text x="390" y="430" text-anchor="middle" fill="#a6b6c7" font-size="12">Thematic research map — not an implemented integration or dependency graph.</text></g></svg>\n';
}
const root=path.resolve(__dirname,"..");
const data=path.join(root,"data","research-lab.json");
const command=path.join(root,"assets","research-command.svg");
const map=path.join(root,"assets","research-ecosystem.svg");
async function refresh(rows, fetcher=fetch){
  validate(rows);
  const next=await Promise.all(rows.map(async r=>{
    const response=await fetcher("https://api.github.com/repos/holland202/"+r.repo+"/branches/main",{headers:{"Accept":"application/vnd.github+json","User-Agent":"holland202-public-profile"},signal:AbortSignal.timeout(15000)});
    if(!response.ok)throw Error("Public API unavailable: "+r.repo+" "+response.status);
    const branch=await response.json();
    const timestamp = branch?.commit?.commit?.committer?.date;
    // GitHub returns UTC commit times. Validate the whole value before taking the day.
    if (branch?.name !== "main" || typeof timestamp !== "string" ||
        !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(timestamp)) {
      throw Error("Unexpected branch response: " + r.repo);
    }
    const parsed = new Date(timestamp);
    if (Number.isNaN(parsed.getTime()) || parsed.toISOString() !== timestamp.replace("Z", ".000Z")) {
      throw Error("Invalid UTC commit time: " + r.repo);
    }
    return {...r, sha: branch.commit.sha, date: timestamp.slice(0, 10)};
  }));
  validate(next);
  return next;
}
async function main(){
  const rows=JSON.parse(fs.readFileSync(data,"utf8"));
  validate(rows);
  const mode = process.argv[2];
  if (!["--check", "--refresh"].includes(mode)) throw Error("Use --check or --refresh");
  const snapshot = mode === "--refresh" ? await refresh(rows) : rows;
  const outputs = [
    [command, render(snapshot)],
    [path.join(root, "assets/research-command-mobile.svg"), mobileCommand(snapshot)],
    [map, mapSvg()],
    [path.join(root, "assets/research-ecosystem-static.svg"), mapSvg(false)],
  ];
  if (mode === "--check") {
    for (const [file, contents] of outputs) {
      if (fs.readFileSync(file, "utf8") !== contents) throw Error("Generated asset differs: " + file);
    }
    return;
  }
  for (const [file, contents] of [[data, JSON.stringify(snapshot, null, 2) + "\n"], ...outputs]) {
    fs.writeFileSync(file, contents);
  }
}
module.exports={validate,render,mapSvg,refresh};
if(require.main===module)main().catch(e=>{console.error(e.message);process.exitCode=1;});
