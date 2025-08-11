
import os, requests
def tts_elevenlabs(text: str, voice_id: str="Rachel", stability=0.5, similarity=0.7):
    key=os.getenv("ELEVENLABS_API_KEY")
    if not key: raise RuntimeError("ELEVENLABS_API_KEY missing")
    url=f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    r=requests.post(url, headers={"xi-api-key": key, "accept":"audio/mpeg", "content-type":"application/json"},
        json={"text": text, "model_id":"eleven_multilingual_v2","voice_settings":{"stability": stability, "similarity_boost": similarity}}, timeout=20)
    r.raise_for_status()
    return r.content
