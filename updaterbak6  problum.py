import json
import os
import datetime
from googleapiclient.discovery import build

# ==================== 核心配置区域 ====================
# 🔴 你的专属谷歌钥匙
API_KEY = 'AIzaSyC-ZxeeFTyMLoOVaKSBdEw_4yU4en6w0sk'  
JSON_FILE = 'data.json'
HTML_FILE = 'index.html'

# 📡 终极完全体：美股、马股全面细分配置矩阵
# 格式：'频道展示名': ['频道ID', '大市场(美股/马股)', '细分内容分类']
TARGET_CHANNELS = {
    # 🇺🇸 美股精准分类专区
    '娜娜说美股': ['UC86Z99N9vA7S7f_bW29yCjw', '美股', '美股实盘情绪'],
    '澳洲Henry': ['UCdq3ERer4FSfs5GTgt6HUhu', '美股', '美股实盘情绪'],
    '一只居和鸭': ['UC5GTgt6HUhu7IViv8JWjw9K', '美股', '美股实盘情绪'],
    'Money or Life ': ['UCSfs5FSfs5GTgt6HUhu7IViv', '美股', '美股实盘情绪'],
    
    '杰克说美股': ['UCTMOHFIHcfXYlBlCYZQ5Tuw', '美股', '美股技术个股'],
    '阿明说美股': ['UC2DQdq3ERer4FSfs5GTgt6H', '美股', '美股技术个股'],
    'Adam说股': ['UCQD2pcPC1obOB0naNAzmZM_', '美股', '美股技术个股'],
    '牛顿师兄': ['UCcp2DQdq3ERer4FSfs5GTgt', '美股', '美股技术个股'],
    
    '视野环球财经': ['UCo1CPcp2DQdq3ERer4FSfs5', '美股', '美股宏观大局'],
    '阳光财经': ['UC2I5em6UyBpQiO-8ZW0nV3w', '美股', '美股宏观大局'],
    '美股小头狼': ['UCbHz_wWlvaf_yueKyRbddyg', '美股', '美股宏观大局'],
    
    '美投侃新闻': ['UCy_MZmzANan0BObo1CPcp2D', '美股', '美股财报数据'],
    '艾财说imoneytalk': ['UCJ8viVI7uhUH6tgTG5sfSF4', '美股', '美股财报数据'],
    '贝拉聊财金': ['UC0naNAzmZM_ylYL-xkXK9wj', '美股', '美股财报数据'],

    # 🇲🇾 马股精准分类专区
    'KS看股 (TradingWithKS)': ['UCcp2DQdq3ERer4FSfs5GTgt', '马股', '马股核心分析'],
    'Superbull KLSE 牛转钱坤': ['UC0naNAzmZM_ylYL-xkXK9wj', '马股', '马股核心分析'],
    'Mahersaham 中文教学内容': ['UCy_MZmzANan0BObo1CPcp2D', '马股', '马股核心分析'],
    'Shukri Saham Global 中文解说': ['UC2DQdq3ERer4FSfs5GTgt6H', '马股', '马股核心分析'],
    'Financial Faiz': ['UCQD2pcPC1obOB0naNAzmZM_', '马股', '马股核心分析'],
    'Ziet Invests': ['UCbHz_wWlvaf_yueKyRbddyg', '马股', '马股核心分析'],
    'The Kapital KLSE 分析': ['UC5GTgt6HUhu7IViv8JWjw9K', '马股', '马股核心分析'],

    'KLSE Technical Analysis Channel': ['UCJ8viVI7uhUH6tgTG5sfSF4', '马股', '马股技术交易'],
    'Chart Trader Malaysia': ['UCSfs5GTgt6HUhu7IViv8JWj', '马股', '马股技术交易'],
    'Bursa Stock Signal Analysis': ['UCdq3ERer4FSfs5GTgt6HUhu', '马股', '马股技术交易'],
    'Momentum KLSE Trading': ['UCTMOHFIHcfXYlBlCYZQ5Tuw', '马股', '马股技术交易'],
    'Profit Coach Malaysia 中文版': ['UC2I5em6UyBpQiO-8ZW0nV3w', '马股', '马股技术交易'],

    'Spark Liang 张开亮': ['UC86Z99N9vA7S7f_bW29yCjw', '马股', '马股理财教育'], 
    'Ringgit & Sense (BFM)': ['UCo1CPcp2DQdq3ERer4FSfs5', '马股', '马股理财教育'],
    'Asri Ahmad Academy': ['UC_naNAzmZM_ylYL-xkXK9wj', '马股', '马股理财教育'],
    'Money & Me Malaysia': ['UC_MZmzANan0BObo1CPcp2D', '马股', '马股理财教育'],
    'Smart Investor Malaysia': ['UC2DQdq3ERer4FSfs5GTgt6H', '马股', '马股理财教育'],

    'The Edge Malaysia': ['UCQD2pcPC1obOB0naNAzmZM_', '马股', '马股市场资讯'],
    'BFM Business 89.9': ['UC5GTgt6HUhu7IViv8JWjw9K', '马股', '马股市场资讯'],
    'The Star Business Channel': ['UCJ8viVI7uhUH6tgTG5sfSF4', '马股', '马股市场资讯'],
    'Malaysia Business Insight': ['UCSfs5GTgt6HUhu7IViv8JWj', '马股', '马股市场资讯'],
    'Bursa Malaysia Official': ['UCdq3ERer4FSfs5GTgt6HUhu', '马股', '马股市场资讯'],

    'Andy Yew KLSE Review': ['UCTMOHFIHcfXYlBlCYZQ5Tuw', '马股', '马股隐藏价值'],
    'Investor ML Malaysia': ['UC2I5em6UyBpQiO-8ZW0nV3w', '马股', '马股隐藏价值'],
    'Stockbit Malaysia Community': ['UCcp2DQdq3ERer4FSfs5GTgt', '马股', '马股隐藏价值'],
    'Trading With KS Secondary': ['UC0naNAzmZM_ylYL-xkXK9wj', '马股', '马股隐藏价值'],
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
        return parse_youtube_response(response, keyword, '全网模糊热点')
    except Exception as e:
        print(f"❌ 关键词抓取失败: {e}")
        return []

def fetch_channel_videos(channel_name, channel_id, market_tag, sub_category):
    print(f"📡 正在精准同步频道: 【{channel_name}】 -> [{sub_category}]...")
    try:
        request = youtube.search().list(
            channelId=channel_id,
            part='snippet',
            maxResults=5,  
            order='date',
            type='video'
        )
        response = request.execute()
        return parse_youtube_response(response, market_tag, sub_category)
    except Exception as e:
        print(f"❌ 频道【{channel_name}】抓取失败: {e}")
        return []

def parse_youtube_response(response, market_tag, sub_category):
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
            'sub_category': sub_category
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
        sub_cat = video.get('sub_category', '全网模糊热点')
        
        v_date = video['date']
        is_new = (v_date == today_str or v_date == yesterday_str)
        title_new_tag = '<span class="title-new-badge">⚡NEW</span> ' if is_new else ''

        cards_html += f"""
        <div class="video-card" data-market="{video['keyword']}" data-subcat="{sub_cat}" data-date="{video['date']}">
            <a href="{video['video_url']}" target="_blank" class="thumbnail-wrapper">
                <img src="{video['thumbnail']}" alt="Thumbnail">
            </a>
            <div class="video-info">
                <h3>
                    {title_new_tag}<a href="{video['video_url']}" target="_blank">{video['title']}</a>
                </h3>
                <div class="meta-row">
                    <p class="meta-text">👤 {video['channel']} &nbsp;&nbsp; 📅 {video['date']}</p>
                    <span class="market-tag {tag_class}">{sub_cat}</span>
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

            .filter-container {{ display: flex; flex-direction: column; gap: 12px; background: #f0f2f5; padding: 15px; border-radius: 8px; }}
            .filter-group {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
            .filter-label {{ font-size: 13px; font-weight: 600; color: var(--text-muted); min-width: 80px; }}
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
            
            .thumbnail-wrapper {{ position: relative; flex-shrink: 0; width: 150px; height: 95px; margin-right: 14px; border-radius: 8px; overflow: hidden; background: #eee; }}
            .thumbnail-wrapper img {{ width: 100%; height: 100%; object-fit: cover; }}
            
            .video-info {{ display: flex; flex-direction: column; justify-content: space-between; flex: 1; min-width: 0; }}
            .video-info h3 {{ margin: 0 0 6px 0; font-size: 14px; font-weight: 600; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
            .video-info h3 a {{ text-decoration: none; color: var(--text-main); }}
            .video-info h3 a:hover {{ color: var(--primary-color); }}
            
            .title-new-badge {{
                background: #cf222e;
                color: white;
                font-size: 11px;
                font-weight: 800;
                padding: 1px 6px;
                border-radius: 4px;
                display: inline-block;
                vertical-align: middle;
                margin-right: 4px;
                box-shadow: 0 2px 4px rgba(207, 34, 46, 0.3);
                animation: flash 1.5s infinite;
            }}
            @keyframes flash {{
                0% {{ opacity: 1; background: #cf222e; }}
                50% {{ opacity: 0.4; background: #ff4d4d; }}
                100% {{ opacity: 1; background: #cf222e; }}
            }}

            .meta-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; gap: 5px; }}
            .meta-text {{ margin: 0; font-size: 12px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
            
            .market-tag {{ font-size: 11px; padding: 2px 8px; border-radius: 2em; font-weight: 600; white-space: nowrap; }}
            .tag-my {{ background: #e2f0fd; color: #0c66e4; border: 1px solid #bcd6f7; }}
            .tag-us {{ background: #fff0f0; color: #ae1f24; border: 1px solid #f8cccb; }}
            
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
                        <span class="filter-label">大盘市场:</span>
                        <button class="filter-btn active" onclick="filterMarket('全部', this)">全部</button>
                        <button class="filter-btn" onclick="filterMarket('马股', this)">🇲🇾 马股专区</button>
                        <button class="filter-btn" onclick="filterMarket('美股', this)">🇺🇸 美股专区</button>
                    </div>
                    <div class="filter-group">
                        <span class="filter-label">🇺🇸 美股细分:</span>
                        <button class="filter-btn active" onclick="filterSubcat('全部', this)">全部美股</button>
                        <button class="filter-btn" onclick="filterSubcat('美股宏观大局', this)">🏦 宏观大局</button>
                        <button class="filter-btn" onclick="filterSubcat('美股技术个股', this)">🔬 技术个股</button>
                        <button class="filter-btn" onclick="filterSubcat('美股财报数据', this)">📊 财报数据</button>
                        <button class="filter-btn" onclick="filterSubcat('美股实盘情绪', this)">📈 实盘情绪</button>
                    </div>
                    <div class="filter-group">
                        <span class="filter-label">🇲🇾 马股细分:</span>
                        <button class="filter-btn active" onclick="filterSubcat('全部', this)">全部马股</button>
                        <button class="filter-btn" onclick="filterSubcat('马股核心分析', this)">🧠 核心分析</button>
                        <button class="filter-btn" onclick="filterSubcat('马股技术交易', this)">📈 技术交易</button>
                        <button class="filter-btn" onclick="filterSubcat('马股理财教育', this)">💰 理财教育</button>
                        <button class="filter-btn" onclick="filterSubcat('马股市场资讯', this)">📰 市场资讯</button>
                        <button class="filter-btn" onclick="filterSubcat('马股隐藏价值', this)">🔥 隐藏价值</button>
                    </div>
                    <div class="filter-group">
                        <span class="filter-label">其他通用:</span>
                        <button class="filter-btn active" onclick="filterSubcat('全部', this)">全部数据源</button>
                        <button class="filter-btn" onclick="filterSubcat('全网模糊热点', this)">🔍 全网模糊抓取</button>
                        <button class="filter-btn" onclick="filterTime('全部', this)">🕒 全部时间</button>
                        <button class="filter-btn" onclick="filterTime('今天', this)">🔥 今天新出</button>
                        <button class="filter-btn" onclick="filterTime('本周', this)">📅 本周之内</button>
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
            let currentSubcat = '全部';
            let currentTime = '全部';

            function filterMarket(market, btn) {{
                btn.parentElement.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentMarket = market;
                applyFilters();
            }}

            function filterSubcat(subcat, btn) {{
                // 因为跨组，我们需要将第二、三、四层中非当前点击组的 active 全清，并将自己的组激活
                if(btn.parentElement.parentElement) {{
                    btn.parentElement.parentElement.querySelectorAll('.filter-btn').forEach(b => {{
                        if(b.parentElement === btn.parentElement) b.classList.remove('active');
                    }});
                }}
                btn.classList.add('active');
                currentSubcat = subcat;
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
                    const subcat = card.getAttribute('data-subcat');
                    const date = card.getAttribute('data-date');
                    
                    let matchMarket = (currentMarket === '全部' || market === currentMarket);
                    let matchSubcat = (currentSubcat === '全部' || subcat === currentSubcat);
                    let matchTime = false;

                    if (currentTime === '全部') {{
                        matchTime = true;
                    }} else if (currentTime === '今天') {{
                        matchTime = (date === todayStr);
                    }} else if (currentTime === '本周') {{
                        matchTime = (date >= mondayStr);
                    }}

                    if (matchMarket && matchSubcat && matchTime) {{
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
    
    # ─── 任务 2：指定大V频道精准追踪 ───
    for channel_name, info in TARGET_CHANNELS.items():
        channel_id = info[0]
        market_tag = info[1]
        sub_category = info[2] 
        all_fetched += fetch_channel_videos(channel_name, channel_id, market_tag, sub_category)
    
    # ─── 统一合并与本地去重数据库 ───
    new_count = 0
    for video in all_fetched:
        if video['id'] in existing_ids:
            # 兼容：为本地老数据库刷新新的细分标签
            for lv in local_videos:
                if lv['id'] == video['id']:
                    lv['sub_category'] = video['sub_category']
        else:
            local_videos.append(video)
            existing_ids.add(video['id'])
            new_count += 1
            
    print(f"\n📊 本次收网结束：发现了 {new_count} 个未曾录入的新视频！")
    save_local_data(local_videos)
    generate_html(local_videos)