import { cpSync, mkdirSync, rmSync, existsSync } from 'node:fs';
mkdirSync('dist',{recursive:true});
for(const name of ['index.html','evidence.html','styles.css','app.js','data.json','favicon.svg','downloads']){
  if(!existsSync(name)) throw new Error(`Missing publication input: ${name}`);
  cpSync(name,`dist/${name}`,{recursive:true});
}
console.log('Static research site built. No runtime data services or fitted model.');
