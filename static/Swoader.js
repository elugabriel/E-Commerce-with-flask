class Swoader{constructor(t,e,o){this.color=t||"white",this.bg=o||"rgb(0,0,0,.6)",this.size=e||100}start(){this.loadcon=document.createElement("div"),this.styles=document.createElement("style"),this.styles.innerHTML="@keyframes rotate{\n        100%{transform:rotate(360deg);}\n    }\n     @keyframes textanime {\n        100%{opacity:0.4;};\n        }\n   ",this.loadcon.innerHTML="<div id='loader'></div><div id='lotext'></div>",setTimeout(()=>{document.body.appendChild(this.loadcon),document.body.appendChild(this.styles),this.addStyles()},2)}addText(t,e,o){setTimeout(()=>{this.lotext=document.getElementById("lotext"),this.lotext.innerHTML=t,this.lotext.style.fontSize=e,this.lotext.style.color=o,this.addStyles()},2)}animateText(){setTimeout(()=>{this.lotext.style.animation="textanime 1s alternate infinite"},2)}displayOnlyText(){setTimeout(()=>{this.loader=document.getElementById("loader"),this.loader.style.display="none"},2)}addStyles(){this.loadcon.style.width="100vw",this.loadcon.style.zIndex="9999",this.loadcon.style.height="100vh",this.loadcon.style.backgroundColor=this.bg,this.loadcon.style.justifyContent="center",this.loadcon.style.alignItems="center",this.loadcon.style.position="fixed",this.loadcon.style.display="flex",this.loadcon.style.flexDirection="column",this.loadcon.style.top="0",this.loadcon.style.left="0",this.loader=document.getElementById("loader"),this.loader=document.getElementById("loader"),this.loader.style.width=this.size+"px",this.loader.style.height=this.size+"px",this.loader.style.borderRadius="50%",this.loader.style.border="20px solid "+this.color,this.loader.style.borderLeftColor="transparent",this.loader.style.borderRightColor="transparent",this.loader.style.animation="rotate 800ms linear infinite",this.lotext=document.getElementById("lotext"),this.lotext.style.fontFamily="courier",this.lotext.style.fontWeight="bolder"}removeWhenLoaded(t){setTimeout(()=>{this.loadcon.style.display="none"},t)}removeWhenWindowLoaded(){window.addEventListener("DOMcontentloaded",()=>{setTimeout(()=>{this.loadcon.style.display="none"},3)})}}