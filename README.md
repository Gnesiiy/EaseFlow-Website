# EaseFlow 官方网站

暖白与雾蓝灰的轻量静态网站，包含 Home、Privacy Policy、Terms of Use、Help & Support 的简体中文和英文版本。

## 本地预览

在终端运行（Python 3.9 或更高版本，无需安装依赖）：

```sh
cd EaseFlow-Website
python3 scripts/build.py
python3 scripts/validate_site.py --base-path /EaseFlow-Website/
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

打开 http://127.0.0.1:4173/ 。按 Ctrl+C 停止服务器。页面已生成，未改文案或样式时可以省略构建命令。

| 页面 | 简体中文 | English |
| --- | --- | --- |
| 首页 | `/` | `/en/` |
| 隐私政策 | `/privacy/` | `/en/privacy/` |
| 使用条款 | `/terms/` | `/en/terms/` |
| 帮助与支持 | `/support/` | `/en/support/` |

## 文案与代码

- `EaseFlow_Website_Copy_zh_en.md`：唯一正文来源；开发者署名及生效日期已确认，本轮接入图标未修改任何正文。
- `scripts/build.py`：清理旧构建产物后，从底稿生成八个静态 HTML 页面。
- `scripts/validate_site.py`：发布检查，核对正文、语言链接、图标、邮箱、锚点及项目子路径。
- `.github/workflows/pages.yml`：在 `main` 分支收到 Push 后构建、检查并发布，也支持手动触发。
- `assets/`：本地 CSS、SVG 插画、网站图标与少量增强脚本。
- `dist/`：完整网站输出，只需静态文件服务器；不提交，由 Actions 重新生成。
- `screenshots/`：仅本地保留的历史截图与检查记录，不提交、不部署。

修改正式正文时，修改底稿后重新运行构建脚本。不要直接修改 `dist/`，再次构建会覆盖生成文件。Markdown 解析器仅支持当前底稿使用的标题、段落、粗体和列表格式。

每个地址均对应实际 `index.html` 文件；页面、资源和导航使用相对路径，不依赖 SPA 回退。语言编码在 URL 中，站内导航保留语言，切换语言保留当前页面和章节锚点。无 cookie、localStorage、远程字体、外部脚本、后台、追踪或第三方分析服务；JavaScript 仅用于切换语言时保留章节锚点，正文、导航、语言切换和 FAQ 本身使用原生 HTML。

## GitHub Pages 兼容性

目标仓库：`Gnesiiy/EaseFlow-Website`。预计地址：https://gnesiiy.github.io/EaseFlow-Website/ 。

工作流使用 Ubuntu 与 Python 3.12，无需 npm 或 pip 安装。构建执行 `python scripts/build.py`，检查执行 `python scripts/validate_site.py --base-path /EaseFlow-Website/`；通过后仅上传 `dist/`（包括 `.nojekyll`），发布到 `github-pages` 环境。只有 `main` 分支能够部署，部署任务依赖构建成功，使用 GitHub 自动提供的 `GITHUB_TOKEN`，无需额外部署密钥。

资源和页面链接均为相对路径，兼容域名根路径与 `/EaseFlow-Website/` 项目子路径。四页中文地址为项目根目录、`privacy/`、`terms/`、`support/`；英文位于对应的 `en/` 路径。无需 SPA 回退、`gh-pages` 分支或复制文件到 `docs/`。

首次发布由仓库所有者执行：

1. 在本地运行 `git push -u origin main`。本次准备工作仅完成本地提交，没有执行 Push。
2. 打开仓库 **Settings → Pages → Build and deployment → Source**，选择 **GitHub Actions**。
3. 在 **Actions → Deploy EaseFlow to GitHub Pages** 查看运行结果。如果第一次运行发生在 Pages 启用之前而失败，启用后选择 **Run workflow → main** 或重新运行失败的任务。
4. 等待 `build` 和 `deploy` 都成功，再打开工作流显示的网站地址，检查四页与语言切换。后续向 `main` Push 会自动更新网站。

如果仓库的 Actions 被禁用，先启用；若 `github-pages` 环境配置了人工审批，按 GitHub 的提示批准该次部署。实际线上部署结果须在 Push 后确认。

配置依据：[GitHub Pages 自定义工作流官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

子路径复查方式：在工作区运行 `python3 -m http.server 4174 --bind 127.0.0.1`，打开 http://127.0.0.1:4174/dist/ 。`/dist/` 在此模拟项目名前缀；实际 GitHub Pages 项目前缀不必叫 `dist`。

## 本轮验收

- 实际浏览器检查四页 × 两种语言；逐行归一化空白后比对源文案，未发现正文遗漏。
- 检查 320、390、768、1440 像素视口，所有页面无横向溢出。
- 实际点击三个首页入口、语言切换、返回首页、英文导航、章节目录、返回顶部。
- 切换语言后页面与章节保持；在项目子路径下验证上述流程。
- FAQ 鼠标展开、键盘 Enter 收起通过。
- 正式图标接入后校验 238 个本地资源／链接／锚点目标，均有效；八页均只有一个 H1。
- 邮箱链接均为 `mailto:easeflowsupport@163.com`。未发测试邮件，邮件客户端是否配置及邮箱实际收件能力需另行确认。
- 截图使用浏览器渲染；视口模拟不等同于实机 iOS Safari 或 Android 浏览器测试。尚未进行实机测试。

## 发布前待确认

1. 已确认：隐私政策及使用条款生效日期为 `2026 年 10 月` / `October 2026`。
2. 已确认：开发者署名为 `Pan XinYue`，客服邮箱为 `easeflowsupport@163.com`。
3. 已指定 GitHub Pages 独立项目仓库 `Gnesiiy/EaseFlow-Website`；未配置自定义域名，底稿中的已审核措辞保持原样。
4. 客服邮箱的实际收件能力、邮件保留／删除规则与处理流程；确认实际操作与底稿一致。
5. 已完成正式 App Icon 接入：源文件为 `assets/AppIcon-1024.png`。导航栏、页脚、首页小标识均使用其等比缩小版本；旧品牌 SVG 与旧 Favicon 已移除。原图文件及配色未修改。

最新图标验收截图与浏览器检查记录在 `screenshots/official-icon/`；旧截图保留作为历史设计记录，不代表当前发布内容。

## 正式品牌图标与 Favicon

普通构建仍为 `python3 scripts/build.py`，无需额外依赖。图标衍生资源已生成并存放在 `assets/`，构建时一起复制到 `dist/assets/`。

- `brand-icon-96.png`：全站品牌图标，桌面导航显示 37px，手机导航显示 32px，沿用原有占位尺寸。
- `favicon-16x16.png`、`favicon-32x32.png`、`favicon-48x48.png`：浏览器图标尺寸。
- `favicon.ico`：包含 16、32、48px 三个图像。
- `apple-touch-icon.png`：180px Apple Touch Icon。

如需从正式原图重新生成，在 macOS 运行 `python3 scripts/generate_icons.py`，然后运行构建命令。该脚本使用系统 `sips` 等比缩小，不重绘、不裁切、不改色；ICO 直接封装生成的 PNG。其他系统可使用已经生成的资源进行普通构建。

本轮实际检查四页双语在 320、390、1440px 视口下的图标加载与布局，并在 390、1440px 下逐页操作语言切换和返回首页；使用 `/dist/` 模拟 GitHub Pages 项目前缀。所有页面无破图、无横向溢出，图标与 Favicon 均使用相对路径。原图与正式底稿哈希、全部页面文字在变更前后完全一致。尚未进行手机实机或线上 GitHub Pages 验证。
