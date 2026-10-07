import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API=(process.env.EXPO_PUBLIC_API_URL||'http://localhost:8000/api/v1').replace(/\/$/,'');
export async function registerForPushNotifications(access:string){
  if(!Device.isDevice) return null;
  const permissions=await Notifications.getPermissionsAsync();
  let finalStatus=permissions.status;
  if(finalStatus!=='granted') finalStatus=(await Notifications.requestPermissionsAsync()).status;
  if(finalStatus!=='granted') return null;
  const token=(await Notifications.getExpoPushTokenAsync()).data;
  await fetch(`${API}/realtime/devices/`,{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${access}`},body:JSON.stringify({token,platform:Device.osName?.toUpperCase()||'ANDROID',provider:'expo',active:true})});
  await AsyncStorage.setItem('agronova_push_token',token);
  return token;
}
export function notificationSocket(access:string,onEvent:(event:any)=>void){
  const base=API.replace(/^http/,'ws').replace(/\/api\/v1$/,'');
  const ws=new WebSocket(`${base}/ws/notifications/?token=${encodeURIComponent(access)}`);
  ws.onmessage=e=>{try{onEvent(JSON.parse(e.data))}catch{}};
  return ws;
}
