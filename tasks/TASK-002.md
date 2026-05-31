# TASK-002：前端项目初始化

## 基本信息
- **Sprint**：Sprint 1
- **预估工时**：4 小时
- **依赖**：无
- **前置条件**：Node.js 18+ 已安装

## 任务描述
使用 Next.js 14 App Router 初始化前端项目，配置 TypeScript 和 Tailwind CSS。

## 文件清单（≤ 5 个文件）
| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `frontend/package.json` | 创建 | 项目依赖和脚本 |
| 2 | `frontend/tsconfig.json` | 创建 | TypeScript 配置 |
| 3 | `frontend/tailwind.config.ts` | 创建 | Tailwind 配置 |
| 4 | `frontend/src/app/layout.tsx` | 创建 | 根布局 |
| 5 | `frontend/src/app/page.tsx` | 创建 | 首页（临时占位） |

## 详细要求

### frontend/package.json
依赖：
- next (14+)
- react, react-dom
- typescript
- tailwindcss, postcss, autoprefixer
- zustand（状态管理）
- react-hook-form, @hookform/resolvers, zod（表单验证）
- lucide-react（图标）
- recharts（图表，后续任务用）

开发依赖：
- @types/react, @types/node
- eslint, eslint-config-next

脚本：
- `dev`：`next dev`
- `build`：`next build`
- `start`：`next start`
- `lint`：`next lint`
- `type-check`：`tsc --noEmit`

### frontend/tailwind.config.ts
- content 路径配置为 `src/**/*.{ts,tsx}`
- 延伸主题（可自定义主色调）

### frontend/src/app/layout.tsx
- 中文 lang 属性
- 引入全局样式
- 基础 HTML 结构

### frontend/src/app/page.tsx
- 临时首页，显示 "智能考试系统" 标题
- 包含导航到 `/auth` 的链接

## 验收标准
1. 运行 `npm install` 无报错
2. 运行 `npm run dev` 成功启动开发服务器（默认 3000 端口）
3. 浏览器访问 `http://localhost:3000` 显示首页
4. 运行 `npm run type-check` 无类型错误
5. 运行 `npm run lint` 无错误

## 测试方法
```bash
cd frontend
npm install
npm run dev
# 浏览器访问 http://localhost:3000
# 预期：显示 "智能考试系统" 标题
```
