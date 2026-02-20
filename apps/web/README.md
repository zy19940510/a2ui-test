# web

`web` 是 Monorepo 中的 Next.js 前端应用，负责展示聊天 UI、工具事件和 A2UI 动态组件。

## 技术栈

- Next.js 16.1.6
- React 19
- Tailwind CSS 4
- A2UI React Renderer（workspace 包）

## 依赖安装

在仓库根目录执行：

```bash
bun install
```

## 启动开发环境

推荐在仓库根目录执行：

```bash
bun run dev:web
```

说明：

- `dev/build` 前会自动执行 `build:deps`。
- `build:deps` 会在根目录执行 `bun run build:a2ui-web`，确保 `packages/a2ui-web/*` 产物可用。

## 常用命令

```bash
# 根目录快捷命令
bun run lint:web
bun run build:web

# 或在 apps/web 下执行
bun run lint
bun run build
bun run start
```

## 环境变量

可选：

- `NEXT_PUBLIC_API_URL`（默认 `http://localhost:8000`）

## 页面

- `/`：聊天主页面
- `/weather`：天气组件演示页
