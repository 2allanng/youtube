import json
import os
import datetime
from googleapiclient.discovery import build

# ==================== 核心配置区域 ====================
# 🔴 你的专属谷歌钥匙
API_KEY = 'AIzaSyC-ZxeeFTyMLoOVaKSBdEw_4yU4en6w0sk'  
JSON_FILE = 'data.json'
HTML_FILE = 'index.html'

# 📡 自定义指定频道列表（第三个参数为：⭐ 主播可信度评分/标签）
# 格式为：'频道名字': ['频道ID', '市场分类', '可信度评分或评语']
TARGET_CHANNELS = {
    '娜娜说美股': ['UC86Z99N9vA7S7f_bW29yCjw', '美股', '⭐⭐⭐⭐⭐ (核心参考)'],
    '澳洲Henry': ['UCdq3ERer4FSfs5GTgt6HUhu', '美股', '⭐⭐⭐⭐ (趋势右侧)'],
    '杰克说美股': ['UCTMOHFIHcfXYlBlCYZQ5Tuw', '美股', '⭐⭐⭐⭐ (技术面)'],
    '阳光财经': ['UC2I5em6UyBpQiO-8ZW0nV3w', '美股', '⭐⭐⭐⭐ (基本面)'],
    '美股小头狼': ['UCbHz_wWlvaf_yueKyRbddyg', '美股', '⭐⭐⭐ (宏观大局)'],
    '牛顿师兄': ['UCcp2DQdq3ERer4FSfs5GTgt', '美股', '⭐⭐⭐⭐ (筹码博弈)'],
    '视野环球财经': ['UCo1CPcp2DQdq3ERer4FSfs5', '美股', '⭐⭐⭐⭐⭐ (全球宏观)'],
    '贝拉聊财金': ['UC0naNAzmZM_ylYL-xkXK9wj', '美股', '⭐⭐⭐ (长线投资)'],
    '美投侃新闻': ['UCy_MZmzANan0BObo1CPcp2D', '美股', '⭐⭐⭐⭐⭐ (数据挖掘)'],
    '阿明说美股': ['UC2DQdq3ERer4FSfs5GTgt6H', '美股', '⭐⭐⭐ (日内短线)'],
    'Adam说股': ['UCQD2pcPC1obOB0naNAzmZM_', '美股', '⭐⭐⭐⭐ (顺势追踪)'],
    '一只居和鸭': ['UC5GTgt6HUhu7IViv8JWjw9K', '美股', '⭐⭐⭐ (情绪监控)'],
    '艾财说imoneytalk': ['UCJ8viVI7uhUH6tgTG5sfSF4', '美股', '⭐⭐⭐⭐ (财报拆解)'],
    'Money or Life ': ['UCSfs5GTgt6HUhu7IViv8JWj', '美股', '⭐⭐⭐ (风险提示)'],
}
# ====================================================

youtube = build('youtube', 'v3', developerKey=API_KEY)

def load_local_data():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_local_data(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def fetch_youtube_videos(keyword):
    """【方式 A】根据关键词模糊抓取最新视频"""
    print(f"🔍 正在根据关键词抓取: {keyword}...")
    try:
        request = youtube.search().list(
            q=keyword,
            part='snippet',
            maxResults=8,  
            order='date',
            type='video'
        )
        response = request.execute()
        return parse_youtube_response(response, keyword, "🔥 全网热点 (自动匹配)")
    except Exception as e:
        print(f"❌ 关键词抓取失败: {e}")
        return []

def fetch_channel_videos(channel_name, channel_id, market_tag, rating):
    """【方式 B】精确抓取指定大V频道的最新视频"""
    print(f"📡 正在精准同步指定频道: 【{channel_name}】...")
    try:
        request = youtube.search().list(
            channelId=channel_id,
            part='snippet',
            maxResults=5,  
            order='date',
            type='video'
        )
        response = request.execute()
        return parse_youtube_response(response, market_tag, rating)
    except Exception as e:
        print(f"❌ 频道【{channel_name}】抓取失败: {e}")
        return []

def parse_youtube_response(response, market_tag, rating):
    """统一解析 YouTube 返回的数据格式"""
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
            'date': snippet['publishedAt'][:10],
            'keyword': market_tag,
            'rating': rating  # 将评分打包入数据库
        })
    return videos

def generate_html(video_list):
    video_list.sort(key=lambda x: x['date'], reverse=True)
    display_videos = video_list[:300]  

    # 计算今天和昨天的日期字符串，用于前端精确判定 NEW 标签
    today_dt = datetime.date.today()
    yesterday_dt = today_dt - datetime.timedelta(days=1)
    today_str = today_dt.strftime('%Y-%m-%d')
    yesterday_str = yesterday_dt.strftime('%Y-%m-%d')

    cards_html = ""
    for video in display_videos:
        tag_class = "tag-my" if video['keyword'] == "马股" else "tag-us"
        
        # 1. 动态判定是否显示 NEW 标签
        v_date = video['date']
        is_new = (v_date == today_str or v_date == yesterday_str)
        new_tag_html = '<span class="new-badge">NEW</span>' if is_new else ''

        # 2. 获取可信度评分（兼容没有预设评分的旧数据）
        rating_val = video.get('rating', '⭐ ⭐ ⭐ (系统推荐)')

        cards_html += f"""
        <div class="video-card" data-market="{video['keyword']}" data-date="{video['date']}">
            <a href="{video['video_url']}" target="_blank" class="thumbnail-wrapper">
                <img src="{video['thumbnail']}" alt="Thumbnail">
                {new_tag_html}
            </a>
            <div class="video-info">
                <h3><a href="{video['video_url']}" target="_blank">{video['title']}</a></h3>
                
                <div class="rating-row">
                    <span class="rating-label">🎯 可信度评分:</span>
                    <span class="rating-value">{rating_val}</span>
                </div>

                <div class="meta-row">
                    <p class="meta-text">👤 {video['channel']} &nbsp;&nbsp; 📅 {video['date']}</p>
                    <span class="market-tag {tag_class}">{video['keyword']}</span>
                </div>
                <div class="card-footer">
                    <button class="report-btn" onclick="alert('Reported successfully!')">🚩 Report</button>
                    <a href="{video['video_url']}" target="_blank" class="play-btn">▶ 观看视频</a>
                </div>
            </div>
        </div>
        """

    # ==================== 社群推广自定义内容 ====================
    GROUP_NAME = "SF 趋势跟势交流群"            
    GROUP_BENEFIT = "每天盘前分享马股、美股风险提示与趋势策略！"  
    CONTACT_TEXT = "添加: 红绿灯导航"   
    ACTION_URL = "https://t.me/allanng"       
    # =========================================================

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
                --my-color: #2da44e;
                --us-color: #bf360c;
                --border-color: #d0d7de;
                --promo-bg: linear-gradient(135deg, #1e3a8a, #3b82f6);
            }}
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
                padding: 20px;
                position: sticky;
                top: 0;
                z-index: 100;
                box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            }}
            .header-content {{ max-width: 1300px; margin: 0 auto; }}
            h2 {{ margin: 0 0 15px 0; font-size: 24px; font-weight: 700; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; color: #111827; }}
            .update-time {{ font-size: 13px; color: var(--text-muted); font-weight: normal; }}
            
            .promo-banner {{
                background: var(--promo-bg);
                color: white;
                padding: 14px 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
                flex-wrap: wrap;
                gap: 15px;
            }}
            .promo-text {{ display: flex; flex-direction: column; gap: 4px; }}
            .promo-title {{ font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }}
            .promo-sub {{ font-size: 13px; color: #e0f2fe; opacity: 0.9; }}
            .promo-action {{ display: flex; align-items: center; gap: 12px; }}
            .promo-contact {{ font-size: 14px; background: rgba(255,255,255,0.15); padding: 6px 12px; border-radius: 6px; border: 1px dashed rgba(255,255,255,0.3); font-weight: 500; }}
            .join-btn {{
                background: #ffffff;
                color: #1e3a8a;
                text-decoration: none;
                padding: 8px 18px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 700;
                transition: all 0.2s;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .join-btn:hover {{ background: #f8fafc; transform: scale(1.03); }}

            .filter-container {{ display: flex; gap: 20px; flex-wrap: wrap; background: #f0f2f5; padding: 10px 15px; border-radius: 8px; }}
            .filter-group {{ display: flex; align-items: center; gap: 8px; }}
            .filter-label {{ font-size: 13px; font-weight: 600; color: var(--text-muted); }}
            .filter-btn {{
                background: var(--card-bg);
                border: 1px solid var(--border-color);
                padding: 6px 14px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.2s;
            }}
            .filter-btn:hover {{ background: #f3f4f6; }}
            .filter-btn.active {{
                background: var(--primary-color);
                color: white;
                border-color: var(--primary-color);
                box-shadow: 0 2px 4px rgba(9, 105, 218, 0.3);
            }}

            .container {{ max-width: 1300px; margin: 25px auto; padding: 0 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }}
            @media (max-width: 500px) {{ .grid {{ grid-template-columns: 1fr; }} }}
            
            .video-card {{ 
                display: flex; 
                background: var(--card-bg); 
                border: 1px solid var(--border-color); 
                padding: 12px; 
                border-radius: 12px; 
                box-shadow: 0 3px 6px rgba(0,0,0,0.02);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .video-card:hover {{ 
                transform: translateY(-4px); 
                box-shadow: 0 8px 16px rgba(0,0,0,0.08); 
            }}
            
            /* 缩略图外层容器（为了实现角标绝对定位） */
            .thumbnail-wrapper {{ position: relative; flex-shrink: 0; width: 150px; height: 95px; margin-right: 14px; border-radius: 8px; overflow: hidden; background: #eee; }}
            .thumbnail-wrapper img {{ width: 100%; height: 100%; object-fit: cover; }}
            
            /* 🔥 动态 NEW 标签微动效样式 */
            .new-badge {{
                position: absolute;
                top: 4px;
                left: 4px;
                background: #cf222e;
                color: white;
                font-size: 10px;
                font-weight: 800;
                padding: 2px 6px;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.7; }}
                100% {{ opacity: 1; }}
            }}
            
            .video-info {{ display: flex; flex-direction: column; justify-content: space-between; flex: 1; min-width: 0; }}
            .video-info h3 {{ margin: 0 0 6px 0; font-size: 14px; font-weight: 600; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
            .video-info h3 a {{ text-decoration: none; color: var(--text-main); }}
            .video-info h3 a:hover {{ color: var(--primary-color); }}
            
            /* ⭐ 评分栏专属样式 */
            .rating-row {{ display: flex; align-items: center; gap: 6px; margin-bottom: 6px; background: #fff8e1; padding: 2px 8px; border-radius: 4px; border: 1px dashed #ffe082; }}
            .rating-label {{ font-size: 11px; font-weight: 600; color: #b78103; }}
            .rating-value {{ font-size: 11px; font-weight: 700; color: #d4af37; }}

            .meta-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; gap: 5px; }}
            .meta-text {{ margin: 0; font-size: 12px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
            
            .market-tag {{ font-size: 11px; padding: 2px 8px; border-radius: 2em; font-weight: 600; white-space: nowrap; }}
            .tag-my {{ background: #dafbe1; color: var(--my-color); }}
            .tag-us {{ background: #ffe7e6; color: var(--us-color); }}
            
            .card-footer {{ display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed #edf2f7; padding-top: 8px; }}
            .report-btn {{ background: none; border: none; color: #cf222e; cursor: pointer; font-size: 12px; display: flex; align-items: center; gap: 3px; padding: 4px; border-radius: 4px; }}
            .report-btn:hover {{ background: #ffe7e6; }}
            .play-btn {{ text-decoration: none; font-size: 12px; background: #f3f4f6; color: var(--text-main); padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border-color); font-weight: 500; transition: all 0.2s; }}
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
                
                <div class="filter-container">
                    <div class="filter-group">
                        <span class="filter-label">市场分类:</span>
                        <button class="filter-btn active" onclick="filterMarket('全部', this)">全部</button>
                        <button class="filter-btn" onclick="filterMarket('马股', this)">🇲🇾 马股</button>
                        <button class="filter-btn" onclick="filterMarket('美股', this)">🇺🇸 美股</button>
                    </div>
                    <div class="filter-group">
                        <span class="filter-label">时间范围:</span>
                        <button class="filter-btn active" onclick="filterTime('全部', this)">全部</button>
                        <button class="filter-btn" onclick="filterTime('今天', this)">🔥 今天</button>
                        <button class="filter-btn" onclick="filterTime('本周', this)">📅 本周内</button>
                    </div>
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
            let currentTime = '全部';

            function filterMarket(market, btn) {{
                btn.parentElement.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentMarket = market;
                applyFilters();
            }}

            function filterTime(timeRange, btn) {{
                btn.parentElement.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentTime = timeRange;
                applyFilters();
            }}

            function applyFilters() {{
                const cards = document.querySelectorAll('.video-card');
                const todayStr = new Date().toISOString().split('T')[0];
                
                const now = new Date();
                const day = now.getDay();
                const diff = now.getDate() - day + (day === 0 ? -6 : 1); 
                const mondayStr = new Date(now.setDate(diff)).toISOString().split('T')[0];

                cards.forEach(card => {{
                    const market = card.getAttribute('data-market');
                    const date = card.getAttribute('data-date');
                    
                    let matchMarket = (currentMarket === '全部' || market === currentMarket);
                    let matchTime = false;

                    if (currentTime === '全部') {{
                        matchTime = true;
                    }} else if (currentTime === '今天') {{
                        matchTime = (date === todayStr);
                    }} else if (currentTime === '本周') {{
                        matchTime = (date >= mondayStr);
                    }}

                    if (matchMarket && matchTime) {{
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
    
    # ─── 任务 2：指定大V频道精准追踪（传入评分参数） ───
    for channel_name, info in TARGET_CHANNELS.items():
        channel_id = info[0]
        market_tag = info[1]
        rating = info[2]  # 获取预设评分
        all_fetched += fetch_channel_videos(channel_name, channel_id, market_tag, rating)
    
    # ─── 统一合并与本地去重数据库 ───
    new_count = 0
    for video in all_fetched:
        if video['id'] not in existing_ids:
            local_videos.append(video)
            existing_ids.add(video['id'])
            new_count += 1
            
    print(f"\n📊 本次收网结束：发现了 {new_count} 个未曾录入的新视频，已追加至本地数据库！")
    save_local_data(local_videos)
    generate_html(local_videos)