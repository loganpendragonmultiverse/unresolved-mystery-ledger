from __future__ import annotations

import json
from typing import Any


def render_html(report: dict[str, Any]) -> str:
    data = json.dumps(report).replace("<", "\\u003c").replace("&", "\\u0026")
    return (
        """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mystery ledger editor</title><style>body{font:17px system-ui;background:#f4f1e9;color:#233d48;max-width:1000px;margin:auto;padding:22px}
section{background:white;border:1px solid #b8c6ce;border-radius:12px;padding:18px;margin:20px 0}label{display:block;margin:12px 0}
input,select,textarea{font:inherit;padding:9px;width:100%;box-sizing:border-box}button{font:inherit;padding:10px;margin:8px 8px 8px 0}
.event{padding:10px;border-left:4px solid #8bb7b6;margin:12px 0}li{margin:8px 0}</style>
<h1>Mystery ledger editor</h1><p>Local author-controlled introductions, clues, promises and resolutions.
This editor contains only the selected report boundary; download does not overwrite the original ledger.</p>
<h2>Chapter timeline</h2><ol id="timeline"></ol><main id="entries"></main>
<button id="add">Add mystery</button><button id="save">Download edited ledger</button><p id="status" role="status"></p>
<script id="data" type="application/json">"""
        + data
        + """</script><script>
const data=JSON.parse(document.getElementById('data').textContent);
function field(parent,item,key,title,options){const label=document.createElement('label');label.textContent=title;
const control=document.createElement(options?'select':'input');if(options){for(const text of options){const option=document.createElement('option');option.value=text;option.textContent=text||'Not set';control.append(option);}}
control.value=item[key]??'';control.addEventListener('input',()=>{item[key]=control.value;timeline();});label.append(control);parent.append(label);}
function timeline(){const target=document.getElementById('timeline');target.replaceChildren();
for(const chapter of data.milestones){const li=document.createElement('li');const label=document.createElement('strong');label.textContent=chapter;li.append(label);
for(const item of data.mysteries){const events=[];if(item.introduced===chapter)events.push('Introduced: '+item.title);
for(const kind of ['clues','promises'])for(const event of item[kind]??[])if(event.at===chapter)events.push(kind+': '+event.text);
if(item.resolved_at===chapter)events.push('Resolution: '+(item.resolution??''));
for(const text of events){const p=document.createElement('p');p.textContent=text;li.append(p);}}target.append(li);}}
function draw(){const root=document.getElementById('entries');root.replaceChildren();
for(const item of data.mysteries){const card=document.createElement('section');
field(card,item,'id','Stable mystery ID');field(card,item,'title','Mystery title');field(card,item,'introduced','Introduced at',data.milestones);
field(card,item,'status','Status',['open','resolved','intentionally_open']);field(card,item,'resolution','Resolution text');field(card,item,'resolved_at','Resolved at',['',...data.milestones]);
for(const kind of ['promises','clues']){const heading=document.createElement('h3');heading.textContent=kind;card.append(heading);
for(const entry of item[kind]??[]){const box=document.createElement('div');box.className='event';field(box,entry,'id',kind==='promises'?'Promise ID for linking':'Clue ID');field(box,entry,'at','Chapter',data.milestones);field(box,entry,'text','Text');
if(kind==='clues'){const label=document.createElement('label');label.textContent='Linked promise IDs (comma separated)';const input=document.createElement('input');input.value=(entry.promise_ids??[]).join(', ');input.addEventListener('input',()=>entry.promise_ids=input.value.split(',').map(s=>s.trim()).filter(Boolean));label.append(input);box.append(label);}card.append(box);}
const add=document.createElement('button');add.textContent='Add '+(kind==='clues'?'clue':'promise');add.addEventListener('click',()=>{item[kind]??=[];item[kind].push({id:kind+'-'+(item[kind].length+1),at:data.milestones[0],text:''});draw();});card.append(add);}
root.append(card);}timeline();}
document.getElementById('add').addEventListener('click',()=>{data.mysteries.push({id:'mystery-'+(data.mysteries.length+1),title:'Untitled mystery',introduced:data.milestones[0],status:'open',clues:[],promises:[]});draw();});
document.getElementById('save').addEventListener('click',()=>{
const ids=data.mysteries.map(item=>item.id);if(new Set(ids).size!==ids.length||data.mysteries.some(item=>!item.id||!item.title||(item.status==='resolved'&&!item.resolution))){document.getElementById('status').textContent='Use unique mystery IDs, titles and a resolution for resolved entries.';return;}
const mysteries=data.mysteries.map(item=>{const copy=JSON.parse(JSON.stringify(item));if(!copy.resolved_at)delete copy.resolved_at;for(const field of ['clues','promises'])for(const entry of copy[field]??[])if(!entry.id)delete entry.id;return copy;});
const url=URL.createObjectURL(new Blob([JSON.stringify({version:1,title:data.title,milestones:data.milestones,mysteries},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='edited-mystery-ledger.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
document.getElementById('status').textContent='Downloaded new input. Run the CLI to validate links and generate updated author-review findings.';});draw();</script></html>"""
    )
