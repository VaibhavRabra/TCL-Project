(function(){
  // Lead-capture webhook. This is the same Make.com hook the India resources site posts to;
  // submissions from this site are tagged src=mecca_gated_asset and campaign="Mecca gated asset - ...".
  // Replace it here if Mecca leads should go to a different scenario.
  var HOOK="https://hook.eu1.make.com/v3115xrk6eh0dy253ob2544jls52ntqn";
  var KEY="tclm_unlocked";
  function q(n){try{return new URLSearchParams(location.search).get(n)||""}catch(e){return""}}
  function reveal(scroll){
    ["gate","why","cta"].forEach(function(id){var e=document.getElementById(id);if(e)e.style.display="none"});
    var a=document.getElementById("asset");if(a){a.style.display="block";if(scroll)a.scrollIntoView({behavior:"smooth"})}
    if(window.onUnlock)window.onUnlock();
  }
  var f=document.getElementById("leadform");
  try{if(!window.noAutoUnlock&&localStorage.getItem(KEY)==="1"&&f){reveal(false);return}}catch(e){}
  if(!f)return;
  f.addEventListener("submit",function(ev){
    ev.preventDefault();
    var quiz=document.getElementById("quiz");
    if(quiz){for(var i=0;i<10;i++){if(!document.querySelector('input[name=q'+i+']:checked')){var el=document.querySelector('input[name=q'+i+']');if(el){el.closest(".q").scrollIntoView({behavior:"smooth",block:"center"});el.focus()}return}}}
    var d=new FormData(f),p=new URLSearchParams();
    d.forEach(function(v,k){p.append(k,v)});
    p.append("src","mecca_gated_asset");p.append("region","Middle East");p.append("page_url",location.href.split("?")[0]);
    p.append("utm_source",q("src")||q("utm_source"));p.append("sender",q("s"));p.append("contact_uid",q("c"));
    if(window.extraPayload)window.extraPayload(p);
    p.append("submitted_at",new Date().toISOString());
    var b=f.querySelector("button");if(b){b.disabled=true;b.textContent="Unlocking…"}
    fetch(HOOK,{method:"POST",mode:"no-cors",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:p.toString()}).catch(function(){}).then(function(){
      try{localStorage.setItem(KEY,"1")}catch(e){}
      reveal(true);
    });
  });
})();
