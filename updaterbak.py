import json
import os
import datetime
from googleapiclient.discovery import build

# ================= 配置区域 =================
API_KEY = 'AIzaSyC-ZxeeFTyMLoOVaKSBdEw_4yU4en6w0sk'  # 替换成你的 YouTube API Key
JSON_FILE = 'data.json'          # 本地数据存储文件
HTML_FILE = 'index.html'         # 本地生成的网页文件
# ===========================================

youtube = build('youtube', 'v3', developerKey=API_KEY)

def load_local_data():
    """读取本地已经存好的视频数据"""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_local_data(data):
    """保存最新数据到本地电脑"""
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def fetch_youtube_videos(keyword):
    """从 YouTube 抓取最新视频"""
    print(f"正在抓取关键词: {keyword}...")
    try:
        request = youtube.search().list(
            q=keyword,
            part='snippet',
            maxResults=8,  # 每次每个关键词取最新 8 个
            order='date',
            type='video'
        )
        response = request.execute()
        
        videos = []
        for item in response.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            videos.append({
                'id': video_id,
                'title': snippet['title'],
                'thumbnail': snippet['thumbnails']['high']['url'],
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'channel': snippet['channelTitle'],
                'date': snippet['publishedAt'][:10], # 格式化为 YYYY-MM-DD
                'keyword': keyword # 记录是马股还是美股
            })
        return videos
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def generate_html(video_list):
    """读取本地最新的所有数据，生成/更新 index.html"""
    # 按照发布日期倒序排序（最新的在最前面）
    video_list.sort(key=lambda x: x['date'], reverse=True)
    
    # 最多在页面展示最新的 100 条，防止页面过大
    display_videos = video_list[:100]

    cards_html = ""
    for video in display_videos:
        cards_html += f"""
        <div class="video-card">
            <a href="{video['video_url']}" target="_blank">
                <img src="{video['thumbnail']}" alt="Thumbnail">
            </a>
            <div class="video-info">
                <h3><a href="{video['video_url']}" target="_blank">{video['title']}</a></h3>
                <p class="meta">Posted by {video['channel']} at {video['date']} <span class="tag">{video['keyword']}</span></p>
                <button class="report-btn" onclick="alert('Reported!')">Report</button>
            </div>
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <title>我的股票视频看板</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h2 {{ color: #333; border-bottom: 2px solid #ccc; padding-bottom: 5px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 1fr)); gap: 15px; }}
            .video-card {{ display: flex; background: #fff; border: 1px solid #ddd; padding: 10px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .video-card img {{ width: 160px; height: 90px; object-fit: cover; border-radius: 4px; margin-right: 15px; }}
            .video-info {{ display: flex; flex-direction: column; justify-content: space-between; flex: 1; }}
            .video-info h3 {{ margin: 0 0 5px 0; font-size: 14px; line-height: 1.3; }}
            .video-info h3 a {{ text-decoration: none; color: #333; }}
            .video-info h3 a:hover {{ color: #cc0000; }}
            .meta {{ margin: 0; font-size: 12px; color: #666; }}
            .tag {{ background: #eee; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-left: 5px; color: #333; }}
            .report-btn {{ align-self: flex-start; background: none; border: none; color: #0056b3; cursor: pointer; font-size: 12px; padding: 0; margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>From Social Media (更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})</h2>
            <div class="grid">
                {cards_html}
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"成功更新 {HTML_FILE} 文件！")

if __name__ == "__main__":
    # 1. 读取本地现有数据
    local_videos = load_local_data()
    existing_ids = {v['id'] for v in local_videos} # 用集合记录已有视频ID，用于去重
    
    # 2. 抓取线上最新数据
    new_my_stock = fetch_youtube_videos("马股")
    new_us_stock = fetch_youtube_videos("美股")
    all_fetched = new_my_stock + new_us_stock
    
    # 3. 合并并去重
    new_count = 0
    for video in all_fetched:
        if video['id'] not in existing_ids:
            local_videos.append(video)
            new_count += 1
            
    print(f"本次抓取结束。发现了 {new_count} 个新视频并已追加到本地。")
    
    # 4. 保存新数据并刷新 HTML
    save_local_data(local_videos)
    generate_html(local_videos)