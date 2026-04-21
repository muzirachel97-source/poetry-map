# 诗词地图

唐诗可视化地图网站，点击地级市查看该地相关的唐诗。

## 技术栈

- 纯静态网站（HTML + JS），无构建工具
- Leaflet.js 地图 + DataV GeoJSON 边界数据
- 配色风格：青绿山水（千里江山图色调）

## 文件结构

| 文件 | 说明 |
|------|------|
| `index.html` | 主页面，地图 + 诗词面板 |
| `poems_data.js` | 前端诗词数据（74 城市，545 首） |
| `poems_from_pdf.json` | PDF 提取的完整数据（含 evidence 字段和 null 条目） |
| `cnkgraph_poems.json` | cnkgraph.com 原始爬取数据（辅助参考） |
| `extract_poems_from_pdf.py` | 从《唐诗鉴赏辞典》PDF 提取诗词的脚本 |
| `extract_cnkgraph.py` | 从 cnkgraph.com 爬取诗词数据的脚本 |
| `deploy/` | 部署用文件夹，只含 index.html 和 poems_data.js |

## 数据流

```
唐诗鉴赏辞典.pdf → extract_poems_from_pdf.py → poems_from_pdf.json → poems_data.js → index.html
cnkgraph.com API → extract_cnkgraph.py → cnkgraph_poems.json（仅作补充参考）
```

## 地点判定规则

每首诗的地点必须有明确依据（evidence 字段），优先级：
1. 诗题/诗文中明确提及地名
2. 鉴赏文中注明"作于某地"
3. cnkgraph 编年数据参考
4. 以上都不确定 → null（不展示在地图上）

## 修改数据后的重建步骤

```bash
python3 extract_poems_from_pdf.py   # 重新提取 → poems_from_pdf.json
# 然后用脚本生成 poems_data.js（见 extract 脚本末尾的转换逻辑）
```
