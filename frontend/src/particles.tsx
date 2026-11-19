import { useEffect, useRef, useState } from 'react'
import { Pause, Play, ShieldCheck } from 'lucide-react'

const names = ['Source code', 'Inspection', 'Software bug', 'Access control', 'Verified shield', 'CodeGuard']
function mask(index: number) {
  const c = document.createElement('canvas'); c.width = 320; c.height = 220
  const x = c.getContext('2d')!; x.strokeStyle = x.fillStyle = 'white'
  x.lineWidth = 7; x.lineJoin = x.lineCap = 'round'
  const paths = [
    'M119 61 L69 110 L119 159 M203 61 L253 110 L203 159 M181 53 L141 167',
    'M193 94 A51 51 0 1 1 91 94 A51 51 0 1 1 193 94 M180 133 L229 180',
    'M125 87 Q160 52 195 87 L195 135 Q194 176 160 176 Q126 176 125 135 Z M142 71 L133 56 M178 71 L187 56 M125 96 L99 82 M125 120 H94 M125 144 L99 161 M195 96 L221 82 M195 120 H226 M195 144 L221 161 M160 98 V151',
    'M113 100 H207 V170 H113 Z M132 100 V78 A28 28 0 1 1 188 78 V100 M160 128 V142',
    'M160 39 Q188 57 215 59 V108 Q213 150 160 181 Q107 150 105 108 V59 Q133 57 160 39 Z M134 108 L152 126 L186 90'
  ]
  if(index<5) x.stroke(new Path2D(paths[index]))
  else { x.textAlign='center'; x.font='bold 48px Arial'; x.fillText('CodeGuard',160,123) }
  const data = x.getImageData(0,0,320,220).data, pts:number[][]=[]
  for(let y=0;y<220;y++) for(let j=0;j<320;j++) if(data[(y*320+j)*4+3]>140) pts.push([(j-160)/160,(110-y)/110])
  return pts
}

export function Particles() {
  const canvas=useRef<HTMLCanvasElement>(null), stopped=useRef(false)
  const [paused,setPaused]=useState(false), [fallback,setFallback]=useState(false), [stage,setStage]=useState(0)
  useEffect(()=>{
    const el=canvas.current!, gl=el.getContext('webgl',{alpha:true,antialias:true})
    if(!gl){setFallback(true);return}
    const reduced=matchMedia('(prefers-reduced-motion: reduce)')
    const vertex=`attribute vec3 a;attribute vec3 b;attribute float seed;uniform float mixv;uniform float time;uniform vec2 pointer;uniform vec2 scale;varying float light;void main(){vec3 p=mix(a,b,mixv);vec2 delta=p.xy-pointer;float d=length(delta);p.xy+=delta/(d+.001)*.028*exp(-12.*d);p.xy+=.009*sin(time+seed*20.)*(1.-mixv);p.xy+=.012*pointer*p.z;gl_Position=vec4(p.xy*scale/(1.-p.z*.12),0.,1.);gl_PointSize=1.2+1.6*seed;light=.52+.48*pow(abs(sin(time*1.5+seed*32.)),3.);}`
    const fragment=`precision mediump float;varying float light;void main(){float r=length(gl_PointCoord-.5);if(r>.5)discard;gl_FragColor=vec4(mix(vec3(.13,.78,.74),vec3(.88,1.,1.),light*light),light*(1.-smoothstep(.2,.5,r)));}`
    const program=gl.createProgram()!, shaders:WebGLShader[]=[]
    for(const [type,src] of [[gl.VERTEX_SHADER,vertex],[gl.FRAGMENT_SHADER,fragment]] as const){
      const s=gl.createShader(type)!;gl.shaderSource(s,src);gl.compileShader(s);gl.attachShader(program,s);shaders.push(s)
    }
    gl.linkProgram(program)
    if(!gl.getProgramParameter(program,gl.LINK_STATUS)){setFallback(true);gl.deleteProgram(program);shaders.forEach(s=>gl.deleteShader(s));return}
    gl.useProgram(program);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE)
    const n=innerWidth<650?1800:5600
    const buffers:WebGLBuffer[]=[]
    function buffer(data:Float32Array){const b=gl!.createBuffer()!;buffers.push(b);gl!.bindBuffer(gl!.ARRAY_BUFFER,b);gl!.bufferData(gl!.ARRAY_BUFFER,data,gl!.STATIC_DRAW);return b}
    const scatter=buffer(Float32Array.from({length:n*3},()=>Math.random()*3.6-1.8))
    const targets=names.map((_,i)=>{const pts=mask(i), arr=new Float32Array(n*3);for(let k=0;k<n;k++){const p=pts[Math.floor(Math.random()*pts.length)];arr.set([p[0],p[1],Math.random()*.12],k*3)}return buffer(arr)})
    function attr(name:string,b:WebGLBuffer,size:number){const pos=gl!.getAttribLocation(program,name);gl!.bindBuffer(gl!.ARRAY_BUFFER,b);gl!.enableVertexAttribArray(pos);gl!.vertexAttribPointer(pos,size,gl!.FLOAT,false,0,0)}
    attr('seed',buffer(Float32Array.from({length:n},()=>Math.random())),1)
    const u=(name:string)=>gl.getUniformLocation(program,name)
    const mix=u('mixv'),time=u('time'),pointer=u('pointer'),scale=u('scale')
    let px=0,py=0,visible=true,raf=0,last=0,clock=0,current=-1
    const move=(e:PointerEvent)=>{const r=el.getBoundingClientRect();px=2*(e.clientX-r.left)/r.width-1;py=1-2*(e.clientY-r.top)/r.height}
    const leave=()=>{px=py=0}
    function draw(now:number){
      const delta=last?Math.min(64,now-last):0;last=now
      if(visible && !document.hidden){
        if(!stopped.current && !reduced.matches)clock+=delta
        const t=reduced.matches?4*4300+1900:clock, id=Math.floor(t/4300)%6, phase=t%4300
        if(id!==current){current=id;setStage(id)}
        const d=Math.min(devicePixelRatio,1.6),w=Math.round(el.clientWidth*d),h=Math.round(el.clientHeight*d)
        if(el.width!==w||el.height!==h){el.width=w;el.height=h}
        gl!.viewport(0,0,w,h);gl!.clear(gl!.COLOR_BUFFER_BIT)
        attr('a',scatter,3);attr('b',targets[id],3)
        const f=Math.max(0,Math.min(1,phase<1500?phase/1500:phase<3500?1:(4300-phase)/800))
        gl!.uniform1f(mix,f*f*(3-2*f));gl!.uniform1f(time,t/1000);gl!.uniform2f(pointer,px,py)
        gl!.uniform2f(scale,Math.min(1,1.46*h/w)*1.15,Math.min(1,w/(1.46*h))*1.15)
        gl!.drawArrays(gl!.POINTS,0,n)
      }
      if(visible&&!document.hidden)raf=requestAnimationFrame(draw)
    }
    const restart=()=>{cancelAnimationFrame(raf);last=0;if(visible&&!document.hidden)raf=requestAnimationFrame(draw)}
    const observer=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;restart()});observer.observe(el)
    el.addEventListener('pointermove',move);el.addEventListener('pointerleave',leave);document.addEventListener('visibilitychange',restart);restart()
    return ()=>{cancelAnimationFrame(raf);observer.disconnect();el.removeEventListener('pointermove',move);el.removeEventListener('pointerleave',leave);document.removeEventListener('visibilitychange',restart);buffers.forEach(b=>gl.deleteBuffer(b));shaders.forEach(s=>gl.deleteShader(s));gl.deleteProgram(program)}
  },[])
  return <div className="visual"><div className="visualHead"><span>FIG. 01</span> SECURITY SIGNATURES</div><canvas ref={canvas} aria-label="Morphing particle illustration"/>{fallback&&<ShieldCheck className="fallback"/>}<div className="visualFoot"><span>{fallback?'Verified shield':names[stage]}</span>{!fallback&&<button aria-label={paused?'Play animation':'Pause animation'} onClick={()=>{stopped.current=!paused;setPaused(!paused)}}>{paused?<Play size={14}/>:<Pause size={14}/>}</button>}</div></div>
}
