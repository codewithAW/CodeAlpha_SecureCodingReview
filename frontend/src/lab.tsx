import {useState} from 'react'
const items=[
 ['Record detail','A user requests a single private record. Which lookup enforces ownership?',['ID and session user','ID alone','Client-supplied owner'],0,'Scope the query to both identifiers before returning a row.'],
 ['Password storage','How should a password verifier be stored?',['Reversible encryption','Salted password hash','Encoded plaintext'],1,'A dedicated password hashing function applies a salt and a work factor.'],
 ['Profile output','Which fields should appear in a profile response?',['Every database column','Every non-null field','An explicit list of public fields'],2,'A projection limits what can cross the response boundary.'],
 ['SQL search','How should a search term enter a SQL statement?',['Bound parameter','Formatted string','String concatenation'],0,'Binding keeps values separate from the SQL statement.'],
 ['Session secrets','How should a stable signing key be supplied?',['Source constant','Protected environment variable','Public build variable'],1,'A server-side secret can persist across restarts without reaching the client bundle.'],
 ['Profile edits','What validates an intentional session-backed profile edit?',['A color-coded form','A hidden endpoint','A server-validated CSRF token'],2,'Bind a random token to the session and require it for mutations.'],
 ['Display names','When should a display name be validated?',['On the server before writing','Only on blur','During export'],0,'Validate type, trimmed length and allowed structure before persistence.'],
 ['Access roles','What establishes administrator privileges?',['A URL parameter','The authenticated account’s server-side role','The page title'],1,'Read the role from trusted server state and enforce it at the endpoint.'],
 ['Error handling','What should a client receive on an unexpected database error?',['A traceback','The SQL string','A generic error'],2,'Keep diagnostics in restricted server logs.'],
 ['HTML output','How should a name appear in the browser?',['As an escaped text node','As raw markup','As script text'],0,'Use text rendering or contextual escaping to preserve the data boundary.']
] as const
export function Lab(){
 const [answers,set]=useState<Record<number,number>>(()=>{try{return JSON.parse(localStorage.getItem('cg-lab')||'{}')||{}}catch{return {}}}),[i,go]=useState(0)
 const [topic,prompt,choices,correct,why]=items[i],count=Object.keys(answers).length
 function save(next:Record<number,number>){set(next);try{localStorage.setItem('cg-lab',JSON.stringify(next))}catch{/* unavailable storage */}}
 return <section><small>DEVELOPER EDUCATION</small><h1>Secure coding lab</h1><p>{count} of {items.length} completed · {i<4?'Foundation':'Applied review'}</p><div className="panel"><small>{topic}</small><h2>{prompt}</h2>{choices.map((s,k)=><button className="answer" key={s} disabled={i in answers} onClick={()=>save({...answers,[i]:k})}>{s}</button>)}{i in answers&&<p role="status"><b>{answers[i]===correct?'Correct.':'Recommended: '+choices[correct]+'.'}</b> {why}</p>}</div><div className="actions"><button disabled={i===0} onClick={()=>go(i-1)}>Previous</button><button disabled={i===9} onClick={()=>go(i+1)}>Next decision →</button><button onClick={()=>{save({});go(0)}}>Reset progress</button></div>{count===10&&<p>Completed with {items.filter((v,k)=>v[3]===answers[k]).length} of 10 correct.</p>}</section>
}
