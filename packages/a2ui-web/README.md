# a2ui-component

a2ui-web 组件库 Monorepo

## 📦 包列表

- **[@a2ui-web/assets](./assets)** - 静态资源包（图标、图片等）
- **[@a2ui-web/animations](./animations)** - 动画和图标库（Lenis、Framer Motion、Lucide React）
- **[@a2ui-web/shadcn-ui](./shadcn-ui)** - shadcn/ui 组件库（55+ 组件）
- **[@a2ui-web/a2ui-react-renderer](./a2ui-react-renderer)** - A2UI 0.8 React 渲染器（事件驱动，无轮询）
- **[@a2ui-web/config-typescript](./config-typescript)** - TypeScript 共享配置
- **[@a2ui-web/config-tailwind](./config-tailwind)** - Tailwind CSS 共享配置
- **[@a2ui-web/config-postcss](./config-postcss)** - PostCSS 共享配置
- **[@a2ui-web/utils](./utils)** - 通用工具函数库

## 📋 环境要求

### 安装 Make

**macOS:**
```bash
# 检查是否已安装
make --version

# 如果未安装，安装 Xcode Command Line Tools
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install build-essential
```

**Linux (CentOS/RHEL):**
```bash
sudo yum groupinstall "Development Tools"
```

**Windows:**
```bash
# 使用 Chocolatey
choco install make

# 或使用 WSL (推荐)
wsl --install
```

## 🚀 发布流程

### 0. 构建包（如果需要）

某些包（如 animations）需要先构建才能发布：

```bash
# 进入包目录
cd animations

# 构建（生成 dist/ 目录）
bun run build

# 或在开发时监听文件变化
bun run dev
```

**需要构建的包：**
- `animations` - React 组件，需要生成 .js 和 .d.ts 文件
- 其他纯配置或静态资源包无需构建

### 1. 升级版本号

**使用 Make 命令自动升级（推荐）：**

```bash
# 修复 bug - 升级 patch 版本 (0.1.0 → 0.1.1)
make patch-assets

# 新增功能 - 升级 minor 版本 (0.1.1 → 0.2.0)
make minor-animations

# 重大更新 - 升级 major 版本 (0.2.0 → 1.0.0)
make major-config-typescript
```

**执行效果：**

```bash
$ make patch-assets
📦 包名: assets
📊 当前版本: 0.1.0
🆙 新版本: 0.1.1 (patch)

确认升级版本号？(y/N) y
✅ 版本已升级: 0.1.0 → 0.1.1

下一步:
  1. 检查更改: git diff assets/package.json
  2. 提交更改: git add assets/package.json && git commit -m 'chore(assets): bump version to 0.1.1'
  3. 发布包: make publish-assets
```

**手动升级版本号（可选）：**

版本号遵循 [语义化版本规范](https://semver.org/lang/zh-CN/)：

- **主版本号（Major）**：不兼容的 API 修改
- **次版本号（Minor）**：向下兼容的功能性新增
- **修订号（Patch）**：向下兼容的问题修正

```bash
# 手动编辑 package.json
vim assets/package.json  # 修改 "version": "0.1.1"

# 或使用 sed（macOS）
sed -i '' 's/"version": "0.1.0"/"version": "0.1.1"/' assets/package.json

# 或使用 sed（Linux）
sed -i 's/"version": "0.1.0"/"version": "0.1.1"/' assets/package.json
```

### 2. 发布包

```bash
# 发布指定包到 GitLab Package Registry
make publish-assets
make publish-animations
make publish-config-typescript
```

### 3. Tag 命名规范

```
<package-name>@<version>
```

示例：
- `assets@0.1.0` - 发布 assets 包 v0.1.0
- `animations@0.1.0` - 发布 animations 包 v0.1.0
- `config-typescript@0.1.0` - 发布 config-typescript 包 v0.1.0

### 4. 完整发布示例

```bash
# 场景：修复了 assets 包中的一个图标错误

# Step 1: 修改代码
# （编辑相关文件...）

# Step 2: 升级版本号（使用 make 命令）
make patch-assets
# 输出: ✅ 版本已升级: 0.1.0 → 0.1.1

# Step 3: 提交代码
git add assets/
git commit -m "fix(assets): correct icon path"
git push

# Step 4: 发布包（会自动创建 tag 并触发 CI）
make publish-assets
# 输出示例：
# 🚀 准备发布 assets 包...
# 📋 包名: assets
# 🏷️  版本: 0.1.1
# 🔖 Tag: assets@0.1.1
#
# 确认发布？(y/N) y
# 📌 创建 tag: assets@0.1.1
# ⬆️  推送 tag 到远程仓库...
# ✅ 发布已触发，请查看 GitLab CI

# Step 5: 等待 CI 完成，查看发布结果
# https://gitlab.longbridge-inc.com/long-bridge-frontend/a2ui-component/-/pipelines
```

### 5. 手动发布流程（可选）

```bash
# 1. 更新包版本号（编辑 package.json）
cd assets
# 修改 version 字段

# 2. 创建并推送 tag
git tag -a "assets@0.1.0" -m "chore: release assets@0.1.0"
git push origin "assets@0.1.0"

# 3. CI 会自动触发发布
```

## 📖 查看已发布的包

https://gitlab.longbridge-inc.com/long-bridge-frontend/a2ui-component/-/packages

## 开发

### shadcn/ui 组件管理

shadcn-ui 包可以从官方同步/更新组件：

```bash
# 使用 Make 命令（推荐）
make shadcn-add

# 或使用 bun 命令
bun run shadcn:add

# 或直接使用 bunx
bunx --bun shadcn@latest add --cwd shadcn-ui
```

执行后会进入交互式选择界面，可以添加或更新任何 shadcn/ui 组件。

### 安装依赖

```bash
# 安装依赖
bun install

# 查看包信息
make list-packages

# 查看所有 make 命令
make help
```

### 从 GitLab Package Registry 安装包

项目中的包发布在 GitLab Package Registry，需要配置认证。

**本地开发：**

1. 创建 GitLab 个人访问令牌：
   - 访问 https://gitlab.longbridge-inc.com/-/profile/personal_access_tokens
   - 创建令牌，权限选择 `read_api` 和 `read_registry`

2. 设置环境变量：
   ```bash
   # 添加到 ~/.bashrc 或 ~/.zshrc
   export GITLAB_TOKEN="your-personal-access-token"
   ```

3. 安装依赖：
   ```bash
   bun install
   ```

**CI/CD 环境：**

CI/CD 会自动使用 `CI_JOB_TOKEN` 进行认证，无需额外配置。

**安装单个包（在其他项目中）：**

```bash
# 方法 1: 使用 bun（推荐）
bun add @a2ui-web/config-typescript --registry https://gitlab.longbridge-inc.com/api/v4/projects/4872/packages/npm/

# 方法 2: 在项目中配置 .npmrc
echo "@a2ui-web:registry=https://gitlab.longbridge-inc.com/api/v4/projects/4872/packages/npm/" >> .npmrc
bun install @a2ui-web/config-typescript
```
