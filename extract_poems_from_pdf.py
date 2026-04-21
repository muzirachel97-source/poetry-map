#!/usr/bin/env python3
"""从《唐诗鉴赏辞典》PDF 提取诗词，带地点证据。"""

import json
import re
import fitz

PDF_PATH = "/mnt/c/liyq/workspace/poetry-map/唐诗鉴赏辞典 (中国古典诗词曲赋鉴赏系列工具书) (周啸天) (z-library.sk, 1lib.sk, z-lib.sk).pdf"
CNKGRAPH_PATH = "/mnt/c/liyq/workspace/poetry-map/cnkgraph_poems.json"
OUTPUT_PATH = "/mnt/c/liyq/workspace/poetry-map/poems_from_pdf.json"

# ── 古地名 → 现代地级市 ──────────────────────────────────
PLACE_TO_CITY = {
    "长安": "西安市", "京兆": "西安市", "咸阳": "咸阳市",
    "金陵": "南京市", "建康": "南京市", "江宁": "南京市", "石头城": "南京市", "秣陵": "南京市",
    "汴京": "开封市", "汴梁": "开封市", "大梁": "开封市",
    "临安": "杭州市", "钱塘": "杭州市", "武林": "杭州市", "西湖": "杭州市",
    "洛阳": "洛阳市", "东都": "洛阳市", "洛城": "洛阳市", "河洛": "洛阳市",
    "成都": "成都市", "锦城": "成都市", "锦官城": "成都市", "益州": "成都市",
    "渭城": "咸阳市",
    "岳阳楼": "岳阳市", "岳阳": "岳阳市", "洞庭": "岳阳市", "巴陵": "岳阳市",
    "黄鹤楼": "武汉市", "武昌": "武汉市", "江夏": "武汉市", "鹦鹉洲": "武汉市", "汉阳": "武汉市",
    "滕王阁": "南昌市", "洪州": "南昌市", "豫章": "南昌市",
    "庐山": "九江市", "匡庐": "九江市", "浔阳": "九江市", "江州": "九江市",
    "彭蠡": "九江市", "香炉峰": "九江市", "西林壁": "九江市", "西林寺": "九江市",
    "东林寺": "九江市", "湓浦": "九江市", "湓城": "九江市",
    "白帝城": "重庆市", "白帝": "重庆市", "夔州": "重庆市", "奉节": "重庆市",
    "瞿塘": "重庆市", "三峡": "重庆市",
    "赤壁": "黄冈市", "黄州": "黄冈市",
    "寒山寺": "苏州市", "姑苏": "苏州市", "吴门": "苏州市", "虎丘": "苏州市",
    "瓜洲": "扬州市", "广陵": "扬州市", "维扬": "扬州市",
    "京口": "镇江市", "润州": "镇江市", "北固山": "镇江市", "北固楼": "镇江市",
    "采石矶": "马鞍山市", "天门山": "马鞍山市", "当涂": "马鞍山市", "牛渚": "马鞍山市",
    "鹳雀楼": "运城市",
    "华山": "渭南市", "华阴": "渭南市", "潼关": "渭南市",
    "泰山": "泰安市",
    "终南山": "西安市", "终南": "西安市", "蓝田": "西安市", "骊山": "西安市",
    "灞桥": "西安市", "灞陵": "西安市", "曲江": "西安市", "乐游原": "西安市",
    "峨眉山": "乐山市", "峨眉": "乐山市",
    "剑门": "广元市", "剑阁": "广元市",
    "阳关": "酒泉市", "玉门关": "酒泉市", "敦煌": "酒泉市",
    "凉州": "武威市", "姑臧": "武威市",
    "襄阳": "襄阳市", "襄州": "襄阳市", "岘山": "襄阳市",
    "荆州": "荆州市", "江陵": "荆州市",
    "宣城": "宣城市", "宣州": "宣城市", "敬亭山": "宣城市",
    "池州": "池州市", "秋浦": "池州市",
    "滁州": "滁州市", "琅琊": "滁州市",
    "楚州": "淮安市",
    "徐州": "徐州市", "彭城": "徐州市",
    "苏州": "苏州市", "吴中": "苏州市",
    "杭州": "杭州市",
    "绍兴": "绍兴市", "会稽": "绍兴市", "越州": "绍兴市", "鉴湖": "绍兴市",
    "永州": "永州市", "零陵": "永州市",
    "柳州": "柳州市",
    "潭州": "长沙市", "长沙": "长沙市",
    "衡阳": "衡阳市", "衡山": "衡阳市", "南岳": "衡阳市",
    "郴州": "郴州市",
    "朗州": "常德市", "桃源": "常德市", "武陵": "常德市",
    "太原": "太原市", "并州": "太原市",
    "幽州": "北京市", "幽州台": "北京市", "蓟": "北京市",
    "扬州": "扬州市",
    "杜陵": "西安市", "少陵": "西安市", "樊川": "西安市",
    "凤翔": "宝鸡市", "岐山": "宝鸡市",
    "剡溪": "绍兴市", "天姥山": "绍兴市",
    "天台山": "台州市", "天台": "台州市",
    "桂林": "桂林市", "广州": "广州市", "番禺": "广州市",
    "福州": "福州市", "泉州": "泉州市",
    "商州": "商洛市", "商山": "商洛市",
    "秦州": "天水市",
    "汉中": "汉中市", "南郑": "汉中市", "梁州": "汉中市",
    "安西": "库车市",
    "邺城": "邯郸市",
    "碣石": "秦皇岛市", "蓬莱": "烟台市",
    "宜昌": "宜昌市", "夷陵": "宜昌市", "峡州": "宜昌市",
    "越城": "绍兴市", "吉水": "吉安市", "青羊": "成都市",
}

TITLE_PLACE_KEYWORDS = sorted(PLACE_TO_CITY.keys(), key=len, reverse=True)

EVIDENCE_PATTERNS = [
    (r'(?:此诗|这首诗|本诗|这首词|此词|该诗)(?:是|乃|系|当)?(?:在|于)(.{2,20}?)(?:时|所作|作|写|创作)', "鉴赏文明确记载"),
    (r'(?:此诗|这首诗|本诗)(?:作|写|创作)于(.{2,20}?)(?:时|期间|途中|之际|。|，|；)', "鉴赏文明确记载"),
    (r'(?:作于|写于|创作于)(.{2,30}?)(?:时|期间|途中|之际|。|，|；|\s)', "鉴赏文明确记载"),
    (r'(?:在|到|至|抵|过|经|游)(.{2,10}?)(?:时所作|时写|所作|作此诗|写此诗|写下|创作)', "鉴赏文记载创作地"),
    (r'(?:途经|路过|行经|经过|游历|游览)(.{2,15}?)(?:时|所作|而作|作|写|，)', "鉴赏文记载途经地"),
    (r'(?:贬谪?|贬为|贬至|贬到|流放|左迁|谪居)(.{2,15}?)(?:时|期间|后|，|。)', "鉴赏文记载贬谪地"),
    (r'到达(.{2,10}?)(?:后|时|，)', "鉴赏文记载到达地"),
]

# cnkgraph 县级名→现代地级市（用于 normalize）
CNKGRAPH_CITY_MAP = {
    "越城": "绍兴市", "吉水": "吉安市", "建阳": "南平市", "青羊": "成都市",
    "奉节": "重庆市", "建德": "杭州市", "西湖": "杭州市", "泰和": "吉安市",
    "江陵": "荆州市", "铅山": "上饶市", "叶县": "平顶山市", "零陵": "永州市",
    "凤翔": "宝鸡市", "市中": "乐山市", "三台": "绵阳市", "崇州": "成都市",
    "忠县": "重庆市", "当涂": "马鞍山市", "大名": "邯郸市", "大荔": "渭南市",
    "莆田": "莆田市", "高邮": "扬州市", "盱眙": "淮安市", "阆中": "南充市",
    "徽州": "黄山市", "星子": "九江市", "贵池": "池州市", "潜山": "安庆市",
    "安陆": "孝感市", "昆山": "苏州市", "灵宝": "三门峡市", "江宁": "南京市",
    "兖州": "济宁市", "定州": "保定市", "登封": "郑州市", "偃师": "洛阳市",
    "华阴": "渭南市", "汝州": "平顶山市", "青州": "潍坊市", "诸城": "潍坊市",
    "武功": "咸阳市", "梓潼": "绵阳市", "剑阁": "广元市",
    "宜阳": "洛阳市", "陕县": "三门峡市", "华县": "渭南市",
    "宿松": "安庆市", "江油": "绵阳市", "滑县": "安阳市",
    "封丘": "新乡市", "乐都": "海东市", "昌平": "北京市",
    "东平": "泰安市", "富县": "延安市", "蒲城": "渭南市",
    "广汉": "德阳市", "户县": "西安市", "鄠县": "西安市",
    "吉木萨尔": "昌吉州", "耒阳": "衡阳市", "周至": "西安市",
    "连州": "清远市", "和县": "马鞍山市", "黄陂": "武汉市",
    "邳州": "徐州市", "泾川": "平凉市", "朝阳": "朝阳市",
}


def _is_author_line(raw):
    """判断一行是否是作者行：2-6个纯汉字（去掉空格/*/全角空格后）。"""
    stripped = raw.replace("　", "").replace("*", "").replace(" ", "").strip()
    if not stripped:
        return False
    if not re.match(r'^[一-鿿]{2,6}$', stripped):
        return False
    return stripped


def parse_pdf():
    """从 PDF 提取全部诗词条目——以鉴赏标记为锚点，向前回溯定位。"""
    doc = fitz.open(PDF_PATH)
    full_text = ""
    for i in range(75, len(doc)):
        full_text += doc[i].get_text()

    lines = full_text.split("\n")

    jianshang_positions = [i for i, l in enumerate(lines) if l.strip() == "鉴赏"]
    sig_positions = [i for i, l in enumerate(lines)
                     if re.match(r'^（[^）]{1,20}）\s*$', l.strip())]

    poems = []
    for j_idx, j_pos in enumerate(jianshang_positions):
        # 从鉴赏行向前回溯，寻找作者行
        # 作者行在诗题和诗文之间，距离鉴赏行通常不超过 80 行
        a_pos = None
        search_start = max(0, j_pos - 100)
        for i in range(j_pos - 1, search_start, -1):
            raw = lines[i].rstrip()
            author_name = _is_author_line(raw)
            if not author_name:
                continue
            # 作者行前面应该有诗题行
            if i == 0:
                continue
            prev = lines[i - 1].strip()
            if not prev or len(prev) > 50 or "。" in prev:
                continue
            # 验证：作者行和鉴赏行之间应有诗文内容（至少几行）
            if j_pos - i < 3:
                continue
            a_pos = i
            break

        if a_pos is None:
            continue

        author_raw = _is_author_line(lines[a_pos].rstrip())
        title_line = lines[a_pos - 1].strip()

        # 诗文：作者行后 → 鉴赏行前（跳过作者简介）
        content_lines_raw = lines[a_pos + 1: j_pos]
        raw_text = ""
        in_bio = False
        for cl in content_lines_raw:
            cl_s = cl.strip()
            if not cl_s:
                continue
            if cl_s == "作者" or cl_s.startswith("*"):
                in_bio = True
                continue
            if in_bio:
                continue
            raw_text += cl_s

        # 去除可能混入的作者简介（含年号/年份/官职等特征）
        bio_pattern = re.compile(
            r'(?:字[^，。]{1,6}，|号[^，。]{1,6}，|'
            r'[（(]\d{3,4}[）)]|'
            r'(?:开元|天宝|大历|贞元|元和|长庆|会昌|大中|乾元|至德|上元|'
            r'永徽|咸亨|仪凤|调露|永隆|开耀|永淳|弘道|嗣圣|垂拱|'
            r'天授|长安|神龙|景龙|先天|景云|太极|延和|'
            r'宝应|广德|永泰|建中|兴元|贞观|武德|显庆|龙朔|麟德|'
            r'咸通|乾符|广明|中和|光启|文德|天复|天祐|'
            r'绍圣|元丰|元祐|熙宁|崇宁|建炎|绍兴)'
            r'[^\n]{0,5}年)'
        )
        bio_start = bio_pattern.search(raw_text)
        if bio_start:
            raw_text = raw_text[:bio_start.start()]

        # 按句末标点分行，还原诗句结构
        raw_text = raw_text.strip()
        verses = re.split(r'(?<=[。？！])', raw_text)
        verses = [v.strip() for v in verses if v.strip()]
        if len(verses) > 1:
            content = "\n".join(verses)
        else:
            content = raw_text

        # 鉴赏文：鉴赏行后 → 下一个署名行
        s_pos = None
        for sp in sig_positions:
            if sp > j_pos:
                s_pos = sp
                break

        if s_pos:
            appr_lines = lines[j_pos + 1: s_pos + 1]
        else:
            next_j = jianshang_positions[j_idx + 1] if j_idx + 1 < len(jianshang_positions) else len(lines)
            appr_lines = lines[j_pos + 1: next_j]
        appr_text = "\n".join(l.strip() for l in appr_lines if l.strip())

        title = title_line.replace("　", " ").strip()
        if not title or not content or len(content) < 5:
            continue
        if len(title) > 40 or "。" in title:
            continue

        poems.append({
            "title": title,
            "author": author_raw,
            "content": content,
            "appreciation": appr_text[:3000],
        })

    return poems


def find_place_in_title(title):
    for keyword in TITLE_PLACE_KEYWORDS:
        if keyword in title:
            city = PLACE_TO_CITY[keyword]
            return city, f"诗题'{title}'含地名'{keyword}'"
    return None


def find_place_in_content(content):
    """从诗文内容中找地名——主要用于"送"类诗的出发地。"""
    for keyword in TITLE_PLACE_KEYWORDS:
        if keyword in content:
            return PLACE_TO_CITY[keyword], f"诗文中提及'{keyword}'"
    return None


def find_place_in_appreciation(appr_text):
    for pattern, desc in EVIDENCE_PATTERNS:
        matches = re.findall(pattern, appr_text)
        for m in matches:
            place_str = m.strip().rstrip("，。；、）")
            for keyword in TITLE_PLACE_KEYWORDS:
                if keyword in place_str:
                    city = PLACE_TO_CITY[keyword]
                    ctx_m = re.search(re.escape(place_str[:8]) + r'.{0,40}', appr_text)
                    ctx = ctx_m.group(0) if ctx_m else place_str
                    return city, f"{desc}：'{ctx}'"

    first300 = appr_text[:400]
    for keyword in TITLE_PLACE_KEYWORDS:
        if keyword not in first300:
            continue
        idx = first300.index(keyword)
        ctx = first300[max(0, idx - 15): idx + len(keyword) + 25]
        triggers = ["作", "写", "游", "过", "到", "至", "经", "贬", "任", "居", "寓", "谪", "赴"]
        if any(w in ctx for w in triggers):
            city = PLACE_TO_CITY[keyword]
            return city, f"鉴赏文提及'{ctx.strip()}'"
    return None


def load_cnkgraph_lookup():
    try:
        with open(CNKGRAPH_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}

    lookup = {}
    for p in data:
        t = p["title"].strip()
        a = p["author"].replace(" ", "").strip()
        c = p["city"]
        key = (t, a)
        if key not in lookup:
            lookup[key] = c
        simple = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩]|其[一二三四五六七八九十]+\s*', '', t).strip()
        if simple and simple != t:
            lookup[(simple, a)] = c
    return lookup


def normalize_city(name):
    if name in PLACE_TO_CITY:
        return PLACE_TO_CITY[name]
    if name in CNKGRAPH_CITY_MAP:
        return CNKGRAPH_CITY_MAP[name]
    if name.endswith(("州", "盟")) and not name.endswith("市"):
        return name + "市"
    if not name.endswith("市"):
        return name + "市"
    return name


def lookup_cnkgraph(title, author, cnk_lookup):
    author_clean = author.replace(" ", "")
    city = cnk_lookup.get((title, author_clean))
    if city:
        return normalize_city(city), f"cnkgraph编年数据：{author}此时期在{city}"

    title_clean = re.sub(r'[（）()\s　]', '', title)
    for (t, a), c in cnk_lookup.items():
        if a != author_clean:
            continue
        t_clean = re.sub(r'[（）()\s　①②③④⑤⑥⑦⑧⑨⑩]', '', t)
        if len(title_clean) >= 3 and (title_clean in t_clean or t_clean in title_clean):
            return normalize_city(c), f"cnkgraph编年数据：{author}此时期在{c}"
    return None


def main():
    print("Step 1: 从 PDF 提取诗词...", flush=True)
    poems = parse_pdf()
    print(f"  提取 {len(poems)} 首", flush=True)

    print("Step 2: 加载 cnkgraph...", flush=True)
    cnk_lookup = load_cnkgraph_lookup()
    print(f"  cnkgraph {len(cnk_lookup)} 条", flush=True)

    print("Step 3: 地点提取...", flush=True)
    by_city = {}
    null_list = []
    stats = {"title": 0, "appreciation": 0, "cnkgraph": 0, "null": 0}

    DEST_PATTERNS = re.compile(r'^送.{1,8}[使赴之归还往去到]')
    for p in poems:
        title, author = p["title"], p["author"]
        title_clean = title.replace(" ", "").replace("　", "")
        place = evidence = None

        is_send_poem = DEST_PATTERNS.match(title_clean)
        if is_send_poem:
            r = find_place_in_content(p["content"])
            if r:
                place, evidence = r
                stats["title"] += 1
        if not place:
            r = find_place_in_title(title)
            if r:
                place, evidence = r
                stats["title"] += 1
        if not place:
            r = find_place_in_appreciation(p["appreciation"])
            if r:
                place, evidence = r
                stats["appreciation"] += 1
        if not place:
            r = lookup_cnkgraph(title, author, cnk_lookup)
            if r:
                place, evidence = r
                stats["cnkgraph"] += 1
        if not place:
            stats["null"] += 1

        entry = {"title": title, "author": author, "content": p["content"], "evidence": evidence}
        if place:
            by_city.setdefault(place, []).append(entry)
        else:
            null_list.append(entry)

    by_city["null"] = null_list
    total_placed = sum(len(v) for k, v in by_city.items() if k != "null")

    print(f"\n=== 统计 ===")
    print(f"总: {len(poems)}  有地点: {total_placed} ({total_placed*100//max(len(poems),1)}%)")
    print(f"  诗题: {stats['title']}  鉴赏: {stats['appreciation']}  cnkgraph: {stats['cnkgraph']}  null: {stats['null']}")
    print(f"城市数: {len(by_city)-1}")

    print(f"\nTop 20:")
    for city, pl in sorted(((k,v) for k,v in by_city.items() if k!="null"), key=lambda x:-len(x[1]))[:20]:
        print(f"  {city}: {len(pl)}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(by_city, f, ensure_ascii=False, indent=2)
    print(f"\n输出: {OUTPUT_PATH}")

    print("\n=== 样本 ===")
    for city in ["西安市", "九江市", "岳阳市", "武汉市", "成都市", "重庆市"]:
        if city in by_city and by_city[city]:
            e = by_city[city][0]
            print(f"  {city}: {e['title']}({e['author']}) | {e['evidence']}")
    print("  null 样本:")
    for e in null_list[:5]:
        print(f"    {e['title']}({e['author']})")


if __name__ == "__main__":
    main()
