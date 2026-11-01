# EaseFlow 官方网站

官网是无依赖的静态网站。四类页面（首页、隐私政策、使用条款、帮助与支持）各有九种完整语言，共 36 个 `index.html` 页面。保留简中根路径和原有 `/en/` 路径；`/en/` 对应 en-US，en-GB 独立位于 `/en-GB/`。

| 语言 | 前缀 |
| --- | --- |
| zh-Hans | `/` |
| zh-Hant | `/zh-Hant/` |
| en-US | `/en/` |
| en-GB | `/en-GB/` |
| ja | `/ja/` |
| ko | `/ko/` |
| es | `/es/` |
| fr | `/fr/` |
| de | `/de/` |

每个前缀下还有 `privacy/`、`terms/`、`support/`。站内链接使用相对地址，支持 GitHub Pages 的 `/EaseFlow-Website/` 项目前缀；页面提供对应的 `lang`、标题、描述、canonical 和九语言 `hreflang`，以及 `x-default`。原生 `<details>` 语言菜单可用键盘操作，切换时保留当前页面及章节锚点；FAQ 也使用原生 `<details>`。

## 文案维护

- `copy/<locale>.md`：每种语言独立的四页正文。段落以 `<!-- home -->`、`<!-- privacy -->`、`<!-- terms -->`、`<!-- support -->` 分隔。此目录是四页正文的唯一正式来源；法律、隐私、安全、备份和删除陈述须保留已确认的原意，并与 iOS 术语核对。
- `copy/release.json`：唯一的版本发布状态。当前 v1.0 已上架，v1.1 尚未正式发布。正式发布时须核实产品状态，再更新此文件并重新构建、校验。
- `copy/release_notes.json`：隐私、条款和帮助页的九语言版本提示模板，由构建脚本按统一状态填入。
- 原有双语底稿已与 `copy/zh-Hans.md`、`copy/en-US.md` 核对；历史版本可从 Git 记录查阅，不需维护第二套正文。

翻译需人工审校，尤其是各语言的法律用语、iOS 具体控件名称、en-US 与 en-GB 的地区写法。不得据此自行增加数据处理、医疗或服务承诺。

## 构建与校验

使用 Python 3.9 或更新版本，不需要安装依赖：

```sh
python3 scripts/build.py
python3 scripts/validate_site.py --base-path /EaseFlow-Website/
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

在本地打开 `http://127.0.0.1:4173/`。`dist/` 是可重建的输出，不应手工编辑或提交。现有 `.github/workflows/pages.yml` 在 `main` Push 后运行构建与校验，再发布 `dist/`；提交后仍需单独 Push 才会触发发布。

`scripts/validate_site.py` 检查 36 页、九语言正文、FAQ 数量、版本提示、邮箱、图标、全部链接与锚点、语言菜单、canonical 和 hreflang。可用 `--base-path /dist/` 在本地模拟项目子路径。浏览器截图及视口检查记录放在忽略提交的 `screenshots/l10n-2026-11-01/`。
