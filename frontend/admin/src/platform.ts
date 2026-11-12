import { reactive } from 'vue'
export const platform=reactive({name:'云枢智学',description:'',logo_file_id:null as number|null,avatar_file_id:null as number|null})
export async function loadPlatform(){try{const r=await fetch('/api/v1/platform/settings');if(r.ok)Object.assign(platform,(await r.json()).data)}catch{/* Keep bundled branding while offline. */}}
