import urllib.request
import urllib.parse
import json
import hashlib
from datetime import datetime, timezone

def write_bluesky_json1(out_path="./data_temp/bluesky.jsonl"):
    query_text = 'social'
    safe_query = urllib.parse.quote(query_text)
    
    api_url = f"https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?q={safe_query}&limit=100"

    req = urllib.request.Request(api_url, headers={'User-Agent': 'SotonLM-DataEngineering/0.1'})
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            data = json.loads(response.read().decode('utf-8'))
            
            for post_wrapper in data.get('posts', []):
                post = post_wrapper.get('record', {})
                
                raw_text = post.get('text', '')
                fetched_url = post_wrapper.get('uri', '')
                
                timestamp_now = datetime.now(timezone.utc).isoformat()
                post_timestamp = post.get('createdAt', timestamp_now)
                
                fetched_url_hash = hashlib.sha256(fetched_url.encode('utf-8')).hexdigest()
                content_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
                token_length = len(raw_text.split())

                post_title = post.get('title', None)
                post_license = post.get('license', None)
                post_license_type = post.get('license_type', None)

                obj = {
                    "id": f"{fetched_url_hash}_{timestamp_now}",
                    "run_id": "bluesky_urllib_noauth_v1", 
                    "timestamp": post_timestamp,
                    "source": "bluesky",
                    "content_type": "Social",
                    "reqeusted_url": api_url, 
                    "fetched_url": fetched_url,
                    "status_code": status_code,
                    "length": token_length,
                    "raw_content": raw_text,
                    "content_format": "plain text",
                    "content_hash": content_hash,

                    "title": post_title,
                    "license_type": post_license_type,
                    "license": post_license,
                    "robots_txt_content": "User-agent: * Allow: /",
                    "language": "en" 
                }
                
                with open(out_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Network error during fetch: {e}")

if __name__ == "__main__":
    write_bluesky_json1()