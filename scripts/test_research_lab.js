"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const {validate,render,mapSvg,refresh}=require("./research_lab.js");
const rows=require("../data/research-lab.json");
test("snapshot has exact public allowlist and deterministic SVG",()=>{
  validate(rows);
  assert.equal(render(rows),render(rows));
  assert.match(render(rows),/not scientific verdicts/);
  for(const r of rows)assert.ok(render(rows).includes(r.sha.slice(0,12)));
});
test("invalid hash, date, duplicate and extra repo fail closed",()=>{
  for(const mutation of [{sha:"bad"},{date:"2026-02-31"},{repo:rows[1].repo}]){
    assert.throws(()=>validate(rows.map((r,i)=>i===0?{...r,...mutation}:r)));
  }
  assert.throws(()=>validate([...rows,rows[0]]));
});
test("SVG escapes text and offers reduced motion",()=>{
  assert.ok(render(rows.map((r,i)=>i===0?{...r,label:"<test &>"}:r)).includes("&lt;test &amp;&gt;"));
  assert.match(mapSvg(),/prefers-reduced-motion:reduce/);
});
test("refresh is read-only, bounded to public main refs",async()=>{
  const seen=[];
  const out=await refresh(rows,async url=>{
    seen.push(url);
    return {ok:true,json:async()=>({name:"main",commit:{sha:"a".repeat(40),commit:{committer:{date:"2026-11-26T00:00:00Z"}}}})};
  });
  assert.equal(seen.length,5);
  assert.ok(seen.every(u=>u.startsWith("https://api.github.com/repos/holland202/")&&u.endsWith("/branches/main")));
  assert.ok(out.every(r=>r.sha==="a".repeat(40)&&r.date==="2026-11-26"));
});
test("API failure or malformed response rejects entire refresh",async()=>{
  await assert.rejects(refresh(rows,async()=>({ok:false,status:429})));
  await assert.rejects(refresh(rows,async()=>({ok:true,json:async()=>({name:"other"})})));
});
test("one malformed tip rejects a batch of otherwise valid responses", async () => {
  const valid = {sha: "a".repeat(40), date: "2026-11-26T12:00:00Z"};
  for (const invalid of [
    {date: "2026-11-26INVALID"}, {date: "2026-11-26T24:00:00Z"},
    {date: "2026-02-31T12:00:00Z"}, {sha: [valid.sha]},
  ]) {
    await assert.rejects(refresh(rows, async url => {
      const tip = url.includes("/veritas-science/") ? {...valid, ...invalid} : valid;
      return {ok: true, json: async () => ({
        name: "main", commit: {sha: tip.sha, commit: {committer: {date: tip.date}}},
      })};
    }));
  }
});
