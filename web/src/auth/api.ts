const API=(import.meta.env.VITE_API_URL||'http://localhost:8000/api/v1').replace(/\/$/,'');
export type Session={access:string;refresh:string;user:any};
export async function request(path:string, options:RequestInit={}, token?:string){
  const headers=new Headers(options.headers); headers.set('Content-Type','application/json'); if(token) headers.set('Authorization',`Bearer ${token}`);
  const res=await fetch(`${API}${path}`,{...options,headers});
  const text=await res.text(); let body:any={}; try{body=text?JSON.parse(text):{}}catch{}
  if(!res.ok) throw new Error(body?.detail||body?.error?.message||body?.message||`Erro ${res.status}`);
  return body;
}
export async function login(email:string,password:string):Promise<Session>{const body=await request('/auth/token/',{method:'POST',body:JSON.stringify({email,password})}); const user=await request('/auth/me/',{},body.access); return {access:body.access,refresh:body.refresh,user};}
export async function register(data:any):Promise<Session>{const body=await request('/auth/register/',{method:'POST',body:JSON.stringify(data)}); return {access:body.data.access,refresh:body.data.refresh,user:body.data.user};}
export async function me(access:string){return request('/auth/me/',{},access)}
export async function profile(access:string){return request('/auth/profile/',{},access)}
export {API};
