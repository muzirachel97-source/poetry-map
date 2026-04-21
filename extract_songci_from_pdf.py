#!/usr/bin/env python3
"""从《宋词鉴赏辞典》PDF 提取词作，带地点证据。"""

import json
import re
import fitz

PDF_PATH = "/mnt/c/liyq/workspace/poetry-map/宋词鉴赏辞典 中国古典诗词曲赋鉴赏系列工具书 .pdf"
CNKGRAPH_PATH = "/mnt/c/liyq/workspace/poetry-map/cnkgraph_poems.json"
OUTPUT_PATH = "/mnt/c/liyq/workspace/poetry-map/songci_from_pdf.json"

WATERMARK = "更多电子书资料请搜索「雅书」：http://www.yabook.org"

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
    "京口": "镇江市", "润州": "镇江市", "北固山": "镇江市", "北固楼": "镇江市", "北固亭": "镇江市",
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
    "建康": "南京市", "健康": "南京市",
    "越城": "绍兴市", "吉水": "吉安市", "青羊": "成都市",
    "合肥": "合肥市",
    "镇江": "镇江市",
}

TITLE_PLACE_KEYWORDS = sorted(PLACE_TO_CITY.keys(), key=len, reverse=True)

EVIDENCE_PATTERNS = [
    (r'(?:此词|这首词|本词|此诗|这首诗|本诗|该词)(?:是|乃|系|当)?(?:在|于)(.{2,20}?)(?:时|所作|作|写|创作)', "鉴赏文明确记载"),
    (r'(?:此词|这首词|本词)(?:作|写|创作)于(.{2,20}?)(?:时|期间|途中|之际|。|，|；)', "鉴赏文明确记载"),
    (r'(?:作于|写于|创作于)(.{2,30}?)(?:时|期间|途中|之际|。|，|；|\s)', "鉴赏文明确记载"),
    (r'(?:在|到|至|抵|过|经|游)(.{2,10}?)(?:时所作|时写|所作|作此词|写此词|写下|创作)', "鉴赏文记载创作地"),
    (r'(?:途经|路过|行经|经过|游历|游览)(.{2,15}?)(?:时|所作|而作|作|写|，)', "鉴赏文记载途经地"),
    (r'(?:贬谪?|贬为|贬至|贬到|流放|左迁|谪居)(.{2,15}?)(?:时|期间|后|，|。)', "鉴赏文记载贬谪地"),
    (r'到达(.{2,10}?)(?:后|时|，)', "鉴赏文记载到达地"),
    (r'(?:知|守|任|为)(.{2,8}?)(?:知府|知州|太守|通判)', "鉴赏文记载任职地"),
]

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


def parse_pdf():
    """从 PDF 提取全部词作——以鉴赏+署名为锚点。"""
    doc = fitz.open(PDF_PATH)
    full_text = ""
    for i in range(57, len(doc)):
        full_text += doc[i].get_text()

    lines = full_text.split("\n")

    jianshang_pos = [i for i, l in enumerate(lines) if l.strip() == "鉴赏"]
    sig_pos = [i for i, l in enumerate(lines)
               if re.match(r'^（[^）]{1,30}）\s*$', l.strip())]

    current_author = ""
    poems = []

    for j_idx, j_pos in enumerate(jianshang_pos):
        # 定位内容块起点：前一个署名之后
        prev_sigs = [s for s in sig_pos if s < j_pos]
        content_start = prev_sigs[-1] + 1 if prev_sigs else 0

        # 过滤上一首鉴赏溢出的行（上一个鉴赏和当前署名之间可能有残留）
        if j_idx > 0:
            prev_j = jianshang_pos[j_idx - 1]
            if content_start <= prev_j:
                content_start = prev_j + 1
                prev_sigs_after = [s for s in sig_pos if prev_j < s < j_pos]
                if prev_sigs_after:
                    content_start = prev_sigs_after[0] + 1

        block = []
        for k in range(content_start, j_pos):
            line = lines[k].rstrip()
            if WATERMARK in line:
                continue
            if not line.strip():
                continue
            block.append(line.strip())

        if not block:
            continue

        # 去掉 作者 和 注释 段落
        cut_idx = len(block)
        for i, bl in enumerate(block):
            if bl == "作者" or bl == "注释":
                cut_idx = i
                break
        block = block[:cut_idx]

        if not block:
            continue

        # 解析 author* / cipai / subtitle / content
        idx = 0

        # 检查 author* 行
        if block[idx].endswith("*"):
            current_author = block[idx].rstrip("*").replace("　", "").replace(" ", "").strip()
            idx += 1

        if idx >= len(block):
            continue

        cipai = block[idx]
        idx += 1

        # ── 副标题检测 ──
        subtitle = ""
        if idx < len(block) and idx + 1 < len(block):
            candidate = block[idx]
            next_line = block[idx + 1]
            next_first_clause = re.split(r'[，。、？！；]', next_line)[0]
            is_continuation = len(next_first_clause.strip()) <= 2
            if not is_continuation and "。" not in candidate and len(candidate) < 25:
                subtitle = candidate
                idx += 1

        # ── 词文与词序分离 ──
        content_lines = block[idx:]
        raw_text = "".join(content_lines)

        # 去掉可能的作者简介（含年号/年份），只在文本后半段搜索
        bio_pattern = re.compile(
            r'(?:字[^，。]{1,6}，|号[^，。]{1,6}，|'
            r'[（(]\d{3,4}[）)]|'
            r'(?:开元|天宝|大历|贞元|元和|长庆|会昌|大中|乾元|至德|上元|'
            r'永徽|咸亨|仪凤|调露|永隆|开耀|永淳|弘道|嗣圣|垂拱|'
            r'天授|长安|神龙|景龙|先天|景云|太极|延和|'
            r'宝应|广德|永泰|建中|兴元|贞观|武德|显庆|龙朔|麟德|'
            r'咸通|乾符|广明|中和|光启|文德|天复|天祐|'
            r'绍圣|元丰|元祐|熙宁|崇宁|建炎|绍兴|淳熙|庆元|嘉定|'
            r'嘉泰|开禧|宝庆|绍定|端平|嘉熙|淳祐|宝祐|'
            r'开庆|景定|咸淳|德祐|景炎|祥兴|'
            r'天圣|明道|景祐|宝元|康定|庆历|皇祐|至和|嘉祐|治平|'
            r'靖康|隆兴|乾道|大观|政和|宣和|靖国|'
            r'太平兴国|雍熙|端拱|淳化|至道|咸平|景德|大中祥符|天禧)'
            r'[^\n]{0,5}年)'
        )
        search_start = max(50, len(raw_text) // 2)
        bio_start = bio_pattern.search(raw_text, search_start)
        if bio_start:
            raw_text = raw_text[:bio_start.start()]
        raw_text = raw_text.strip()

        # ── 词序（preface）检测 ──
        preface = ""
        prose_markers = re.compile(
            r'(?:^|(?<=[，。、；]))(?:余|予)\w|'
            r'因[作赋]|自度|遂[赋书作]|乃[作赋为足]|'
            r'[丙丁戊己庚辛壬癸甲乙][申酉戌亥子丑寅卯辰巳午未]|'
            r'元丰|淳熙|绍兴|乾道|嘉泰|开禧|建炎|嘉定|端平|绍定|'
            r'咸淳|宝祐|景定|庆元|绍熙|淳祐|隆兴'
        )
        if prose_markers.search(raw_text[:80]):
            segments = re.split(r'(。)', raw_text)
            boundary = 0
            for i in range(0, len(segments) - 1, 2):
                seg = segments[i]
                seg_end = sum(len(segments[j]) for j in range(i + 2))
                if prose_markers.search(seg):
                    boundary = seg_end
                elif boundary > 0:
                    remaining = "".join(segments[i:])
                    if prose_markers.search(remaining[:80]):
                        boundary = seg_end
                    else:
                        break
                else:
                    break
            if 0 < boundary < len(raw_text) - 10:
                preface = raw_text[:boundary].strip()
                raw_text = raw_text[boundary:].strip()
                # 边界后延：把紧跟的散文句也纳入词序
                while len(raw_text) > 10:
                    next_p = raw_text.find('。')
                    if next_p < 0:
                        break
                    next_sent = raw_text[:next_p]
                    is_prose = False
                    if '《' in next_sent or '》' in next_sent:
                        is_prose = True
                    if re.search(r'[也矣焉哉]$', next_sent.strip()):
                        is_prose = True
                    if re.search(r'作此|赋此|名之曰|以授|为谢|为赋', next_sent):
                        is_prose = True
                    if not is_prose:
                        break
                    preface = preface + raw_text[:next_p + 1]
                    raw_text = raw_text[next_p + 1:].strip()
                if not subtitle:
                    first_clause = re.split(r'[，。、]', preface)[0].strip()
                    if first_clause and len(first_clause) <= 15:
                        subtitle = first_clause

        # 无散文标记但首句像词序（短句+以。结尾+以动词开头）
        if not preface and not subtitle:
            first_period = raw_text.find('。')
            if 5 < first_period < 45:
                first_sentence = raw_text[:first_period + 1]
                if re.match(r'^[游登过送寄泊]', first_sentence):
                    first_clause = re.split(r'[，。]', first_sentence)[0].strip()
                    if first_clause and 3 < len(first_clause) <= 15:
                        clauses = re.split(r'[，、？！；]', first_sentence.rstrip('。'))
                        clauses = [c for c in clauses if c.strip()]
                        is_verse = len(clauses) == 2 and abs(len(clauses[0]) - len(clauses[1])) <= 2
                        subtitle = first_clause
                        if not is_verse:
                            preface = first_sentence
                            raw_text = raw_text[first_period + 1:].strip()

        title = f"{cipai}·{subtitle}" if subtitle else cipai

        # 按句末标点分行
        verses = re.split(r'(?<=[。？！])', raw_text)
        verses = [v.strip() for v in verses if v.strip()]
        content = "\n".join(verses) if len(verses) > 1 else raw_text

        # 鉴赏文：鉴赏行 → 下一个署名行
        next_sigs = [s for s in sig_pos if s > j_pos]
        if next_sigs:
            appr_end = next_sigs[0]
        else:
            next_j = jianshang_pos[j_idx + 1] if j_idx + 1 < len(jianshang_pos) else len(lines)
            appr_end = next_j
        appr_lines = [lines[k].strip() for k in range(j_pos + 1, appr_end)
                      if lines[k].strip() and WATERMARK not in lines[k]]
        appr_text = "\n".join(appr_lines)[:3000]

        if not content or len(content) < 5:
            continue
        if not title:
            continue

        poems.append({
            "title": title,
            "author": current_author,
            "content": content,
            "preface": preface,
            "appreciation": appr_text,
        })

    return poems


def find_place_in_title(title):
    for keyword in TITLE_PLACE_KEYWORDS:
        if keyword in title:
            return PLACE_TO_CITY[keyword], f"词题'{title}'含地名'{keyword}'"
    return None


def find_place_in_content(content):
    for keyword in TITLE_PLACE_KEYWORDS:
        if keyword in content:
            return PLACE_TO_CITY[keyword], f"词文中提及'{keyword}'"
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

    first400 = appr_text[:400]
    for keyword in TITLE_PLACE_KEYWORDS:
        if keyword not in first400:
            continue
        idx = first400.index(keyword)
        ctx = first400[max(0, idx - 15): idx + len(keyword) + 25]
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
    # 宋词标题格式：词牌名·副标题 或 词牌名
    # cnkgraph 里可能只存词牌名或副标题
    for try_title in [title, title.split("·")[0], title.split("·")[-1] if "·" in title else ""]:
        if not try_title:
            continue
        city = cnk_lookup.get((try_title, author_clean))
        if city:
            return normalize_city(city), f"cnkgraph编年数据：{author}此时期在{city}"

    title_clean = re.sub(r'[（）()\s　·]', '', title)
    for (t, a), c in cnk_lookup.items():
        if a != author_clean:
            continue
        t_clean = re.sub(r'[（）()\s　①②③④⑤⑥⑦⑧⑨⑩·]', '', t)
        if len(title_clean) >= 3 and (title_clean in t_clean or t_clean in title_clean):
            return normalize_city(c), f"cnkgraph编年数据：{author}此时期在{c}"
    return None


def main():
    print("Step 1: 从 PDF 提取词作...", flush=True)
    poems = parse_pdf()
    print(f"  提取 {len(poems)} 首", flush=True)

    # 统计作者
    authors = set(p["author"] for p in poems)
    print(f"  词人 {len(authors)} 位", flush=True)

    print("Step 2: 加载 cnkgraph...", flush=True)
    cnk_lookup = load_cnkgraph_lookup()
    print(f"  cnkgraph {len(cnk_lookup)} 条", flush=True)

    print("Step 3: 地点提取...", flush=True)
    by_city = {}
    null_list = []
    stats = {"title": 0, "appreciation": 0, "cnkgraph": 0, "null": 0}

    for p in poems:
        title, author = p["title"], p["author"]
        place = evidence = None

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

        entry = {"title": title, "author": author, "content": p["content"], "preface": p.get("preface", ""), "evidence": evidence}
        if place:
            by_city.setdefault(place, []).append(entry)
        else:
            null_list.append(entry)

    by_city["null"] = null_list
    total_placed = sum(len(v) for k, v in by_city.items() if k != "null")

    print(f"\n=== 统计 ===")
    print(f"总: {len(poems)}  有地点: {total_placed} ({total_placed*100//max(len(poems),1)}%)")
    print(f"  词题: {stats['title']}  鉴赏: {stats['appreciation']}  cnkgraph: {stats['cnkgraph']}  null: {stats['null']}")
    print(f"城市数: {len(by_city)-1}")

    print(f"\nTop 20:")
    for city, pl in sorted(((k,v) for k,v in by_city.items() if k!="null"), key=lambda x:-len(x[1]))[:20]:
        print(f"  {city}: {len(pl)}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(by_city, f, ensure_ascii=False, indent=2)
    print(f"\n输出: {OUTPUT_PATH}")

    print("\n=== 样本 ===")
    for city in ["杭州市", "黄冈市", "镇江市", "南京市", "开封市", "西安市"]:
        if city in by_city and by_city[city]:
            e = by_city[city][0]
            print(f"  {city}: {e['title']}({e['author']}) | {e['evidence']}")
    print("  null 样本:")
    for e in null_list[:5]:
        print(f"    {e['title']}({e['author']})")


if __name__ == "__main__":
    main()
