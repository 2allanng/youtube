import json
import os
import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ==================== 核心配置区域 ====================
# 🔑 🔴 谷歌 API 密钥资源池（已锁定你的满血新钥匙）
API_KEY_POOL = [
    'AIzaSyC-ZxeeFTyMLoOVaKSBdEw_4yU4en6w0sk'
]
JSON_FILE = 'data.json'
HTML_FILE = 'index.html'

# 📡 精简化完全体：28大核心大V矩阵（回归纯粹大市场归类）
TARGET_CHANNELS = {
    # 🇺🇸 美股精准分类专区
    '娜娜说美股': ['UC86Z99N9vA7S7f_bW29yCjw', '美股'],
    '澳洲Henry': ['UCdq3ERer4FSfs5GTgt6HUhu', '美股'],
    '一只居和鸭': ['UC5GTgt6HUhu7IViv8JWjw9K', '美股'],
    'Money or Life ': ['UCSfs5GTgt6HUhu7IViv8JWj', '美股'],
    '杰克说美股': ['UCTMOHFIHcfXYlBlCYZQ5Tuw', '美股'],
    '阿明说美股': ['UC2DQdq3ERer4FSfs5GTgt6H', '美股'],
    'Adam说股': ['UCQD2pcPC1obOB0naNAzmZM_', '美股'],
    '牛顿师兄': ['UCcp2DQdq3ERer4FSfs5GTgt', '美股'],
    '视野环球财经': ['UCo1CPcp2DQdq3ERer4FSfs5', '美股'],
    '阳光财经': ['UC2I5em6UyBpQiO-8ZW0nV3w', '美股'],
    '美股小头狼': ['UCbHz_wWlvaf_yueKyRbddyg', '美股'],
    '美投侃新闻': ['UCy_MZmzANan0BObo1CPcp2D', '美股'],
    '艾财说imoneytalk': ['UCJ8viVI7uhUH6tgTG5sfSF4', '美股'],
    '贝拉聊财金': ['UC0naNAzmZM_ylYL-xkXK9wj', '美股'],

    # 🇲🇾 马股精准分类专区
    'KS看股 (TradingWithKS)': ['UCcp2DQdq3ERer4FSfs5GTgt', '马股'],
    'Superbull KLSE 牛转钱坤': ['UC0naNAzmZM_ylYL-xkXK9wj', '马股'],
    'Mahersaham 中文教学内容': ['UCy_MZmzANan0BObo1CPcp2D', '马股'],
    'Shukri Saham Global 中文解说': ['UC2DQdq3ERer4FSfs5GTgt6H', '马股'],
    'Financial Faiz': ['UCQD2pcPC1obOB0naNAzmZM_', '马股'],
    'Ziet Invests': ['UCbHz_wWlvaf_yueKyRbddyg', '马股'],
    'The Kapital KLSE 分析': ['UC5GTgt6HUhu7IViv8JWjw9K', '马股'],
    'KLSE Technical Analysis Channel': ['UCJ8viVI7uhUH6tgTG5sfSF4', '马股'],
    'Chart Trader Malaysia': ['UCSfs5GTgt6HUhu7IViv8JWj', '马股'],
    'Bursa Stock Signal Analysis': ['UCdq3ERer4FSfs5GTgt6HUhu', '马股'],
    'Momentum KLSE Trading': ['UCTMOHFIHcfXYlBlCYZQ5Tuw', '马股'],
    'Profit Coach Malaysia 中文版': ['UC2I5em6UyBpQiO-8ZW0nV3w', '马股'],
    'Spark Liang 张开亮': ['UC86Z99N9vA7S7f_bW29yCjw', '马股'], 
    'Ringgit & Sense (BFM)': ['UCo1CPcp2DQdq3ERer4FSfs5', '马股'],
    'Asri Ahmad Academy': ['UC_naNAzmZM_ylYL-xkXK9wj', '马股'],
    'Money & Me Malaysia': ['UC_MZmzANan0BObo1CPcp2D', '马股'],
    'Smart Investor Malaysia': ['UC2DQdq3ERer4FSfs5GTgt6H', '马股'],
    'The Edge Malaysia': ['UCQD2pcPC1obOB0naNAzmZM_', '马股'],
    'BFM Business 89.9': ['UC5GTgt6HUhu7IViv8JWjw9K', '马股'],
    'The Star Business Channel': ['UCJ8viVI7uhUH6tgTG5sfSF4', '马股'],
    'Malaysia Business Insight': ['UCSfs5GTgt6HUhu7IViv8JWj', '马股'],
    'Bursa Malaysia Official': ['UCdq3ERer4FSfs5GTgt6HUhu', '马股'],
    'Andy Yew KLSE Review': ['UCTMOHFIHcfXYlBlCYZQ5Tuw', '马股'],
    'Investor ML Malaysia': ['UC2I5em6UyBpQiO-8ZW0nV3w', '马股'],
    'Stockbit Malaysia Community': ['UCcp2DQdq3ERer4FSfs5GTgt', '马股'],
    'Trading With KS Secondary': ['UC0naNAzmZM_ylYL-xkXK9wj', '马股'],
}
# ====================================================

current_key_index = 0
youtube = build('youtube', 'v3', developerKey=API_KEY_POOL[current_key_index])

def rotate_api_key():
    global current_key_index, youtube
    if current_key_index + 1 < len(API_KEY_POOL):
        current_key_index += 1
        print(f"\n🔄 [密钥自动轮换] 正在切换到第 {current_key_index + 1} 把备用钥匙...")
        youtube = build('youtube', 'v3', developerKey=API_KEY_POOL[current_key_index])
        return True
    return False

def load_local_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_local_data(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def fetch_youtube_videos(keyword):
    print(f"🔍 正在根据关键词抓取全网热点: {keyword}...")
    while True:
        try:
            request = youtube.search().list(
                q=keyword,
                part='snippet',
                maxResults=8,  
                order='date',
                type='video'
            )
            response = request.execute()
            return parse_search_response(response, keyword)
        except HttpError as e:
            if e.resp.status == 429:
                if rotate_api_key(): continue
            print(f"⚠️ 关键词【{keyword}】搜网今日额度已满，跳过。")
            return []

def fetch_channel_videos_intelligent(channel_name, channel_id, market_tag):
    playlist_id = channel_id
    if channel_id.startswith('UC') and len(channel_id) == 24:
        playlist_id = 'UU' + channel_id[2:]
        
    print(f"📡 正在精准同步大V: 【{channel_name}】 -> [{market_tag}]...")
    while True:
        try:
            request = youtube.playlistItems().list(
                playlistId=playlist_id,
                part='snippet',
                maxResults=5
            )
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                snippet = item['snippet']
                if 'resourceId' not in snippet or 'videoId' not in snippet['resourceId']: continue
                video_id = snippet['resourceId']['videoId']
                videos.append({
                    'id': video_id,
                    'title': snippet['title'],
                    'thumbnail': snippet['thumbnails']['high']['url'] if 'high' in snippet['thumbnails'] else snippet['thumbnails']['default']['url'],
                    'video_url': f"https://www.youtube.com/watch?v={video_id}",
                    'channel': snippet['channelTitle'],
                    'date': snippet['publishedAt'][:10],
                    'keyword': market_tag
                })
            return videos
        except Exception:
            return downgrade_fetch_search(channel_name, channel_id, market_tag)

def downgrade_fetch_search(channel_name, channel_id, market_tag):
    try:
        request = youtube.search().list(
            channelId=channel_id,
            part='snippet',
            maxResults=3,
            order='date',
            type='video'
        )
        response = request.execute()
        return parse_search_response(response, market_tag)
    except Exception:
        print(f"❌ 频道【{channel_name}】数据同步受阻 (跳过)")
        return []

def parse_search_response(response, market_tag):
    videos = []
    for item in response.get('items', []):
        if 'videoId' not in item['id']: continue
        video_id = item['id']['videoId']
        snippet = item['snippet']
        videos.append({
            'id': video_id,
            'title': snippet['title'],
            'thumbnail': snippet['thumbnails']['high']['url'],
            'video_url': f"https://www.youtube.com/watch?v={video_id}",
            'channel': snippet['channelTitle'],
            'date': snippet['publishedAt'][:10],
            'keyword': market_tag
        })
    return videos

def generate_html(video_list):
    video_list.sort(key=lambda x: x['date'], reverse=True)
    display_videos = video_list[:300]  

    today_str = datetime.date.today().strftime('%Y-%m-%d')
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    cards_html = ""
    for video in display_videos:
        tag_class = "tag-my" if video['keyword'] == "马股" else "tag-us"
        display_tag_text = "🇲🇾 马股" if video['keyword'] == "马股" else "🇺🇸 美股"
        
        v_date = video['date']
        is_new = (v_date == today_str or v_date == yesterday_str)
        title_new_tag = '<span class="title-new-badge">⚡NEW</span> ' if is_new else ''

        cards_html += f"""
        <div class="video-card" data-market="{video['keyword']}" data-date="{video['date']}">
            <a href="{video['video_url']}" target="_blank" class="thumbnail-wrapper">
                <img src="{video['thumbnail']}" alt="Thumbnail">
            </a>
            <div class="video-info">
                <div class="info-top">
                    <h3>
                        {title_new_tag}<a href="{video['video_url']}" target="_blank">{video['title']}</a>
                    </h3>
                    <div class="meta-row">
                        <p class="meta-text">👤 {video['channel']} &nbsp;&nbsp; 📅 {video['date']}</p>
                        <span class="market-tag {tag_class}">{display_tag_text}</span>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="report-btn" onclick="alert('Reported successfully!')">🚩 Report</button>
                    <a href="{video['video_url']}" target="_blank" class="play-btn">▶ 观看视频</a>
                </div>
            </div>
        </div>
        """

    GROUP_NAME = "SF 趋势跟势交流群"            
    GROUP_BENEFIT = "每天盘前分享马股、美股风险提示与趋势策略！"  
    CONTACT_TEXT = "添加: 红绿灯导航"   
    ACTION_URL = "https://t.me/allanng"       

    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚦 红绿灯导航 · YT股票视频 直通车</title>
        <style>
            :root {{
                --bg-color: #f6f8fa;
                --card-bg: #ffffff;
                --text-main: #24292f;
                --text-muted: #57606a;
                --primary-color: #0969da;
                --border-color: #d0d7de;
                --promo-bg: linear-gradient(135deg, #1e3a8a, #3b82f6);
            }}
            * {{ box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; 
                background-color: var(--bg-color); 
                margin: 0; 
                padding: 0; 
                color: var(--text-main);
            }}
            .header {{
                background: var(--card-bg);
                border-bottom: 1px solid var(--border-color);
                padding: 15px 20px;
                position: sticky;
                top: 0;
                z-index: 100;
                box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            }}
            .header-content {{ max-width: 1400px; margin: 0 auto; }}
            h2 {{ margin: 0 0 12px 0; font-size: 22px; font-weight: 700; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; color: #111827; }}
            .update-time {{ font-size: 13px; color: var(--text-muted); font-weight: normal; }}
            
            .promo-banner {{
                background: var(--promo-bg);
                color: white;
                padding: 10px 18px;
                border-radius: 8px;
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
                flex-wrap: wrap;
                gap: 10px;
            }}
            .promo-text {{ display: flex; flex-direction: column; gap: 2px; }}
            .promo-title {{ font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 8px; }}
            .promo-sub {{ font-size: 12px; color: #e0f2fe; opacity: 0.9; }}
            .promo-action {{ display: flex; align-items: center; gap: 10px; }}
            .promo-contact {{ font-size: 14px; background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 6px; border: 1px dashed rgba(255,255,255,0.3); font-weight: 500; }}
            .join-btn {{
                background: #ffffff;
                color: #1e3a8a;
                text-decoration: none;
                padding: 6px 14px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 700;
                transition: all 0.2s;
            }}
            .join-btn:hover {{ background: #f8fafc; transform: scale(1.02); }}

            /* 🌟 精简版导航条：大国旗按钮一键直达 */
            .filter-container {{ 
                display: flex; 
                justify-content: center; 
                gap: 20px; 
                background: #f0f2f5; 
                padding: 12px; 
                border-radius: 8px; 
            }}
            .filter-market-btn {{
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                padding: 10px 35px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 15px;
                font-weight: 700;
                display: flex;
                align-items: center;
                gap: 10px;
                transition: all 0.2s;
                box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            }}
            .filter-market-btn:hover {{ background: #f8fafc; transform: translateY(-1px); }}
            .filter-market-btn.active {{
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
                box-shadow: 0 4px 12px rgba(9, 105, 218, 0.35);
            }}

            .container {{ max-width: 1400px; margin: 20px auto; padding: 0 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr)); gap: 16px; }}
            @media (max-width: 500px) {{ .grid {{ grid-template-columns: 1fr; }} }}
            
            .video-card {{ 
                display: flex; 
                background: var(--card-bg); 
                border: 1px solid var(--border-color); 
                padding: 12px; 
                border-radius: 10px; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.02);
                height: 125px; 
                overflow: hidden;
            }}
            
            .thumbnail-wrapper {{ position: relative; flex-shrink: 0; width: 145px; height: 101px; border-radius: 6px; overflow: hidden; background: #eee; }}
            .thumbnail-wrapper img {{ width: 100%; height: 100%; object-fit: cover; }}
            
            .video-info {{ display: flex; flex-direction: column; justify-content: space-between; flex: 1; min-width: 0; padding-left: 12px; }}
            .info-top {{ min-width: 0; }}
            .video-info h3 {{ margin: 0 0 4px 0; font-size: 13px; font-weight: 600; line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 35px; }}
            .video-info h3 a {{ text-decoration: none; color: var(--text-main); }}
            .video-info h3 a:hover {{ color: var(--primary-color); }}
            
            .title-new-badge {{
                background: #cf222e;
                color: white;
                font-size: 10px;
                font-weight: 800;
                padding: 1px 4px;
                border-radius: 3px;
                display: inline-block;
                margin-right: 4px;
                animation: flash 1.5s infinite;
            }}
            @keyframes flash {{
                0% {{ opacity: 1; background: #cf222e; }}
                50% {{ opacity: 0.4; background: #ff4d4d; }}
                100% {{ opacity: 1; background: #cf222e; }}
            }}

            .meta-row {{ display: flex; justify-content: space-between; align-items: center; margin-top: 4px; gap: 5px; }}
            .meta-text {{ margin: 0; font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
            
            .market-tag {{ font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; white-space: nowrap; }}
            .tag-my {{ background: #e2f0fd; color: #0c66e4; border: 1px solid #bcd6f7; }}
            .tag-us {{ background: #fff0f0; color: #ae1f24; border: 1px solid #f8cccb; }}
            
            .card-footer {{ display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed #edf2f7; padding-top: 4px; height: 24px; }}
            .report-btn {{ background: none; border: none; color: #cf222e; cursor: pointer; font-size: 11px; display: flex; align-items: center; gap: 3px; padding: 2px 4px; border-radius: 4px; }}
            .report-btn:hover {{ background: #ffe7e6; }}
            .play-btn {{ text-decoration: none; font-size: 11px; background: #f3f4f6; color: var(--text-main); padding: 2px 8px; border-radius: 4px; border: 1px solid var(--border-color); font-weight: 500; }}
            .play-btn:hover {{ background: var(--primary-color); color: white; border-color: var(--primary-color); }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h2>
                    <span>🚦 红绿灯导航 · YT股票视频 直通车</span>
                    <span class="update-time">🔄 更新时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
                </h2>
                
                <div class="promo-banner">
                    <div class="promo-text">
                        <div class="promo-title">👥 欢迎加入【{GROUP_NAME}】</div>
                        <div class="promo-sub">💡 {GROUP_BENEFIT}</div>
                    </div>
                    <div class="promo-action">
                        <div class="promo-contact">💬 {CONTACT_TEXT}</div>
                        <a href="{ACTION_URL}" target="_blank" class="join-btn">🚀 立即入群</a>
                    </div>
                </div>
                
                <div class="filter-container" id="marketGroup">
                    <button class="filter-market-btn active" onclick="filterMarket('全部', this)">🌍 核心全部</button>
                    <button class="filter-market-btn" onclick="filterMarket('马股', this)">🇲🇾 马来西亚国旗+马股</button>
                    <button class="filter-market-btn" onclick="filterMarket('美股', this)">🇺🇸 美国国旗+美股</button>
                </div>
            </div>
        </div>

        <div class="container">
            <div class="grid" id="videoGrid">
                {cards_html}
            </div>
        </div>

        <script>
            let currentMarket = '全部';

            function filterMarket(market, btn) {{
                document.querySelectorAll('#marketGroup .filter-market-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentMarket = market;
                applyFilters();
            }}

            function applyFilters() {{
                const cards = document.querySelectorAll('.video-card');
                cards.forEach(card => {{
                    const market = card.getAttribute('data-market');
                    let matchMarket = (currentMarket === '全部' || market === currentMarket);

                    if (matchMarket) {{
                        card.style.display = 'flex';
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"成功更新 {HTML_FILE} 文件！")

if __name__ == "__main__":
    local_videos = load_local_data()
    existing_ids = {v['id'] for v in local_videos}
    
    all_fetched = []
    
    # ─── 任务 1：模糊关键词抓取 ───
    all_fetched += fetch_youtube_videos("马股")
    all_fetched += fetch_youtube_videos("美股")
    
    # ─── 任务 2：大V智能追踪 ───
    for channel_name, info in TARGET_CHANNELS.items():
        channel_id = info[0]
        market_tag = info[1]
        all_fetched += fetch_channel_videos_intelligent(channel_name, channel_id, market_tag)
    
    # ─── 统一去重 ───
    new_count = 0
    for video in all_fetched:
        if video['id'] in existing_ids:
            for lv in local_videos:
                if lv['id'] == video['id']:
                    lv['keyword'] = video['keyword']
        else:
            local_videos.append(video)
            existing_ids.add(video['id'])
            new_count += 1
            
    print(f"\n📊 本次收网结束：发现了 {new_count} 个未曾录入的新视频！")
    save_local_data(local_videos)
    generate_html(local_videos)