#!/usr/bin/env python3
"""从 cnkgraph.com 提取诗词-城市数据"""

import json
import math
import re
import time
import urllib.request

FAMOUS_POETS = [
    "李白", "杜甫", "白居易", "王维", "李商隐",
    "杜牧", "孟浩然", "王昌龄", "岑参", "高适",
    "韩愈", "柳宗元", "刘禹锡", "元稹", "贾岛",
    "温庭筠", "李贺", "王勃", "陈子昂", "张九龄",
    "苏轼", "辛弃疾", "李清照", "陆游", "范仲淹",
    "欧阳修", "王安石", "柳永", "黄庭坚", "秦观",
    "杨万里", "范成大", "文天祥", "姜夔", "晏殊",
    "晏几道", "周邦彦", "张先", "贺铸", "吴文英",
]

COUNTY_TO_PREFECTURE = {
    '越城': '绍兴', '吉水': '吉安', '建阳': '南平', '青羊': '成都',
    '奉节': '重庆', '建德': '杭州', '西湖': '杭州', '泰和': '吉安',
    '江陵': '荆州', '铅山': '上饶', '叶县': '平顶山', '零陵': '永州',
    '和县': '马鞍山', '儋州': '海口', '诸城': '潍坊', '临川': '抚州',
    '修水': '九江', '凤翔': '宝鸡', '建瓯': '南平', '市中': '乐山',
    '三台': '绵阳', '崇州': '成都', '忠县': '重庆', '当涂': '马鞍山',
    '万年': '上饶', '余杭': '杭州', '新昌': '绍兴', '合浦': '北海',
    '桃源': '常德', '永嘉': '温州', '溧阳': '常州', '瑞安': '温州',
    '鄱阳': '上饶', '射洪': '遂宁', '巩县': '郑州', '宜兴': '无锡',
    '余干': '上饶', '永新': '吉安', '宁海': '宁波', '乐平': '景德镇',
    '临安': '杭州', '连州': '清远', '阳羡': '无锡', '临桂': '桂林',
    '庐山': '九江', '祁门': '黄山', '汤阴': '安阳', '蓝田': '西安',
    '新津': '成都', '闽清': '福州', '云安': '达州', '涪陵': '重庆',
    '义乌': '金华', '长洲': '苏州', '武功': '咸阳', '歙县': '黄山',
    '兰溪': '金华', '浦城': '南平', '灵石': '晋中', '合川': '重庆',
    '富阳': '杭州', '德清': '湖州', '桐庐': '杭州', '鹿邑': '周口',
    '平江': '岳阳', '南丰': '抚州', '万安': '吉安', '夷陵': '宜昌',
    '金坛': '常州', '丹阳': '镇江', '万州': '重庆', '彭水': '重庆',
    '库车': '阿克苏', '额济纳旗': '阿拉善盟', '敦煌': '酒泉',
    '巴林左旗': '赤峰',
}


def strip_html(html):
    text = re.sub(r'<span class=["\']inlineComment2["\'][^>]*>.*?</span>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', '', text)
    text = text.replace('&nbsp;', '').replace('&amp;', '&').replace('　', '').strip()
    return text


def extract_poems_from_detail(detail_html, city, lat, lng):
    items = []
    for m in re.finditer(
        r"squareLabel1'>([^<]+)<|<div id='poem_(\d+)' class='_poem'>",
        detail_html
    ):
        if m.group(1):
            items.append(('author', m.group(1)))
        elif m.group(2):
            items.append(('poem_start', m.group(2)))

    parts = re.split(r"<div id='poem_(\d+)' class='_poem'>", detail_html)
    block_by_id = {}
    for i in range(1, len(parts), 2):
        block_by_id[parts[i]] = parts[i + 1] if i + 1 < len(parts) else ''

    poems = []
    current_author = ''
    for item_type, value in items:
        if item_type == 'author':
            current_author = value
        elif item_type == 'poem_start':
            block = block_by_id.get(value, '')
            if not block:
                continue

            title_m = re.search(r"labeling=true'[^>]*>(.*?)</a>", block)
            title = strip_html(title_m.group(1)) if title_m else ''

            author_m = re.search(r'ShowPoemAuthorProfile\(\d+,\s*"[^"]*",\s*"([^"]+)"', block)
            author = author_m.group(1) if author_m else current_author

            sentences = re.findall(
                r"class='poemSentence'[^>]*>(.*?)<div id='poem_sentence_",
                block, re.DOTALL,
            )
            lines = [strip_html(s) for s in sentences]
            content = "\n".join(l for l in lines if l)

            if title and content:
                poems.append({
                    "id": int(value),
                    "title": title,
                    "author": author,
                    "content": content,
                    "city": city,
                    "lat": lat,
                    "lng": lng,
                })

    return poems


def fetch_poet_poems(poet_name):
    url = f"https://cnkgraph.com/Api/Biography/Poems/{urllib.request.quote(poet_name)}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"  Error fetching {poet_name}: {e}")
        return []

    all_poems = []
    for t in data.get('Traces', []):
        for m in (t.get('Markers') or []):
            detail = m.get('Detail') or ''
            city = m.get('Title', '')
            if detail and city:
                all_poems.extend(
                    extract_poems_from_detail(detail, city, m.get('Latitude', 0), m.get('Longitude', 0))
                )
    return all_poems


def normalize_city(name):
    if name.endswith(('州', '盟')):
        return name
    if not name.endswith('市'):
        return name + '市'
    return name


def main():
    # Step 1: fetch reference cities
    print("Fetching reference cities...", flush=True)
    req = urllib.request.Request(
        "https://cnkgraph.com/Api/Biography",
        headers={"Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        main_data = json.loads(resp.read().decode('utf-8'))

    ref_cities = []
    for m in main_data['Traces'][0]['Markers']:
        ref_cities.append({
            'name': m['Title'],
            'lat': m['Latitude'],
            'lng': m['Longitude'],
        })
    print(f"  {len(ref_cities)} reference cities loaded")

    # Step 2: fetch poems for each famous poet
    all_poems = []
    seen_ids = set()

    for i, poet in enumerate(FAMOUS_POETS):
        print(f"[{i + 1}/{len(FAMOUS_POETS)}] {poet}...", end=' ', flush=True)
        poems = fetch_poet_poems(poet)
        new = 0
        for p in poems:
            if p['id'] not in seen_ids:
                seen_ids.add(p['id'])
                all_poems.append(p)
                new += 1
        print(f"{new} new poems (total: {len(all_poems)})", flush=True)
        time.sleep(0.3)

    # Step 3: map to prefectures
    def find_nearest(lat, lng):
        best, best_d = None, 999
        for rc in ref_cities:
            d = math.sqrt((lat - rc['lat']) ** 2 + (lng - rc['lng']) ** 2)
            if d < best_d:
                best_d = d
                best = rc['name']
        return best if best_d < 1.5 else None

    ref_set = {rc['name'] for rc in ref_cities}
    city_poems = {}

    for p in all_poems:
        c = p['city']
        if c in COUNTY_TO_PREFECTURE:
            mapped = COUNTY_TO_PREFECTURE[c]
        elif c in ref_set:
            mapped = c
        else:
            mapped = find_nearest(p['lat'], p['lng'])

        if not mapped:
            continue

        key = normalize_city(mapped)
        if key not in city_poems:
            city_poems[key] = []
        city_poems[key].append({
            'title': p['title'],
            'author': p['author'],
            'content': p['content'],
        })

    # Deduplicate
    for city in city_poems:
        seen = set()
        unique = []
        for p in city_poems[city]:
            k = (p['title'], p['author'])
            if k not in seen:
                seen.add(k)
                unique.append(p)
        city_poems[city] = unique

    total = sum(len(v) for v in city_poems.values())
    empty_author = sum(1 for v in city_poems.values() for p in v if not p['author'])

    print(f"\n=== Final ===")
    print(f"{len(city_poems)} cities, {total} poems, {empty_author} without author")
    print(f"\nTop 30:")
    for city, pl in sorted(city_poems.items(), key=lambda x: -len(x[1]))[:30]:
        print(f"  {city}: {len(pl)}")

    with open("/mnt/c/liyq/workspace/poetry-map/poems_data.json", "w", encoding="utf-8") as f:
        json.dump(city_poems, f, ensure_ascii=False, indent=2)
    print(f"\nSaved poems_data.json")


if __name__ == "__main__":
    main()
